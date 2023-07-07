from colorama import Fore
from colorama import Style
from sortedcontainers import SortedSet
import math
import gc
import time
import random

from event import *
from record import *
from AP import *
from STA import *
from slot import *


class Event_handler:

    def __init__(self):
        self.events = []
        self.contenders = []
        self.next_event = None
        self.current_time = 0
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

    def set_DL_throughput(self, STA_ID, throughput, is_interval_random):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        assert(throughput > 0)
        self.contenders[STA_ID].set_DL_throughput(throughput, is_interval_random)

    def set_UL_throughput(self, STA_ID, throughput, is_interval_random):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        assert(throughput > 0)
        self.contenders[STA_ID].set_UL_throughput(throughput, is_interval_random)

    def set_link_capacity(self, STA_ID, link_capacity):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        assert(link_capacity > 0)
        ap = self.contenders[0]
        ap.wlan.set_link_capacity(STA_ID, link_capacity)

    def set_buffer_size_AP(self, buffer_size):
        assert(buffer_size > 0)
        self.contenders[0].buffer_capacity = buffer_size

    def set_buffer_size_STA(self, STA_ID, buffer_size):
        self.contenders[STA_ID].buffer_capacity = buffer_size

    def toggle_DL_slot(self, STA_ID, first_start, duration, interval):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        assert(duration < interval)
        assert(first_start < interval)
        DL_slot = Slot(STA_ID, first_start, duration, interval)
        self.contenders[STA_ID].toggle_DL_slot(DL_slot)
        self.contenders[0].toggle_DL_slot(STA_ID, DL_slot)

    def toggle_DL_prompt(self, STA_ID, prompt_interval):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        assert(prompt_interval > 0)
        self.contenders[STA_ID].toggle_DL_prompt(prompt_interval)
        self.contenders[0].toggle_DL_prompt(STA_ID, prompt_interval)

    def toggle_UL_slot(self, STA_ID, first_start, duration, interval):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        assert(duration < interval)
        assert(first_start < interval)
        UL_slot = Slot(STA_ID, first_start, duration, interval)
        self.contenders[STA_ID].toggle_UL_slot(UL_slot)

    def toggle_UL_prompt(self, STA_ID, prompt_interval):
        assert(STA_ID > 0 and STA_ID < len(self.contenders))
        assert(prompt_interval > 0)
        self.contenders[STA_ID].toggle_UL_prompt()
        self.contenders[0].toggle_UL_prompt(STA_ID, prompt_interval)


    def deactivate_random_error_on_frame(self):
        self.PER = None
        
    ## HANDLE EVENTS

    def retrieve_events(self):
        self.events.clear()
        for contender in self.contenders:
            event = contender.get_next_event(self.current_time)
            if event is not None:
                assert(event.start >= self.current_time)
                for frame in event.frames:
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
        if len(earliest_events) == 0 or earliest_events[0].start - self.current_time > MAX_NO_EVENT_PERIOD:
            self.next_event = Event(self.current_time + MAX_NO_EVENT_PERIOD, 0, None)
        elif len(earliest_events) == 1:
            # Error on the frame
            self.next_event = earliest_events[0]
            for frame in self.next_event.frames:
                frame.nb_of_transmissions += 1
                if self.PER is not None and random.randint(1, 1 / self.PER) == 1:
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
            self.next_event = Event(start, duration, None)
            for event in earliest_events:
                self.next_event.frames += event.frames
            for frame in self.next_event.frames:
                frame.nb_of_transmissions += 1
                frame.has_collided = True
        self.current_time = self.next_event.end
        self.record_event()
        self.verify_next_event()

    def verify_next_event(self):
        event = self.next_event
        for frame in event.frames:
            if frame.sender_ID == frame.receiver_ID:
                assert(frame.label == "beacon")
                assert(len(event.frames) == 1 or frame.has_collided)
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
        for frame in self.next_event.frames:
            frame.is_in_error = False
            frame.has_collided = False

    def record_event(self):
        gc.disable()
        self.record.add_event(self.next_event)
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
                if abs(event.start - earliest_start) < TIME_PRECISION:
                    earliest_events.append(event)
            return earliest_events
    


