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
        self.contenders.clear()
        ap = AP(0)
        self.contenders = [ap]
        for i in range(1, nb_STAs+1):
            sta = STA(i)
            self.contenders.append(sta)
            ap.add_STA(sta)


    def set_DL_traffic(self, STA_ID, traffic_type, arg_dict):
        assert(STA_ID > 0 and STA_ID <= len(self.contenders))
        self.contenders[0].set_DL_traffic(STA_ID, traffic_type, arg_dict)

    def set_UL_traffic(self, STA_ID, traffic_type, arg_dict):
        assert(STA_ID > 0 and STA_ID <= len(self.contenders))
        self.contenders[STA_ID].set_UL_traffic(traffic_type, arg_dict)

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

    def toggle_DL_slot(self, STA_ID, first_start, duration, interval):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        assert(duration < interval)
        assert(first_start < interval)
        DL_slot = Slot(STA_ID, first_start, duration, interval)
        self.contenders[STA_ID].toggle_DL_slot(DL_slot)
        self.contenders[0].toggle_DL_slot(STA_ID, DL_slot)

    def toggle_DL_prompt(self, STA_ID, strategy_name, arg_dict):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        self.contenders[STA_ID].toggle_DL_prompt(strategy_name, arg_dict)
        self.contenders[0].toggle_DL_prompt(STA_ID)

    def toggle_UL_slot(self, STA_ID, first_start, duration, interval):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        assert(duration < interval)
        assert(first_start < interval)
        UL_slot = Slot(STA_ID, first_start, duration, interval)
        self.contenders[STA_ID].toggle_UL_slot(UL_slot)

    def toggle_UL_prompt(self, STA_ID, strategy_name, arg_dict):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        self.contenders[STA_ID].toggle_UL_prompt()
        self.contenders[0].toggle_UL_prompt(STA_ID, strategy_name, arg_dict)


    def deactivate_random_error_on_frame(self):
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
                "Frame counter": DL_traffic.frame_generator.frame_counter,
                "Generated data": DL_traffic.frame_generator.total_generated_data,
                "Pending frames": len(DL_traffic.pending_frame_table)
            }
            STA_dict["DL traffic"] = DL_traffic_dict
            UL_traffic = self.contenders[STA_ID].UL_data_stream
            UL_traffic_dict = {
                "Frame counter": UL_traffic.frame_generator.frame_counter,
                "Generated data": UL_traffic.frame_generator.total_generated_data,
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
    

    def get_record(self):
        result = dict()
        all_STA_dict = dict()
        for STA in self.contenders[1:]:
            STA_dict = dict()
            STA_dict["Datarate"] = STA.wlan.get_link_capacity(STA.ID)
            STA_dict["use DL slot"] = STA.use_DL_slot()
            STA_dict["use DL prompt"] = STA.use_DL_prompt()
            STA_dict["use UL slot"] = STA.use_UL_slot()
            STA_dict["use UL prompt"] = STA.use_UL_prompt()
            if STA_dict["use DL slot"]:
                # DL_slot_dict = dict()
                # DL_slot_dict["Start"] = float(STA.DL_slot.start)
                # DL_slot_dict["Duration"] = STA.DL_slot.duration
                # DL_slot_dict["Interval"] = STA.DL_slot.interval
                STA_dict["DL slot"] = STA.DL_slot.get_dictionary()
            if STA_dict["use UL slot"]:
                # UL_slot_dict = dict()
                # UL_slot_dict["Start"] = STA.UL_slot.start
                # UL_slot_dict["Duration"] = STA.UL_slot.duration
                # UL_slot_dict["Interval"] = STA.UL_slot.interval
                STA_dict["UL slot"] = STA.UL_slot.get_dictionary()
            all_STA_dict[str(STA.ID)] = STA_dict

        result["STAs"] = all_STA_dict
        result["Events"] = self.record.get_dictionary()
        
        return result

