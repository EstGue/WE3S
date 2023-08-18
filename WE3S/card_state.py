from colorama import Fore
from colorama import Style
from sortedcontainers import SortedSet

from WE3S.event import *
from WE3S.visualisation import *
from WE3S.common_parameters import *

class Card_state:

    def __init__(self, STA_ID):
        self.STA_ID = STA_ID
        
        self.Rx = Timestamp(0)
        self.Tx = Timestamp(0)
        self.CCA_busy = Timestamp(0)
        self.idle = Timestamp(0)
        self.doze = Timestamp(0)

        self.current_time = Timestamp(0)

        self.wakeup_time = None
        self.DL_slot = None
        
        self.timeline = None
        if DEBUG:
            self.timeline = Visualisation()



    def toggle_DL_slot(self, DL_slot):
        self.DL_slot = DL_slot
        self.wakeup_time = None

## HANDLES NEW EVENTS
            
    def add_event(self, event):
        if event.is_sender(self.STA_ID):
            self.nothing_happens_until(event.start)
            self.add_event_sender(event)
        elif event.is_receiver(self.STA_ID) and not event.is_collision():
            self.nothing_happens_until(event.start)
            self.add_event_receiver(event)
        elif event.is_beacon() and not self.is_dozing(event.start):
            self.nothing_happens_until(event.start)
            self.add_event_receiver(event)
        else:
            self.nothing_happens_until(event.start)
            self.add_event_not_participating(event)
            
        if DEBUG:
            self.timeline.add_separation()


    def nothing_happens_until(self, time):
        if self.DL_slot is None:
            if self.wakeup_time is None:
                self.idle_until(time)
            elif Timestamp(self.wakeup_time) <= self.current_time:
                self.idle_until(time)
            else:
                if self.wakeup_time < time:
                    self.doze_until(self.wakeup_time)
                    self.idle_until(time)
                else:
                    self.doze_until(time)
        else:
            # Use DL slot
            finish = False
            while not finish:
                if self.DL_slot.is_in_SP(self.current_time):
                    SP_end = self.DL_slot.get_current_SP_end(self.current_time)
                    if time <= SP_end:
                        finish = True
                    self.idle_until(min(SP_end, time))
                else:
                    next_SP_start = self.DL_slot.get_next_SP_start(self.current_time)
                    next_SP_end = self.DL_slot.get_next_SP_end(self.current_time)
                    self.doze_until(min(next_SP_start, time))
                    if time <= next_SP_start:
                        finish = True
                    else:
                        self.idle_until(min(next_SP_end, time))
                        if time <= next_SP_end:
                            finish = True



    def add_event_not_participating(self, event):
        if self.DL_slot is None:
            if self.wakeup_time <= self.current_time:
                self.CCA_busy_until(event.end)
            else:
                if self.wakeup_time < event.end:
                    self.doze_until(self.wakeup_time)
                    self.CCA_busy_until(event.end)
                else:
                    self.doze_until(event.end)
        else:
            # Use DL slot
            finish = False
            while not finish:
                if self.DL_slot.is_in_SP(self.current_time):
                    SP_end = self.DL_slot.get_current_SP_end(self.current_time)
                    if event.end <= SP_end:
                        finish = True
                    self.CCA_busy_until(min(SP_end, event.end))
                else:
                    next_SP_start = self.DL_slot.get_next_SP_start(self.current_time)
                    next_SP_end = self.DL_slot.get_next_SP_end(self.current_time)
                    self.doze_until(min(next_SP_start, event.end))
                    if event.end <= next_SP_start:
                        finish = True
                    else:
                        self.CCA_busy_until(min(next_SP_end, event.end))
                        if event.end <= next_SP_end:
                            finish = True


    def add_event_sender(self, event):
        self.idle_until(event.start)
        self.Tx_until(event.end)

    def add_event_receiver(self, event):
        self.idle_until(event.start)
        self.Rx_until(event.end)


            
## SCHEDULES DOZE PERIODS
        
    def switch_to_doze_state(self, wakeup_time):
        assert(self.current_time < wakeup_time)
        assert(wakeup_time - self.current_time > MIN_DOZE_DURATION)
        self.wakeup_time = wakeup_time
        # self.add_scheduled_doze((self.current_time - 1, wakeup_time))
            

    def is_dozing(self, time):
        if self.DL_slot is None:
            return time < self.wakeup_time
        else:
            return not self.DL_slot.is_in_SP(time)

    def clear_scheduled_doze(self):
        self.scheduled_doze_table.clear()
    


## FUNCTIONS TO ADD STATE DURING A GIVEN PERIOD                
            
    def doze_until(self, time):
        assert(self.current_time <= time)
        self.doze += time - self.current_time
        if DEBUG:
            self.timeline.add_until(time, 'z')
        self.current_time = time
        self.verify_inner_state()

    def idle_until(self, time):
        if not self.current_time <= time:
            print(f"{Fore.RED}Time can only flow in one direction.")
            print("Current time:", self.current_time)
            print("Idle until:", time, f"{Style.RESET_ALL}")
            assert(0)
        self.idle += time - self.current_time
        if DEBUG:
            self.timeline.add_until(time, 'i')
        self.current_time = time
        self.verify_inner_state()

    def Rx_until(self, time):
        assert(self.current_time <= time)
        self.Rx += time - self.current_time
        if DEBUG:
            self.timeline.add_until(time, 'r')
        self.current_time = time
        self.verify_inner_state()

    def Tx_until(self, time):
        assert(self.current_time <= time)
        self.Tx += time - self.current_time
        if DEBUG:
            self.timeline.add_until(time, 't')
        self.current_time = time
        self.verify_inner_state()

    def CCA_busy_until(self, time):
        assert(self.current_time <= time)
        self.CCA_busy += time - self.current_time
        if DEBUG:
            self.timeline.add_until(time, 'c')
        self.current_time = time
        self.verify_inner_state()



## DEBUG FUNCTIONS
        
    def verify_inner_state(self):
        result = True
        if self.current_time < 0:
            print(f"{Fore.RED}Card State: ERROR current_time")
            print(f"{Style.RESET_ALL}", end="")
            result = False
        
        if self.Rx < 0:
            print(f"{Fore.RED}Card State: ERROR Rx")
            print(f"{Style.RESET_ALL}", end="")
            result = False
        if self.Tx < 0:
            print(f"{Fore.RED}Card State: ERROR Tx")
            print(f"{Style.RESET_ALL}", end="")
            result = False
        if self.CCA_busy < 0:
            print(f"{Fore.RED}Card State: ERROR CCA_busy")
            print(f"{Style.RESET_ALL}", end="")
            result = False
        if self.idle < 0:
            print(f"{Fore.RED}Card State: ERROR idle")
            print(f"{Style.RESET_ALL}", end="")
            result = False
        if self.doze < 0:
            print(f"{Fore.RED}Card State: ERROR doze")
            print(f"{Style.RESET_ALL}", end="")
            result = False

        add = self.Rx + self.Tx + self.CCA_busy + self.idle + self.doze
        if self.current_time != add:
            print(f"{Fore.RED}Card State: ERROR state counters do not match current time")
            print("Current time:", self.current_time.s, "s", self.current_time.ms, "ms", self.current_time.us, "us")
            print("State addition:", add.s, "s", add.ms, "ms", add.us, "us")
            print(f"{Style.RESET_ALL}", end="")
            result = False
            
        assert(result)

        
    def get_dictionary(self):
        result = {
            "STA_ID": self.STA_ID,
            "Rx": float(self.Rx),
            "Tx": float(self.Tx),
            "CCA_busy": float(self.CCA_busy),
            "idle": float(self.idle),
            "doze": float(self.doze)
        }
        return result
