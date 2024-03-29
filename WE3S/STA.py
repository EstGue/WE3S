from WE3S.contender import *
from WE3S.frame_generator import *
from WE3S.stream_handler import *

class STA (Contender):

    def __init__(self, ID):
        Contender.__init__(self, ID)

        self.UL_data_stream = Data_stream(self.ID, 0)
        self.DL_prompt_stream = None
        self.DL_prompt_answer = []

        self.DL_slot = None
        self.wait_for_DL_prompt_answer = None
        self.UL_slot = None
        self.received_UL_prompt = None

        self.buffer_capacity = STA_BUFFER_CAPACITY

        self.wlan.add_STA()

### INITIALIZATION and related functions

    def add_UL_traffic(self, traffic_type, arg_dict, label, start, end):
        self.UL_data_stream.add_traffic(label, traffic_type, arg_dict, start, end)

    def use_DL_slot(self):
        return self.DL_slot is not None

    def use_DL_prompt(self):
        return self.DL_prompt_stream is not None

    def use_UL_slot(self):
        return self.UL_slot is not None

    def use_UL_prompt(self):
        return self.received_UL_prompt is not None

    def toggle_DL_slot(self, DL_slot):
        assert(not self.use_DL_prompt())
        self.DL_slot = DL_slot
        self.state_counter.toggle_DL_slot(DL_slot)

    def toggle_DL_prompt(self, strategy_name, arg_dict):
        assert(not self.use_DL_slot())
        assert(not self.use_UL_prompt())
        self.DL_prompt_stream = Prompt_stream(self.ID, 0, "DL prompt")
        self.DL_prompt_stream.set_strategy(strategy_name, arg_dict)
        self.wait_for_DL_prompt_answer = False
        if self.use_UL_slot():
            self.DL_prompt_stream.toggle_slot(self.UL_slot)

    def toggle_UL_slot(self, UL_slot):
        assert(not self.use_UL_prompt())
        self.UL_slot = UL_slot
        self.UL_data_stream.toggle_slot(UL_slot)
        if self.use_DL_prompt():
            self.DL_prompt_stream.toggle_slot(UL_slot)

    def toggle_UL_prompt(self):
        assert(not self.use_UL_slot())
        assert(not self.use_DL_prompt())
        self.received_UL_prompt = False
        self.UL_data_stream.toggle_prompt()

    def initialize(self):
        self.verify_initialization()
        self.UL_data_stream.initialize()
        if self.use_DL_prompt():
            self.DL_prompt_stream.initialize()
        if DEBUG and self.use_DL_slot():
            self.timeline.append(self.DL_slot.get_timeline())
        if DEBUG and self.use_UL_slot():
            self.timeline.append(self.UL_slot.get_timeline())
            

    def verify_initialization(self):
        if self.use_DL_slot():
            assert(not self.use_DL_prompt())
        if self.use_DL_prompt():
            assert(not self.use_DL_slot())
            assert(not self.use_UL_prompt())
            assert(self.DL_prompt_stream is not None)
        if self.use_UL_slot():
            assert(not self.use_UL_prompt())
            assert(self.UL_slot == self.UL_data_stream.slot)
            if self.use_DL_prompt():
                assert(self.UL_slot == self.DL_prompt_stream.slot)
        if self.use_UL_prompt():
            assert(not self.use_UL_slot())
            assert(not self.use_DL_prompt())
            assert(self.UL_data_stream.use_prompt())

### GET_NEXT_EVENT() and related functions

    def get_next_event(self, current_time):
        assert(self.current_time == current_time)
        stream = self.select_stream()
        if stream is None:
            return None
        return self.create_event(stream)

    def select_stream(self):
        if not self.use_DL_prompt() and not self.use_UL_prompt():
            return self.UL_data_stream
        if self.use_UL_prompt():
            if self.received_UL_prompt:
                return self.UL_data_stream
            else:
                return None
        if self.use_DL_prompt():
            # If one stream cannot transmit, then the other is selected
            if self.DL_prompt_stream.get_transmission_time(self.backoff) is None \
               and self.UL_data_stream.get_transmission_time(self.backoff) is None:
                return None
            elif self.DL_prompt_stream.get_transmission_time(self.backoff) is None:
                return self.UL_data_stream
            elif self.UL_data_stream.get_transmission_time(self.backoff) is None:
                return DL_prompt_stream
            # Chooses the oldest stream between UL_data_stream and DL_prompt_stream
            DL_prompt_creation_time = self.DL_prompt_stream.get_oldest_creation_time()
            UL_data_creation_time = self.UL_data_stream.get_oldest_creation_time()
            if DL_prompt_creation_time < UL_data_creation_time:
                return self.DL_prompt_stream
            else:
                return self.UL_data_stream

    def create_event(self, stream):
        event_start = self.create_event_start(stream)
        if event_start is None:
            return None
        event_duration = self.create_event_duration(stream)
        event_frames = stream.get_frames()[:MAX_AGGREGATED_FRAMES]
        event = Event(event_start, event_duration, event_frames.copy())
        return event


    def create_event_start(self, stream):
        if self.use_UL_prompt():
            if self.received_UL_prompt:
                return self.current_time + SIFS
            return None
        else:
            event_start = stream.get_transmission_time(self.backoff)
            return max(event_start, float(self.current_time + DIFS + self.backoff * BACKOFF_SLOT))

    def create_event_duration(self, stream):
        data_rate = self.wlan.get_link_capacity(self.ID)
        frame_table = stream.get_frames()[:MAX_AGGREGATED_FRAMES]
        is_ACK = len(frame_table) == 1 and frame_table[0].label == "ACK"
        total_size = sum([frame.size for frame in frame_table])
        total_size += MAC_HEADER_SIZE
        event_duration = PHY_HEADER_DURATION
        event_duration += Timestamp(total_size / data_rate)
        if not is_ACK:
            event_duration += ACK_DURATION
        return event_duration
        

### UPDATE_INFORMATION() and related functions

    def update_information(self, event):
        if DEBUG:
            self.update_timeline(event)
        self.update_backoff(event)
        self.current_time = event.end
        self.verify_strategy_use(event)
        self.react_to_DL_prompt_answer(event)
        self.remove_sent_frames(event)
        self.update_scheduled_to_pending()
        self.react_to_UL_prompts(event)
        self.update_doze(event)
        self.verify_inner_state()

    def update_backoff(self, event):
        self.decrease_backoff(event)
        if event.is_sender(self.ID):
            if event.is_collision() or event.is_error():
                self.new_backoff_after_collision()
            else:
                self.new_backoff_after_success()

    def update_doze(self, event):
        self.state_counter.add_event(event)
        if self.use_DL_prompt():
            if self.wait_for_DL_prompt_answer:
                return
            transmission_time = self.UL_data_stream.get_transmission_time(self.backoff)
            DL_prompt_transmission_time = self.DL_prompt_stream.get_transmission_time(self.backoff)
            transmission_time = min(transmission_time, DL_prompt_transmission_time)
            if transmission_time ==-1:
                return
            if Timestamp(transmission_time) - self.current_time > MIN_DOZE_DURATION:
                self.state_counter.switch_to_doze_state(Timestamp(transmission_time))

        transmission_time = self.UL_data_stream.get_transmission_time(self.backoff)
        if self.use_DL_prompt():
            DL_prompt_transmission_time = self.DL_prompt_stream.get_transmission_time(self.backoff)
            transmission_time = min(transmission_time, DL_prompt_transmission_time)
        self.state_counter.update_next_scheduled_transmission(transmission_time)
        
        


    def verify_strategy_use(self, event):
        if event.is_sender(self.ID):
            if self.use_UL_slot():
                if not self.UL_slot.is_in_SP(event.start):
                    print(f"{Fore.RED}The STA", self.ID, " has sent a frame outside its UL slots.")
                    print("Event start:", event.start)
                    print("Current_ SP:", self.UL_slot.get_current_SP_start(event.start), end="")
                    print(" - ", self.UL_slot.get_current_SP_end(event.start))
                    print("Next SP:", self.UL_slot.get_next_SP_start(event.start))
                    print(f"{Style.RESET_ALL}")
                    assert(0)
            if self.use_UL_prompt():
                assert(self.received_UL_prompt)
        if event.is_receiver(self.ID):
            if self.use_DL_slot():
                if not self.DL_slot.is_in_SP(event.start):
                    print(f"{Fore.RED}The STA", self.ID, " has sent a frame outside its DL slots.")
                    print("Event start:", event.start)
                    print("Current_ SP:", self.DL_slot.get_current_SP_start(event.start), end="")
                    print(" - ", self.DL_slot.get_current_SP_end(event.start))
                    print("Next SP:", self.DL_slot.get_next_SP_start(event.start))
                    print(f"{Style.RESET_ALL}")
                    assert(0)
            elif self.use_DL_prompt():
                assert(self.wait_for_DL_prompt_answer)


    def remove_sent_frames(self, event):
        if event.is_collision():
            return
        if event.is_sender(self.ID):
            for frame in event.frame_table.copy():
                if not frame.is_in_error:
                    assert(frame.sender_ID == self.ID)
                    if frame.label == "DL prompt":
                        assert(self.use_DL_prompt())
                        self.wait_for_DL_prompt_answer = True
                        self.DL_prompt_stream.remove_frame(frame.ID)
                    elif frame.label == "ACK":
                        assert(self.use_UL_prompt())
                        self.received_UL_prompt = False
                    else:
                        self.UL_data_stream.remove_frame(frame.ID)
                        if self.use_UL_prompt() and not self.UL_data_stream.is_pending():
                            self.received_UL_prompt = False
                        # print(f"{Fore.RED}The STA is not supposed to send a frame different from UL Tx, DL prompt or ACK")
                        # print("Frame:", frame.get_dictionary())
                        # print(f"{Style.RESET_ALL}")
                        # assert(0)

    def react_to_DL_prompt_answer(self, event):
        if self.wait_for_DL_prompt_answer:
            if not event.is_receiver(self.ID):
                print(f"{Fore.RED}The STA", self.ID, "is waiting for an answer to its DL prompt")
                print("Event:", event.get_dictionary())
                print(f"{Style.RESET_ALL}")
                assert(0)
            assert(event.is_receiver(self.ID))
            self.DL_prompt_answer += event.frame_table
            if event.is_EOSP():
                self.wait_for_DL_prompt_answer = False
                self.DL_prompt_stream.set_prompt_answer(self.DL_prompt_answer.copy())
                self.DL_prompt_answer = []
            elif len(event.frame_table) == 1 and event.frame_table[0].label == "ACK":
                self.wait_for_DL_prompt_answer = False
                self.DL_prompt_answer = []
                self.DL_prompt_stream.set_prompt_answer(self.DL_prompt_answer.copy())
                        
    def update_scheduled_to_pending(self):
        self.UL_data_stream.update_time(self.current_time)
        while not self.UL_data_stream.is_up_to_date():
            if self.get_number_of_pending_frames() < self.buffer_capacity:
                self.UL_data_stream.buffer_scheduled_frame()
            else:
                self.UL_data_stream.drop_scheduled_frame()
        if self.use_DL_prompt():
            self.DL_prompt_stream.update_time(self.current_time)
            while not self.DL_prompt_stream.is_up_to_date():
                self.DL_prompt_stream.buffer_scheduled_frame()

    def get_number_of_pending_frames(self):
        return self.UL_data_stream.get_number_of_pending_frames()

    def react_to_UL_prompts(self, event):
        if not self.use_UL_prompt():
            return
        if not event.is_collision():
            if len(event.frame_table) == 1 and event.frame_table[0].label == "UL prompt" and not event.is_error():
                if event.is_receiver(self.ID):
                    self.received_UL_prompt = True



### DEBUG

    def verify_inner_state(self):
        assert(self.UL_data_stream.current_time == self.current_time)
        if self.use_DL_prompt():
            assert(self.DL_prompt_stream.current_time == self.current_time)
        assert(self.state_counter.current_time == self.current_time)


    def update_timeline(self, event):
        if DEBUG:
            self.timeline[0].add_until(event.start, '-')
            if event.is_beacon():
                self.timeline[0].add_until(event.end, 'b')
            if event.is_sender(self.ID):
                if event.is_DL_prompt():
                    self.timeline[0].add_until(event.end, 'p')
                else:
                    self.timeline[0].add_until(event.end, '^')
            elif event.is_receiver(self.ID):
                if event.is_collision():
                    self.timeline[0].add_until(event.end, 'x')
                elif event.is_error():
                    self.timeline[0].add_until(event.end, 'R')
                elif event.is_ACK():
                    self.timeline[0].add_until(event.end, 'K')
                else:
                    self.timeline[0].add_until(event.end, '*')
            else:
                self.timeline[0].add_until(event.end, '-')
            self.timeline[0].add_separation()
            if self.use_UL_slot():
                self.UL_slot.update_timeline(event)
            if self.use_DL_slot() and self.DL_slot != self.UL_slot:
                self.DL_slot.update_timeline(event)


    def get_dictionary(self):
        result = {
            "ID": self.ID,
            "UL traffic": self.UL_data_stream.get_dictionary(),
            "Datarate": self.wlan.get_link_capacity(self.ID),
            "use DL slot": self.use_DL_slot(),
            "use DL prompt": self.use_DL_prompt(),
            "use UL slot": self.use_UL_slot(),
            "use UL prompt": self.use_UL_prompt()
        }
        if self.use_DL_slot():
            result["DL slot"] = self.DL_slot.get_dictionary()
        if self.use_DL_prompt():
            result["DL prompt"] = self.DL_prompt_stream.prompt_strategy.get_dictionary()
        if self.use_UL_slot():
            result["UL slot"] = self.UL_slot.get_dictionary()
        result["counters"] = self.state_counter.get_dictionary()
        return result
