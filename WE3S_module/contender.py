import random

from common_parameters import *
from card_state import *
from WLAN import *

wlan = WLAN()

class Contender:

    def __init__(self, ID):
        global wlan
        self.wlan = wlan
        
        self.ID = ID
        self.current_time = 0
        
        self.backoff = 0
        self.contention_window = MIN_CONTENTION_WINDOW
        self.state_counter = Card_state(self.ID)
        
        self.timeline = None
        if DEBUG:
            self.timeline = [Visualisation()]
            self.timeline.append(self.state_counter.timeline)

            

## BACKOFF MANAGEMENT: utilitary functions

    def decrease_backoff(self, event):
        tmp = self.current_time + DIFS
        nb_slot = 0
        while tmp < event.start:
            tmp += BACKOFF_SLOT
            nb_slot += 1
        self.backoff = max(0, self.backoff - nb_slot)

    def new_backoff_after_collision(self):
        self.increase_contention_window()
        self.backoff = random.randint(1, self.contention_window)

    def new_backoff_after_success(self):
        self.reset_contention_window()
        self.backoff = random.randint(1, self.contention_window)        
  
        
    def reset_contention_window(self):
        self.contention_window = MIN_CONTENTION_WINDOW
        self.backoff = -1

    def increase_contention_window(self):
        self.contention_window *= 2
        if self.contention_window > MAX_CONTENTION_WINDOW:
            self.contention_window = MAX_CONTENTION_WINDOW
        self.backoff = -1



## DEBUG FUNCTIONS

    def print_timeline(self):
        if DEBUG:
            print(self.ID)
            for line in self.timeline:
                print(line)
