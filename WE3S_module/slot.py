import math
import random

from WE3S.visualisation import *
from WE3S.event import *
from WE3S.common_parameters import *
from WE3S.timestamp import *

class Slot():
    def __init__(self, STA_ID, start, duration, interval):
        self.STA_ID = STA_ID
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
        # tmp = self.start
        # while tmp + self.interval <= current_time:
        #     tmp += self.interval
        # return tmp
        
        # nb_interval = current_time - self.start
        # nb_interval = math.floor(nb_interval / self.interval)
        # return self.interval * nb_interval + self.start

    def get_current_SP_end(self, current_time):
        return self.get_current_SP_start(current_time) + self.duration

    def get_next_SP_start(self, current_time):
        return self.get_current_SP_start(current_time) + self.interval
        # nb_interval = current_time - self.start
        # nb_interval = math.floor(nb_interval / self.interval) + 1
        # return self.interval * nb_interval + self.start + TIME_PRECISION

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


def unit_test_slot():
    slot = Slot(1, 0.4, 1/9, 1/3)

    for i in range(1000):
        print(i)
        # Time limits:
        k = random.randint(1, 100)
        n = random.randint(1, 100)
        nb_test = Timestamp(k/n)
        assert(slot.is_in_SP(slot.get_current_SP_start(nb_test)))
        assert(not slot.is_in_SP(slot.get_current_SP_end(nb_test)))
        assert(slot.is_in_SP(slot.get_next_SP_start(nb_test)))
        assert(not slot.is_in_SP(slot.get_next_SP_end(nb_test)))
        assert(slot.get_current_SP_start(slot.get_next_SP_end(nb_test)) > nb_test)


    print("OK")
