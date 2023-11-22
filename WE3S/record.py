from colorama import Fore
from colorama import Style

from WE3S.timestamp import *

class Record:
    def __init__(self):
        self.event_record = []
        self.STA_record = []
        self.current_time = Timestamp()

    def add_event(self, new_event, STA_record):
        if self.current_time > new_event.start:
            print(f"{Fore.RED}ERROR: new event cannot be earlier than previous event.")
            print("\tCurrent time: ", self.current_time)
            print("\tEvent start: ", new_event.start)
            print("\tEvent label: ", new_event.label)
            print(f"{Style.RESET_ALL}")
        self.event_record.append(new_event.copy())
        self.STA_record.append(STA_record.copy())
        self.current_time = new_event.end


    # def add_event2(self, new_event):
    #     if self.current_time > new_event.start:
    #         print(f"{Fore.RED}ERROR: new event cannot be earlier than previous event.")
    #         print("\tCurrent time: ", self.current_time)
    #         print("\tEvent start: ", new_event.start)
    #         print("\tEvent label: ", new_event.label)
    #         print(f"{Style.RESET_ALL}")
    #     self.event_record.append(new_event.copy())
    #     self.current_time = new_event.end

    def reset(self):
        self.current_time = 0
        self.event_record.clear()

    def get_dictionary(self):
        result = dict()
        i = 0
        for event, STA_record in zip(self.event_record, self.STA_record):
            key = "Event" + str(i)
            i += 1
            result[key] = event.get_dictionary()
            result[key]["STAs"] = STA_record
        return result

    def __str__(self):
        result = "---\n"
        for event in self.event_record:
            result += event.__str__()
            result += "\n"
        return result

    def copy(self):
        copy = Record()
        copy.event_record = self.event_record.copy()
        copy.current_time = Timestamp(self.current_time)
        return copy
