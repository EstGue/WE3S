from WE3S.contender import *
from WE3S.stream_handler import *

class AP(Contender):

    def __init__(self, ID):
        Contender.__init__(self, ID)

        self.buffer_capacity = AP_BUFFER_CAPACITY

        self.stream_table = [Beacon_stream()]
        self.stream_information = dict()

        self.received_DL_prompt = -1
        self.sent_UL_prompt = -1
        self.UL_prompt_answer = []


### INITIALIZATION and related functions

    def add_STA(self, sta):
        datastream_index = len(self.stream_table)
        self.stream_table.append(Data_stream(0, sta.ID))
        self.stream_information[str(sta.ID)] = dict()
        self.stream_information[str(sta.ID)]["DL Tx index"] = datastream_index
        self.stream_information[str(sta.ID)]["use DL slot"] = False
        self.stream_information[str(sta.ID)]["use DL prompt"] = False
        self.stream_information[str(sta.ID)]["use UL slot"] = False
        self.stream_information[str(sta.ID)]["use UL prompt"] = False
        if sta.use_DL_slot():
            self.stream_information[str(sta.ID)]["use DL slot"] = True
            self.stream_table[datastream_index].toggle_DL_slot(sta.DL_slot)
        if sta.use_DL_prompt():
            self.stream_information[str(sta.ID)]["use DL prompt"] = True
            self.stream_table[datastream_index].toggle_DL_prompt()
        if sta.use_UL_slot():
            self.stream_information[str(sta.ID)]["use UL slot"] = True
        if sta.use_UL_prompt():
            self.stream_information[str(sta.ID)]["use UL prompt"] = True
            prompt_stream_index = len(self.stream_table)
            self.stream_table.append(Prompt_stream(sta.UL_prompt_interval, 0, sta.ID, "UL prompt"))
            self.stream_information[str(sta.ID)]["UL prompt index"] = prompt_stream_index

    def add_DL_traffic(self, STA_ID, traffic_type, arg_dict, label, start, end):
        stream_index = self.stream_information[str(STA_ID)]["DL Tx index"]
        self.stream_table[stream_index].add_traffic(label, traffic_type, arg_dict, start, end)

    def toggle_DL_slot(self, STA_ID, DL_slot):
        self.stream_information[str(STA_ID)]["use DL slot"] = True
        datastream_index = self.stream_information[str(STA_ID)]["DL Tx index"]
        self.stream_table[datastream_index].toggle_slot(DL_slot)
        if self.stream_information[str(STA_ID)]["use UL prompt"]:
            UL_prompt_stream_index = self.stream_information[str(STA_ID)]["UL prompt index"]
            self.stream_table[UL_prompt_stream_index].toggle_slot(DL_slot)

    def toggle_DL_prompt(self, STA_ID):
        self.stream_information[str(STA_ID)]["use DL prompt"] = True
        datastream_index = self.stream_information[str(STA_ID)]["DL Tx index"]
        self.stream_table[datastream_index].toggle_prompt()

    def toggle_UL_slot(self, STA_ID, UL_slot):
        self.stream_information[str(STA_ID)]["use UL slot"] = True

    def toggle_UL_prompt(self, STA_ID, strategy_name, arg_dict):
        self.stream_information[str(STA_ID)]["use UL prompt"] = True
        len_stream = len(self.stream_table)
        prompt_stream = Prompt_stream(0, STA_ID, "UL prompt")
        prompt_stream.set_strategy(strategy_name, arg_dict)
        self.stream_table.append(prompt_stream)
        self.stream_information[str(STA_ID)]["UL prompt index"] = len_stream
        if self.stream_information[str(STA_ID)]["use DL slot"]:
            datastream_index = self.stream_information[str(STA_ID)]["DL Tx index"]
            DL_slot = self.stream_table[datastream_index].slot
            self.stream_table[-1].toggle_slot(DL_slot)


    def initialize(self):
        self.verify_initialization()
        for stream in self.stream_table:
            stream.initialize()

    def verify_initialization(self):
        for sta in self.stream_information:
            datastream_index = self.stream_information[sta]["DL Tx index"]
            assert(self.stream_table[datastream_index].get_receiver_ID() == int(sta))
            use_DL_slot = self.stream_information[sta]["use DL slot"]
            use_DL_prompt = self.stream_information[sta]["use DL prompt"]
            use_UL_slot = self.stream_information[sta]["use UL slot"]
            use_UL_prompt = self.stream_information[sta]["use UL prompt"]
            if use_DL_slot:
                assert(not use_DL_prompt)
                assert(self.stream_table[datastream_index].use_slot())
            if use_DL_prompt:
                assert(not use_DL_slot)
                assert(not use_UL_prompt)
                assert(self.stream_table[datastream_index].use_prompt())
            if use_UL_slot:
                assert(not use_UL_prompt)
            if use_UL_prompt:
                assert(not use_UL_slot)
                assert(not use_DL_prompt)
                assert("UL prompt index" in self.stream_information[sta])

### GET NEXT EVENT and related functions

    def get_next_event(self, current_time):
        assert(self.current_time == current_time)
        stream_index = self.select_stream()
        if stream_index is None:
            return None
        return self.create_event(self.stream_table[stream_index])

    def select_stream(self):
        if self.received_DL_prompt != -1: # Received a prompt, needs to immediatly answer it.
            return int(self.stream_information[str(self.received_DL_prompt)]["DL Tx index"])
        if self.stream_table[0].is_pending() and self.sent_UL_prompt == -1: # Beacons
            return 0
        transmission_time_table = [stream.get_transmission_time(self.backoff) for stream in self.stream_table]
        if self.no_scheduled_transmission():
            return None
        if self.no_pending_stream():
            # We select the stream with the lowest transmission time
            min_transmission_value = None
            min_transmission_index = None
            for transmission_index, transmission_value in enumerate(transmission_time_table):
                if transmission_value is not None:
                    if min_transmission_value is None:
                        min_transmission_value = transmission_value
                        min_transmission_index = transmission_index
                    elif transmission_value < min_transmission_value :
                        min_transmission_value = transmission_value
                        min_transmission_index = transmission_index
            assert(min_transmission_value != -1)
            return min_transmission_index
        elif self.one_pending_stream():
            return transmission_time_table.index(-1)
        elif self.multiple_pending_streams():
            # We take the oldest frame among the pending stream
            min_creation_time_value = None
            min_creation_time_index = None
            for i,stream in enumerate(self.stream_table):
                if stream.get_transmission_time(self.backoff) == -1:
                    if min_creation_time_value is None:
                        min_creation_time_value = stream.get_pending_frame_creation_time()
                        min_creation_time_index = i
                    elif stream.get_pending_frame_creation_time() < min_creation_time_value:
                        min_creation_time_value = stream.get_pending_frame_creation_time()
                        min_creation_time_index = i
            return min_creation_time_index
        else:
            print(f"{Fore.RED}There are either zero, one or multiple pending streams{Style.RESET_ALL}")
            assert(0)

    def no_scheduled_transmission(self):
        for stream in self.stream_table:
            transmission_time = stream.get_transmission_time(self.backoff)
            if transmission_time is not None:
                return False
        return True

    def no_pending_stream(self):
        for stream in self.stream_table:
            transmission_time = stream.get_transmission_time(self.backoff)
            if transmission_time is not None and transmission_time < 0:
                return False
        return True
    
    def one_pending_stream(self):
        nb_pending_stream = 0
        for stream in self.stream_table:
            transmission_time = stream.get_transmission_time(self.backoff)
            if transmission_time is not None and transmission_time == -1:
                nb_pending_stream += 1
        if nb_pending_stream == 1:
            return True
        else:
            return False

    def multiple_pending_streams(self):
        nb_pending_stream = 0
        for stream in self.stream_table:
            transmission_time = stream.get_transmission_time(self.backoff)
            if transmission_time is not None and transmission_time == -1:
                nb_pending_stream += 1
        if nb_pending_stream > 1:
            return True
        else:
            return False
            
    def create_event(self, stream):
        if stream is None:
            return None # Nothing to send
        event_duration = self.create_event_duration(stream)
        event_start = self.create_event_start(stream)
        if stream.use_slot():
            assert(stream.slot.is_in_SP(event_start))
        event_frames = stream.get_frames().copy()
        event = Event(event_start, event_duration, event_frames)
        return event


    def create_event_start(self, stream):
        if self.received_DL_prompt != -1:
            return self.current_time + SIFS
        transmission_time = stream.get_transmission_time(self.backoff)
        assert(transmission_time is not None)
        if transmission_time == -1:
            event_start = 0
            if stream.priority > 0:
                # Prioritary streams get transmitted right after a SIFS
                event_start = self.current_time + SIFS
            else:
                # Otherwise, it uses a DIFS and backoff
                event_start = self.current_time + DIFS + self.backoff * BACKOFF_SLOT
            if stream.use_slot():
                assert(stream.slot.is_in_SP(event_start))
            return event_start
        elif transmission_time > 0:
            if stream.priority > 0:
                result = max(transmission_time, self.current_time + SIFS)
                if stream.use_slot():
                    assert(stream.slot.is_in_SP(result))
                return result
            else:
                result = max(transmission_time, self.current_time + DIFS + self.backoff * BACKOFF_SLOT)
                if stream.use_slot():
                    assert(stream.slot.is_in_SP(result))
                return result

    def create_event_duration(self, stream):
        data_rate = self.wlan.get_link_capacity(stream.get_receiver_ID())
        frame_table = stream.get_frames()[:MAX_AGGREGATED_FRAMES]
        is_ACK = len(frame_table) == 1 and frame_table[0].label == "ACK"
        total_size = sum([frame.size for frame in frame_table])
        total_size += MAC_HEADER_SIZE
        event_duration = PHY_HEADER_DURATION
        event_duration += Timestamp(total_size / data_rate)
        if not is_ACK:
            event_duration += ACK_DURATION
        return event_duration

    

### UPDATE INFORMATION and related functions

    def update_information(self, event):
        self.update_backoff(event)
        self.state_counter.add_event(event)
        if DEBUG:
            self.update_timeline(event)
        self.current_time = event.end
        self.update_UL_prompt_answer(event)
        self.update_received_DL_prompt(event)
        self.remove_sent_frames(event)
        self.update_stream_time()
        self.update_scheduled_to_pending()
        if event.is_DL_prompt():
            self.received_DL_prompt = event.get_sender_ID()
        self.verify_inner_state()

    def update_backoff(self, event):
        self.decrease_backoff(event)
        if event.is_sender(self.ID):
            if event.is_collision() or event.is_error():
                self.new_backoff_after_collision()
            else:
                self.new_backoff_after_success()        


    def remove_sent_frames(self, event):
        beacon_removed = self.remove_sent_beacon(event)
        DL_Tx_removed = self.remove_sent_DL_Tx(event)
        UL_prompt_removed = self.remove_sent_UL_prompt(event)
        for frame in event.frame_table:
            if frame.sender_ID == self.ID:
                if not frame.has_collided and not frame.is_in_error:
                    assert(beacon_removed or DL_Tx_removed or UL_prompt_removed or frame.label == "ACK")
        self.update_active_DL_prompt(event)

    def remove_sent_beacon(self, event):
        for frame in event.frame_table.copy():
            if frame.label == "beacon":
                self.stream_table[0].remove_frame(frame.ID)
                return True
        return False

    def remove_sent_DL_Tx(self, event):
        has_removed_frame = False
        for frame in event.frame_table.copy():
            if frame.sender_ID == self.ID:
                if not frame.has_collided and not frame.is_in_error:
                    if frame.label != "beacon" and frame.label != "UL prompt" and frame.label != "ACK":
                        STA_ID = frame.receiver_ID
                        stream_index = self.stream_information[str(STA_ID)]["DL Tx index"]
                        self.stream_table[stream_index].remove_frame(frame.ID)
                        has_removed_frame = True
        return has_removed_frame


    def remove_sent_UL_prompt(self, event):
        has_removed_frame = False
        for frame in event.frame_table.copy():
            if frame.sender_ID == self.ID:
                if not frame.has_collided and not frame.is_in_error:
                    if frame.label == "UL prompt":
                        STA_ID = frame.receiver_ID
                        stream_index = self.stream_information[str(STA_ID)]["UL prompt index"]
                        self.stream_table[stream_index].remove_frame(frame.ID)
                        self.sent_UL_prompt = STA_ID
                        has_removed_frame = True
        return has_removed_frame

    def update_active_DL_prompt(self, event):
        if self.received_DL_prompt != -1:
            stream_index = self.stream_information[str(self.received_DL_prompt)]["DL Tx index"]
            if event.is_sender(self.ID):
                if event.is_EOSP() and not event.is_collision() and not event.is_error():
                    self.received_DL_prompt = -1
                if len(event.frame_table) == 1 and event.frame_table[0].label == "ACK":
                    self.received_DL_prompt = -1

    def update_received_DL_prompt(self, event):
        if not event.is_collision() and not event.is_error() and event.is_receiver(self.ID):
            if len(event.frame_table) == 1 and event.frame_table[0].label == "DL prompt":
                assert(self.stream_information[str(event.frame_table[0].sender_ID)]["use DL prompt"])
                self.received_DL_prompt = event.frame_table[0].sender_ID

    def update_UL_prompt_answer(self, event):
        if self.sent_UL_prompt != -1:
            self.UL_prompt_answer += event.frame_table
            for frame in event.frame_table:
                assert(frame.sender_ID == self.sent_UL_prompt or frame.has_collided)
            if event.is_EOSP:
                stream_index = self.stream_information[str(self.sent_UL_prompt)]["UL prompt index"]
                self.stream_table[stream_index].set_prompt_answer(self.UL_prompt_answer)
                self.UL_prompt_answer = []
                self.sent_UL_prompt = -1
                
    def update_stream_time(self):
        for stream in self.stream_table:
            stream.update_time(self.current_time)        
                
    def update_scheduled_to_pending(self):
        while not self.streams_are_up_to_date():
            stream_index = self.get_index_of_oldest_scheduled_frame()
            if self.get_number_of_pending_frames() < self.buffer_capacity:
                self.stream_table[stream_index].buffer_scheduled_frame()
            else:
                self.stream_table[stream_index].drop_scheduled_frame()

    def streams_are_up_to_date(self):
        for stream in self.stream_table:
            if not stream.is_up_to_date():
                return False
        return True

    def get_number_of_pending_frames(self):
        total_nb_frames = 0
        for stream in self.stream_table:
            total_nb_frames += stream.get_number_of_pending_frames()
        return total_nb_frames

    def get_index_of_oldest_scheduled_frame(self):
        creation_time_table = [stream.get_scheduled_frame_creation_time() for stream in self.stream_table]
        oldest_creation_time = None
        for creation_time in creation_time_table:
            if creation_time is not None:
                if oldest_creation_time is None:
                    oldest_creation_time = creation_time
                elif creation_time < oldest_creation_time:
                    oldest_creation_time = creation_time
        if oldest_creation_time is None:
            return None
        else:
            return creation_time_table.index(oldest_creation_time)




### DEBUG and related functions

    def verify_inner_state(self):
        final_result = True
        for stream in self.stream_table:
            if stream.current_time != self.current_time:
                print(f"{Fore.RED}Stream is not synchrone.")
                print(f"Stream index:", self.stream_table.index(stream), f"{Style.RESET_ALL}")
                final_result = False
            stream.verify_inner_state()
        assert(final_result)

    def update_timeline(self, event):
        if DEBUG:
            self.timeline[0].add_until(event.start, '-')
            if len(event.frame_table) == 1 and event.frame_table[0].label == "beacon":
                self.timeline[0].add_until(event.end, 'b')
            if event.is_sender(self.ID):
                self.timeline[0].add_until(event.end, 'v')
            elif event.is_receiver(self.ID):
                if event.is_collision():
                    self.timeline[0].add_until(event.end, 'x')
                elif event.is_error():
                    self.timeline[0].add_until(event.end, 'R')
                elif event.is_DL_prompt():
                    self.timeline[0].add_until(event.end, 'p')
                else:
                    self.timeline[0].add_until(event.end, '*')
            else:
                self.timeline[0].add_until(event.end, '-')
            self.timeline[0].add_separation()

    def get_dictionary(self):
        result = {"ID": self.ID}
        DL_traffic_dict = dict()
        for STA_ID in self.stream_information:
            stream_index = self.stream_information[STA_ID]["DL Tx index"]
            DL_traffic_dict[STA_ID] = self.stream_table[stream_index].get_dictionary()
        result["DL traffic"] = DL_traffic_dict
        return result
