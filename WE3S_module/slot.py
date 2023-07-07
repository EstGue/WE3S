from visualisation import *
from event import *
from common_parameters import *

import math
import random

class Slot():
    def __init__(self, STA_ID, start, duration, interval):
        self.STA_ID = STA_ID
        self.start = start
        self.interval = interval
        self.duration = duration
        self.timeline = None
        if DEBUG:
            self.timeline = Visualisation()

    def is_in_SP(self, time):
        current_SP_start = self.get_current_SP_start(time)
        current_SP_end = self.get_current_SP_end(time)
        return current_SP_start <= time and time < current_SP_end

    def get_current_SP_start(self, current_time):
        # tmp = self.start
        # while tmp + self.interval < current_time:
        #     tmp += self.interval
        # return tmp
        
        nb_interval = current_time - self.start
        nb_interval = math.floor(nb_interval / self.interval)
        return self.interval * nb_interval + self.start

    def get_current_SP_end(self, current_time):
        return self.get_current_SP_start(current_time) + self.duration

    def get_next_SP_start(self, current_time):
        # return self.get_current_SP_start(current_time) + self.interval
        nb_interval = current_time - self.start
        nb_interval = math.floor(nb_interval / self.interval) + 1
        return self.interval * nb_interval + self.start + TIME_PRECISION

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
            "Start": self.start,
            "Interval": self.interval,
            "Duration": self.duration
        }
        return result


def unit_test_slot():
    slot = Slot(1, 0.4, 1/9, 1/3)

    for i in range(1000):
        print(i)
        # Time limits:
        k = random.randint(1, 100)
        n = random.randint(1, 100)
        nb_test = k/n
        assert(slot.is_in_SP(slot.get_current_SP_start(nb_test)))
        assert(not slot.is_in_SP(slot.get_current_SP_end(nb_test)))
        assert(slot.is_in_SP(slot.get_next_SP_start(nb_test)))
        assert(not slot.is_in_SP(slot.get_next_SP_end(nb_test)))
        assert(slot.get_current_SP_start(slot.get_next_SP_end(nb_test)) > nb_test)


    print("OK")
