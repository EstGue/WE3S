from colorama import Fore
from colorama import Style

from frame_generator import *
from common_parameters import *

class Stream:

    def __init__(self):
        self.frame_generator = None
        self.priority = 0
        self.pending_frame_table = []
        self.scheduled_frame = None

        self.slot = None
        self.received_prompt = None

        self.current_time = 0


### INITIALIZATION and related functions

    def initialize(self):
        self.scheduled_frame = self.frame_generator.get_frame()

    def use_slot(self):
        return self.slot is not None

    def use_prompt(self):
        return self.received_prompt is not None

    def get_destination_ID(self):
        return self.frame_generator.destination_ID

    def get_sender_ID(self):
        return self.frame_generator.sender_ID

    def toggle_slot(self, slot):
        assert(slot is not None)
        assert(not self.use_prompt())
        self.slot = slot

    def toggle_prompt(self):
        assert(not self.use_slot())
        self.received_prompt = False

### GET_NEXT_EVENT() and related functions

    def get_frames(self):
        if len(self.pending_frame_table) != 0:
            if len(self.pending_frame_table) <= MAX_AGGREGATED_FRAMES:
                self.pending_frame_table[-1].EOSP = True
                return self.pending_frame_table
            else:
                return self.pending_frame_table[:MAX_AGGREGATED_FRAMES]
        else:
            if not self.use_prompt():
                return [self.scheduled_frame]
            else:
                return [self.create_ACK()]

    def create_ACK(self):
        ACK = Frame(self.current_time, self.get_sender_ID(), self.get_destination_ID(), "ACK", "HIGH", ACK_SIZE)
        ACK.EOSP = True
        return ACK

    def get_transmission_time(self, backoff):
        # Returns None if the stream cannot emit now or later. (e.g. in case of prompts)
        # Returns -1 if the stream can emit right away
        # Returns the time when the stream can emit if it's later than now.
        if self.use_prompt():
            return self.get_transmission_time_prompt()
        elif self.use_slot():
            return self.get_transmission_time_slot(backoff)
        else:
            return self.get_transmission_time_raw()

    def get_transmission_time_raw(self):
        if len(self.pending_frame_table) != 0:
            return -1
        else:
            return self.scheduled_frame.creation_time

    def get_transmission_time_prompt(self):
        if not self.received_prompt:
            return None
        else:
            return -1

    def get_transmission_time_slot(self, backoff):
        delay = DIFS + backoff * BACKOFF_SLOT
        if len(self.pending_frame_table) != 0:
            tmp = self.current_time + delay
            if self.slot.is_in_SP(tmp):
                return -1
            else:
                transmission_time = self.slot.get_next_SP_start(self.current_time + delay) + TIME_PRECISION
                assert(self.slot.is_in_SP(transmission_time))
                return transmission_time
        else:
            transmission_time = self.scheduled_frame.creation_time
            transmission_time = max(transmission_time, self.current_time + DIFS + backoff * BACKOFF_SLOT)
            if self.slot.is_in_SP(transmission_time):
                return transmission_time
            else:
                revised_transmission_time = self.slot.get_next_SP_start(transmission_time) + TIME_PRECISION
                assert(self.slot.is_in_SP(revised_transmission_time))
                return revised_transmission_time

    def get_oldest_creation_time(self):
        # Returns creation_time of the oldest pending frames if the stream is pending
        # Otherwise, returns the creation time of the scheduled frame.
        if self.is_pending():
            return self.get_pending_frame_creation_time()
        else:
            return self.get_scheduled_frame_creation_time()
            
    def get_pending_frame_creation_time(self):
        assert(len(self.pending_frame_table) > 0)
        pending_creation_time_table = [frame.creation_time for frame in self.pending_frame_table]
        return min(pending_creation_time_table)

    def is_pending(self):
        return len(self.pending_frame_table) != 0



### UPDATE_INFORMATION and related functions

    def remove_frame(self, frame_ID):
        assert(frame_ID is not None)
        for frame in self.pending_frame_table:
            if frame.ID == frame_ID:
                self.pending_frame_table.remove(frame)
                return
        if frame_ID == self.scheduled_frame.ID:
            self.load_next_scheduled_frame()
        else:
            print(f"{Fore.RED}The frame does not belong to this stream")
            print(frame.get_dictionary())
            print("Pending frames:")
            for frame in self.pending_frame_table:
                print("\t", frame.get_dictionary())
            print("Scheduled frame:")
            print("\t", self.scheduled_frame.get_dictionary())
            print(f"{Style.RESET_ALL}")
            assert(0)

    def load_next_scheduled_frame(self):
        self.frame_generator.load_next_frame()
        self.scheduled_frame = self.frame_generator.get_frame()


    def update_time(self, current_time):
        self.current_time = current_time
    
    def is_up_to_date(self):
        return self.current_time < self.scheduled_frame.creation_time

    def get_buffer_size(self):
        return len(self.pending_frame_table)

    def get_scheduled_frame_creation_time(self):
        return self.scheduled_frame.creation_time

    def buffer_scheduled_frame(self):
        self.pending_frame_table.append(self.scheduled_frame)
        self.load_next_scheduled_frame()

    def drop_scheduled_frame(self):
        self.load_next_scheduled_frame()

### DEBUG

    def verify_inner_state(self):
        result_final = True
        if self.scheduled_frame is None:
            print(f"{Fore.RED}No frame is scheduled{Style.RESET_ALL}")
            result_final = False
        if self.get_scheduled_frame_creation_time() <= self.current_time:
            print(f"{Fore.RED}Stream is not up to date")
            print("Scheduled frame creation time:", self.get_scheduled_frame_creation_time())
            print("Current time:", self.current_time, f"{Style.RESET_ALL}")
            result_final = False
        for frame in self.pending_frame_table:
            if self.current_time < frame.creation_time:
                print(f"{Fore.RED}Pending frame is not yet created")
                print("Pending frame creation time:", frame.creation_time)
                print("Current time:", self.current_time, f"{Style.RESET_ALL}")
                result_final = False
        assert(result_final)

        
class Data_stream(Stream):

    def __init__(self, frame_generator):
        Stream.__init__(self)
        self.frame_generator = frame_generator



class Prompt_stream(Stream):

    def __init__(self, prompt_interval, sender_ID, destination_ID, label):
        Stream.__init__(self)

        assert(prompt_interval > 0)
        self.prompt_interval = prompt_interval
        self.sender_ID = sender_ID
        self.destination_ID = destination_ID
        self.label = label

    def initialize(self):
        creation_time = (random.randint(10, 100) / 100) * self.prompt_interval
        self.scheduled_frame = self.create_frame(creation_time)

    def get_destination_ID(self):
        return self.destination_ID

    def create_frame(self, creation_time):
        assert(creation_time > self.current_time)
        return Frame(creation_time, self.sender_ID, self.destination_ID, self.label, "LOW", PROMPT_SIZE)

    def remove_frame(self, frame_ID):
        for frame in self.pending_frame_table:
            if frame.ID == frame_ID:
                self.pending_frame_table.remove(frame)
                self.load_next_scheduled_frame()
                return
        if frame_ID == self.scheduled_frame.ID:
            self.load_next_scheduled_frame()
            return
        else:
            print(f"{Fore.RED}The frame does not belong to this stream")
            print(frame.get_dictionary(), f"Style.RESET_ALL")
            assert(0)

    def load_next_scheduled_frame(self):
        creation_time = self.current_time + self.prompt_interval
        self.scheduled_frame = self.create_frame(creation_time)

    def is_up_to_date(self):
        if self.scheduled_frame is None:
            return True
        else:
            return Stream.is_up_to_date(self)
            
    def verify_inner_state(self):
        if len(self.pending_frame_table) == 1:
            assert(self.scheduled_frame is None)
            assert(self.pending_frame_table[0].creation_time <= self.current_time)
        if len(self.pending_frame_table) == 0:
            assert(self.scheduled_frame is not None)
            assert(self.scheduled_frame.creation_time > self.current_time)
        if len(self.pending_frame_table) > 1:
            print(f"{Fore.RED}There can be no more than one prompt at a time")
            print("Number of prompts:", len(self.pending_frame_table))
            assert(0)

    def get_scheduled_frame_creation_time(self):
        if self.scheduled_frame is not None:
            return self.scheduled_frame.creation_time
        else:
            return None


            
    def buffer_scheduled_frame(self):
        assert(self.scheduled_frame.creation_time <= self.current_time)
        self.pending_frame_table = [self.scheduled_frame]
        self.scheduled_frame = None

        
    def drop_scheduled_frame(self):
        self.buffer_scheduled_frame()



class Beacon_stream(Stream):

    def __init__(self):
        Stream.__init__(self)
        self.priority = 1
        self.frame_generator = Frame_generator(1, BEACON_SIZE, 0, 0, "beacon", False)
        self.frame_generator.set_frequency(1 / TBTT)
        # self.frame_generator.is_interval_random = False

    def update_time(self, current_time):
        Stream.update_time(self, current_time)
        if len(self.pending_frame_table) != 0:
            if self.current_time - self.pending_frame_table[0].creation_time > BEACON_EXPIRATION_DATE:
                self.pending_frame_table.clear()

    def drop_scheduled_frame(self):
        self.buffer_scheduled_frame()

    def verify_inner_state(self):
        Stream.verify_inner_state(self)
        if not len(self.pending_frame_table) in [0,1]:
            print(f"{Fore.RED}There cannot be more than one pending beacon at a time.")
            print("Pending frames:")
            for frame in self.pending_frame_table:
                print("\t", frame.get_dictionary())
            print(f"{Style.RESET_ALL}")
            assert(0)

    def remove_frame(self, frame_ID):
        if frame_ID is None:
            if len(self.pending_frame_table) != 0:
                self.pending_frame_table.clear()
            else:
                self.load_next_scheduled_frame()
        else:
            if len(self.pending_frame_table) != 0:
                assert(self.pending_frame_table[0].ID == frame_ID)
                self.pending_frame_table.clear()
            else:
                if self.scheduled_frame.ID != frame_ID:
                    print(f"{Fore.RED}This frame does not belong to this stream.")
                    print("Frame ID:", frame_ID)
                    print("Scheduled beacon:", self.scheduled_frame.get_dictionary())
                    print(f"{Style.RESET_ALL}")
                    assert(0)
                self.load_next_scheduled_frame()
