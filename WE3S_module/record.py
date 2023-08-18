from colorama import Fore
from colorama import Style

from WE3S.timestamp import *

class Record:
    def __init__(self):
        self.event_record = []
        self.current_time = Timestamp()

    def add_event(self, new_event):
        if self.current_time > new_event.start:
            print(f"{Fore.RED}ERROR: new event cannot be earlier than previous event.")
            print("\tCurrent time: ", self.current_time)
            print("\tEvent start: ", new_event.start)
            print("\tEvent label: ", new_event.label)
            print(f"{Style.RESET_ALL}")
        self.event_record.append(new_event.copy())
        self.current_time = new_event.end

    def reset(self):
        self.current_time = 0
        self.event_record.clear()

    def get_dictionary(self):
        result = dict()
        i = 0
        for event in self.event_record:
            key = "Event" + str(i)
            i += 1
            result[key] = event.get_dictionary()
        return result

    def __str__(self):
        result = "---\n"
        for event in self.event_record:
            result += event.__str__()
            result += "\n"
        return result
