from colorama import Fore
from colorama import Style
from sortedcontainers import SortedSet
from numpy import random
import math
import gc
import time

from WE3S.event import *
from WE3S.record import *
from WE3S.AP import *
from WE3S.STA import *
from WE3S.slot import *


class Event_handler:

    def __init__(self):
        self.events = []
        self.contenders = []
        self.next_event = None
        self.current_time = Timestamp()
        self.sent_frames = SortedSet()
        self.record = Record()
        self.PER = PER

        self.contenders.append(AP(0))


    ## SET SIMULATION PARAMETERS

    def set_nb_STAs(self, nb_STAs):
        ap = self.contenders[0]
        self.contenders.clear()
        self.contenders = [ap]
        for i in range(1, nb_STAs+1):
            sta = STA(i)
            self.contenders.append(sta)
            ap.add_STA(sta)


    def add_DL_traffic(self, STA_ID, traffic_type, arg_dict, label, start, end):
        assert(STA_ID > 0 and STA_ID <= len(self.contenders))
        self.contenders[0].add_DL_traffic(STA_ID, traffic_type, arg_dict, label, start, end)

    def add_UL_traffic(self, STA_ID, traffic_type, arg_dict, label, start, end):
        assert(STA_ID > 0 and STA_ID <= len(self.contenders))
        self.contenders[STA_ID].add_UL_traffic(traffic_type, arg_dict, label, start, end)

    def set_link_capacity(self, STA_ID, link_capacity):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        assert(link_capacity > 0)
        ap = self.contenders[0]
        ap.wlan.set_link_capacity(STA_ID, link_capacity)

    def set_buffer_capacity_AP(self, buffer_capacity):
        assert(buffer_capacity > 0)
        self.contenders[0].buffer_capacity = buffer_capacity

    def set_buffer_capacity_STA(self, STA_ID, buffer_capacity):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        assert(buffer_capacity > 0)
        self.contenders[STA_ID].buffer_capacity = buffer_capacity

    def initialize_DL_slot(self, STA_ID, slot_type, arg_dict):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        DL_slot = Slot(slot_type, arg_dict)
        self.contenders[STA_ID].initialize_DL_slot(DL_slot)
        self.contenders[0].initialize_DL_slot(STA_ID, DL_slot)

    def initialize_DL_prompt(self, STA_ID, strategy_name, arg_dict):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        arg_dict["Event handler"] = self
        arg_dict["STA ID"] = STA_ID
        self.contenders[STA_ID].initialize_DL_prompt(strategy_name, arg_dict)
        self.contenders[0].initialize_DL_prompt(STA_ID)

    def initialize_UL_slot(self, STA_ID, first_start, duration, interval):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        assert(duration < interval)
        assert(first_start < interval)
        UL_slot = Slot("Static", {"First start": first_start,
                                  "Duration": duration,
                                  "Interval": interval})
        self.contenders[STA_ID].initialize_UL_slot(UL_slot)

    def initialize_UL_prompt(self, STA_ID, strategy_name, arg_dict):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        self.contenders[STA_ID].initialize_UL_prompt()
        self.contenders[0].initialize_UL_prompt(STA_ID, strategy_name, arg_dict)


    def disable_random_error_on_frame(self):
        self.PER = None

    ## HANDLE EVENTS

    def retrieve_events(self):
        self.events.clear()
        for contender in self.contenders:
            event = contender.get_next_event(self.current_time)
            if event is not None:
                assert(event.start >= self.current_time)
                for frame in event.frame_table:
                    assert(frame.sender_ID == contender.ID)
                    if frame.creation_time > event.start:
                        print(f"{Fore.RED}The event cannot start before the frame was created.")
                        print("Event start:", event.start)
                        print("Frame:", frame.get_dictionary())
                        print(f"{Style.RESET_ALL}")
                        assert(0)
                self.events.append(event)

    def elect_next_event(self):
        earliest_events = self.get_earliest_events()
        if len(earliest_events) == 0:
            # This point should be never reached.
            self.next_event = Event(self.current_time + 0.1, 0, None)
        elif self.current_time + SIMULATION_TIME_STEP < earliest_events[0].start:
            # Ensures that the contenders update themselves regularly, even if there are no event
            self.next_event = Event(self.current_time + SIMULATION_TIME_STEP, 0, [])
        elif len(earliest_events) == 1:
            # Error on the frame
            self.next_event = earliest_events[0]
            for frame in self.next_event.frame_table:
                frame.nb_of_transmissions += 1
                if self.PER is not None and random.binomial(size=1, n=1, p=PER):
                    frame.is_in_error = True
                else:
                    if frame.ID in self.sent_frames:
                        print(f"{Fore.RED}This frame has already been successfully sent.")
                        print(frame.get_dictionary())
                        print(f"{Style.RESET_ALL}")
                    assert(not frame.ID in self.sent_frames)
                    self.sent_frames.add(frame.ID)

        else:
            # Collision
            duration = max([event.duration for event in earliest_events])
            start = earliest_events[0].start
            self.next_event = Event(start, duration, [])
            for event in earliest_events:
                self.next_event.frame_table += event.frame_table
            for frame in self.next_event.frame_table:
                frame.nb_of_transmissions += 1
                frame.has_collided = True
        self.current_time = self.next_event.end
        self.record_event()
        self.verify_next_event()

    def verify_next_event(self):
        event = self.next_event
        for frame in event.frame_table:
            if frame.sender_ID == frame.receiver_ID:
                assert(frame.label == "beacon")
                assert(len(event.frame_table) == 1 or frame.has_collided)
            elif frame.label == "UL Tx" or frame.label == "DL prompt":
                assert(frame.receiver_ID == 0)
                assert(frame.sender_ID != 0)
            elif frame.label == "DL Tx" or frame.label == "UL prompt":
                assert(frame.receiver_ID != 0)
                assert(frame.sender_ID == 0)
            elif frame.label == "ACK":
                if frame.sender_ID == 0:
                    assert(frame.receiver_ID != 0)
                elif frame.sender_ID != 0:
                    assert(frame.receiver_ID == 0)

    def inform_contenders(self):
        for contender in self.contenders:
            contender.update_information(self.next_event)
        for frame in self.next_event.frame_table:
            frame.is_in_error = False
            frame.has_collided = False

    def record_event(self):
        all_STA_dict = dict()
        nb_STAs = len(self.contenders)
        for STA_ID in range(1, nb_STAs):
            STA_dict = dict()
            DL_traffic_index = self.contenders[0].stream_information[str(STA_ID)]["DL Tx index"]
            DL_traffic = self.contenders[0].stream_table[DL_traffic_index]
            DL_traffic_dict = {
                "Frame counter": DL_traffic.frame_generator.get_frame_counter(),
                "Generated data": DL_traffic.frame_generator.get_total_generated_data(),
                "Pending frames": len(DL_traffic.pending_frame_table)
            }
            STA_dict["DL traffic"] = DL_traffic_dict
            UL_traffic = self.contenders[STA_ID].UL_data_stream
            UL_traffic_dict = {
                "Frame counter": UL_traffic.frame_generator.get_frame_counter(),
                "Generated data": UL_traffic.frame_generator.get_total_generated_data(),
                "Pending frames": len(UL_traffic.pending_frame_table)
            }
            STA_dict["UL traffic"] = UL_traffic_dict
            # STA_dict["Datarate"] = self.contenders[0].wlan.get_link_capacity(STA_ID)
            state_counter = self.contenders[STA_ID].state_counter
            STA_dict["Tx time"] = float(state_counter.Tx)
            STA_dict["Rx time"] = float(state_counter.Rx)
            STA_dict["CCA time"] = float(state_counter.CCA_busy)
            STA_dict["idle time"] = float(state_counter.idle)
            STA_dict["doze time"] = float(state_counter.doze)
            all_STA_dict[str(STA_ID)] = STA_dict.copy()
        
        gc.disable()
        self.record.add_event(self.next_event, all_STA_dict)
        gc.enable()
        assert(self.record.current_time == self.current_time)

    def print_timeline(self):
        for contender in self.contenders:
            contender.print_timeline()

    def get_earliest_events(self):
        if len(self.events) == 0:
            return []
        elif len(self.events) == 1:
            return [self.events[0]]
        else:
            earliest_start = self.events[0].start
            for event in self.events:
                if event.start < earliest_start:
                    earliest_start = event.start
            earliest_events = []
            for event in self.events:
                if event.start == earliest_start:
                    earliest_events.append(event)
            return earliest_events


    def disable_DL_prompt(self, STA_ID):
        assert(STA_ID > 0 and STA_ID <= len(self.contenders))
        self.contenders[0].disable_DL_prompt(STA_ID)
        self.contenders[STA_ID].disable_DL_prompt()

    def enable_DL_prompt(self, STA_ID):
        assert(STA_ID > 0 and STA_ID <= len(self.contenders))
        self.contenders[0].enable_DL_prompt(STA_ID)
        self.contenders[STA_ID].enable_DL_prompt()

        
    ## GET END RESULTS

    def get_record(self):
        result = dict()
        all_STA_dict = dict()
        for STA in self.contenders[1:]:
            STA_dict = STA.get_dictionary()
            all_STA_dict[str(STA.ID)] = STA_dict

        result["STAs"] = all_STA_dict
        result["Events"] = self.record.get_dictionary()
        
        return result


