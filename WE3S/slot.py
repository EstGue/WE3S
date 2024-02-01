import math
from numpy import random
from colorama import Fore
from colorama import Style

from WE3S.visualisation import *
from WE3S.event import *
from WE3S.common_parameters import *
from WE3S.timestamp import *

class Slot():

    def __init__(self, slot_type, arg_dict):
        self.slot = None
        
        if slot_type == "Static":
            assert("First start" in arg_dict)
            assert("Duration" in arg_dict)
            assert("Interval" in arg_dict)
            first_start = arg_dict["First start"]
            duration = arg_dict["Duration"]
            interval = arg_dict["Interval"]
            self.slot = Static_slot(first_start, duration, interval)

        elif slot_type == "Dynamic":
            assert("Start" in arg_dict)
            assert("Duration" in arg_dict)
            start_table = arg_dict["Start"]
            duration_table = arg_dict["Duration"]
            self.slot = Dynamic_slot(start_table, duration_table)

        else:
            print(f"{Fore.RED}Unrecognized slot type")
            print("Possible slot types: Static, Dynamic")
            print("Given slot type:", slot_type)
            print(f"{Style.RESET_ALL}")
            assert(False)

    def is_in_SP(self, time):
        return self.slot.is_in_SP(time)
    
    def get_current_SP_start(self, current_time):
        return self.slot.get_current_SP_start(current_time)

    def get_current_SP_end(self, current_time):
        return self.slot.get_current_SP_end(current_time)

    def get_next_SP_start(self, current_time):
        return self.slot.get_next_SP_start(current_time)

    def get_next_SP_end(self, current_time):
        return self.slot.get_next_SP_end(current_time)

    def update_timeline(self, event):
        return self.slot.update_timeline(event)

    def get_timeline(self):
        return self.slot.timeline
                                
    def get_dictionary(self):
        return self.slot.get_dictionary()

class Static_slot():

    def __init__(self, start, duration, interval):
        assert(interval > 0 and duration > 0 and start >= 0)
        assert(duration < interval)
        assert(start < interval)

        self.start = Timestamp(start)
        self.interval = Timestamp(interval)
        self.duration = Timestamp(duration)
        self.timeline = None
        if DEBUG:
            self.timeline = Visualisation()

    def is_in_SP(self, time):
        current_SP_start = self.get_current_SP_start(time)
        current_SP_end = self.get_current_SP_end(time)
        return current_SP_start <= time and time < current_SP_end

    def get_current_SP_start(self, current_time):
        current_time_int = current_time.us + current_time.ms * 10**3 + current_time.s * 10**6
        interval_int = self.interval.us + self.interval.ms * 10**3 + self.interval.s * 10**6
        start_int = self.start.us + self.start.ms * 10**3 + self.start.s * 10**6
        multiplier = (current_time_int - start_int) // interval_int
        return self.start + multiplier * self.interval

    def get_current_SP_end(self, current_time):
        return self.get_current_SP_start(current_time) + self.duration

    def get_next_SP_start(self, current_time):
        return self.get_current_SP_start(current_time) + self.interval

    def get_next_SP_end(self, current_time):
        return self.get_next_SP_start(current_time) + self.duration

    def update_timeline(self, event):
        if self.timeline.timeline_current_time != event.end:
            while self.timeline.timeline_current_time < event.end:
                timeline_time = self.timeline.timeline_current_time
                self.timeline.add_until(min(event.end, self.get_current_SP_end(timeline_time)), '=')
                self.timeline.add_until(min(event.end, self.get_next_SP_start(timeline_time)), '.')
            self.timeline.add_separation()
                        
        
    def get_dictionary(self):
        result = {
            "Start": float(self.start),
            "Interval": float(self.interval),
            "Duration": float(self.duration)
        }
        return result


class Dynamic_slot():

    def __init__(self, start_table, duration_table):
        self.start_table = []
        self.duration_table = []
        for start, duration in zip(start_table, duration_table):
            assert(start >= 0)
            assert(duration > 10**-6)
            self.start_table.append(Timestamp(start))
            self.duration_table.append(Timestamp(duration))

        # The slots must be ordered
        previous_start = self.start_table[0]
        for start in self.start_table[1:]:
            assert(previous_start < start)
            prevous_start = start

        self.last_index_asked = None

        self.timeline = None
        if DEBUG:
            self.timeline = Visualisation()

    def is_in_SP(self, time):
        index = self.get_current_SP_index(time)
        start = self.start_table[index]
        end = self.start_table[index] + self.duration_table[index]
        return start <= time and time < end

    def get_current_SP_start(self, time):
        index = self.get_current_SP_index(time)
        start = self.start_table[index]
        return start

    def get_current_SP_end(self, time):
        index = self.get_current_SP_index(time)
        start = self.start_table[index]
        return self.start_table[index] + self.duration_table[index]

    def get_next_SP_start(self, time):
        index = self.get_current_SP_index(time)
        if index == len(self.start_table) - 1:
            # No more scheduled DL slot
            return Timestamp(10**10)
        return self.start_table[index+1]

    def get_next_SP_end(self, time):
        index = self.get_current_SP_index(time)
        if index == len(self.start_table) - 1:
            # No more scheduled DL slot
            return Timestamp(10**11)
        return self.start_table[index+1] + self.duration_table[index+1]

    def get_current_SP_index(self, time):
        if self.last_index_asked is None:
            self.last_index_asked = 0
        elif self.start_table[self.last_index_asked] > time:
            self.last_index_asked = 0
        for i in range(self.last_index_asked, len(self.start_table)):
            start = self.start_table[i]
            if time < start :
                self.last_index_asked = max(0, i-1)
                return max(0, i-1)
        self.last_index_asked = len(self.start_table)-1
        return len(self.start_table)-1
                

        
    def update_timeline(self, event):
        if self.timeline.timeline_current_time != event.end:
            while self.timeline.timeline_current_time < event.end:
                timeline_time = self.timeline.timeline_current_time
                self.timeline.add_until(min(event.end, self.get_current_SP_end(timeline_time)), '=')
                self.timeline.add_until(min(event.end, self.get_next_SP_start(timeline_time)), '.')
            self.timeline.add_separation()

    def get_dictionary(self):
        pass

def unit_test_slot():
    start = [0.4 +k/3 for k in range(100)]
    duration = [1/9 for k in range(100)]
    # slot = Slot(1, 0.4, 1/9, 1/3)
    slot = Dynamic_slot(start, duration)

    for i in range(1000):
        print(i)
        # Time limits:
        k = random.randint(1, 100)
        n = random.randint(1, 100)
        nb_test = Timestamp(k/n)
        print("\tcurrent SP start: ", slot.get_current_SP_start(nb_test))
        print("\tCurrent SP end: ", slot.get_current_SP_end(nb_test))
        print("\tNext SP start:", slot.get_next_SP_start(nb_test))
        assert(slot.is_in_SP(slot.get_current_SP_start(nb_test)))
        assert(not slot.is_in_SP(slot.get_current_SP_end(nb_test)))
        assert(slot.is_in_SP(slot.get_next_SP_start(nb_test)))
        assert(not slot.is_in_SP(slot.get_next_SP_end(nb_test)))
        assert(slot.get_current_SP_start(slot.get_next_SP_end(nb_test)) > nb_test)


    print("OK")
    
