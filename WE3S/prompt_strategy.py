from numpy import random
from colorama import Fore
from colorama import Style

from WE3S.frame import *

class Prompt_strategy:

    def __init__(self, strategy_name, arg_dict):
        self.strategy = None
        if strategy_name == "Constant":
            self.strategy = Prompt_strategy_Constant(arg_dict)

        elif strategy_name == "AIMD":
            self.strategy = Prompt_strategy_AIMD(arg_dict)

        elif strategy_name == "Disabling AIMD":
            self.strategy = Prompt_strategy_Disabling_AIMD(arg_dict)

        elif strategy_name == "Packet interval":
            self.strategy = Prompt_strategy_packet_interval(arg_dict)
            
        else:
            print(f"{Fore.RED}This prompt strategy does not exist.")
            print("Must be in: Constant, AIMD, Disabling AIMD")
            print("Is:", strategy_name)
            print(f"{Style.RESET_ALL}")
            assert(0)

    def get_next_prompt_interval(self):
        next_prompt_interval = self.strategy.get_next_prompt_interval()
        return next_prompt_interval

    def update_prompt_answer(self, complete_frame_table):
        # print(f"{Fore.YELLOW}Nb frames returned:", len(complete_frame_table), f"{Style.RESET_ALL}")
        self.strategy.update_prompt_answer(complete_frame_table)

    def monitor_events(self, event):
        self.strategy.monitor_events(event)


class Prompt_strategy_Constant :

    def __init__(self, arg_dict):
        assert("Prompt interval" in arg_dict)
        assert(arg_dict["Prompt interval"] > 0)
        self.prompt_interval = arg_dict["Prompt interval"]
        if "First prompt" in arg_dict:
            first_prompt = arg_dict["First prompt"]
            assert(first_prompt >= 0)
            self.next_interval = first_prompt
        else:
            self.next_interval = random.randint(1, 100) * (self.prompt_interval / 100)

    def get_next_prompt_interval(self):
        return self.next_interval
    
    def update_prompt_answer(self, complete_frame_table):
        self.next_interval = self.prompt_interval

    def monitor_events(self, event):
        pass
        
    def get_dictionary(self):
        return {
            "Strategy name": "Constant",
            "Prompt interval": self.prompt_interval
        }

class Prompt_strategy_AIMD (Prompt_strategy):

    def __init__(self, arg_dict):
        assert("Min prompt interval" in arg_dict)
        # etc...
        self.min_prompt_interval = arg_dict["Min prompt interval"]
        self.max_prompt_interval = arg_dict["Max prompt interval"]
        self.prompt_interval_incrementation_step = arg_dict["Prompt interval step"]
        self.objective_nb_returned_frames = arg_dict["Objective nb returned frames"]
        self.max_nb_returned_frames = arg_dict["Max nb returned frames"]
        self.next_interval = self.min_prompt_interval

    def get_next_prompt_interval(self):
        return self.next_interval
        
    def update_prompt_answer(self, complete_frame_table):
        nb_returned_frames = 0
        for frame in complete_frame_table:
            if not frame.is_in_error:
                nb_returned_frames += 1

        if nb_returned_frames >= self.max_nb_returned_frames:
            self.next_interval = self.min_prompt_interval
        elif nb_returned_frames > self.objective_nb_returned_frames:
            self.next_interval /= 2
        elif nb_returned_frames < self.objective_nb_returned_frames:
            self.next_interval += self.prompt_interval_incrementation_step

        self.next_interval = min(self.next_interval, self.max_prompt_interval)
        self.next_interval = max(self.next_interval, self.min_prompt_interval)

    def monitor_events(self, event):
        pass
        
    def get_dictionary(self):
        return {
            "Strategy name": "AIMD",
            "Min prompt interval": self.min_prompt_interval,
            "Max prompt interval": self.max_prompt_interval,
            "Prompt interval incrementation step": self.prompt_interval_incrementation_step,
            "Objective nb returned frames": self.objective_nb_returned_frames,
            "Max nb returned frames": self.max_nb_returned_frames
        }


class Prompt_strategy_Disabling_AIMD:

    def __init__(self, arg_dict):
        self.STA_ID = arg_dict["STA ID"]
        self.event_handler = arg_dict["Event handler"]
        self.min_prompt_interval = arg_dict["Min prompt interval"]
        self.max_prompt_interval = arg_dict["Max prompt interval"]
        self.prompt_interval_incrementation_step = arg_dict["Prompt interval step"]
        self.objective_nb_returned_frames = arg_dict["Objective nb returned frames"]
        self.max_nb_returned_frames = arg_dict["Max nb returned frames"]
        self.time_before_enabling = arg_dict["Time before enabling"]
        self.next_interval = self.min_prompt_interval

        self.is_active = True
        self.last_received_frame = -1

    def get_next_prompt_interval(self):
        return self.next_interval

    def update_prompt_answer(self, complete_frame_table):
        nb_returned_frames = 0
        for frame in complete_frame_table:
            if not frame.is_in_error:
                nb_returned_frames += 1

        if nb_returned_frames >= self.max_nb_returned_frames:
            if self.next_interval == self.min_prompt_interval:
                self.disable_prompt()
            self.next_interval = self.min_prompt_interval
        elif nb_returned_frames > self.objective_nb_returned_frames:
            self.next_interval /= 2
        elif nb_returned_frames < self.objective_nb_returned_frames:
            self.next_interval += self.prompt_interval_incrementation_step

        self.next_interval = min(self.next_interval, self.max_prompt_interval)
        self.next_interval = max(self.next_interval, self.min_prompt_interval)


    def monitor_events(self, event):
        if event.is_receiver(self.STA_ID):
            if not event.is_collision():
                self.last_received_frame = event.end
        else:
            if event.end - self.last_received_frame > self.time_before_enabling:
                if not self.is_active:
                    self.enable_prompt()

    def enable_prompt(self):
        print(f"{Fore.YELLOW}Prompt strategy: Enabling {Style.RESET_ALL}")
        self.is_active = True
        self.event_handler.enable_DL_prompt(self.STA_ID)

    def disable_prompt(self):
        print(f"{Fore.YELLOW}Prompt strategy: Disabling{Style.RESET_ALL}")
        self.is_active = False
        self.event_handler.disable_DL_prompt(self.STA_ID)
        
        
class Prompt_strategy_packet_interval (Prompt_strategy):

    def __init__(self, arg_dict):
        self.objective_nb_returned_frames = arg_dict["Objective nb returned frames"]
        self.nb_stored_values = arg_dict["Nb stored values"]
        self.next_prompt_interval = 0.005
        self.previous_prompt_interval = 0.005
        self.frame_interval_table = []
        self.nb_frames_table = []
        self.ongoing_frame_interval = 0

    def get_next_prompt_interval(self):
        return self.next_prompt_interval

    def update_prompt_answer(self, complete_frame_table):
        frame_interval, nb_frames = self.compute_new_value(complete_frame_table)
        if nb_frames > 0:
            self.add_value_in_table(frame_interval, nb_frames)
        avg_frame_interval = self.compute_average_frame_interval()
        if avg_frame_interval is not None:
            self.previous_prompt_interval = self.next_prompt_interval
            self.next_prompt_interval = self.objective_nb_returned_frames * avg_frame_interval

    def compute_new_value(self, complete_frame_table):
        nb_frames = 0
        for frame in complete_frame_table:
            if not frame.is_in_error:
                nb_frames += 1
        if nb_frames > 0:
            frame_interval = (self.previous_prompt_interval + self.ongoing_frame_interval) / nb_frames
            self.ongoing_frame_interval = 0
            return frame_interval, nb_frames
        else:
            self.ongoing_frame_interval += self.previous_prompt_interval
            return 0, 0

    def add_value_in_table(self, frame_interval, nb_frames):
        self.frame_interval_table.append(frame_interval)
        self.nb_frames_table.append(nb_frames)
        if len(self.frame_interval_table) > self.nb_stored_values:
            self.frame_interval_table.pop(0)
            self.nb_frames_table.pop(0)
        assert(len(self.frame_interval_table) == len(self.nb_frames_table))

    def compute_average_frame_interval(self):
        if len(self.frame_interval_table) == 0:
            return None
        avg_frame_interval = 0
        for frame_interval, nb_frames in zip(self.frame_interval_table, self.nb_frames_table):
            avg_frame_interval += nb_frames * frame_interval
        avg_frame_interval = avg_frame_interval / sum(self.nb_frames_table)
        return avg_frame_interval


    def monitor_events(self, event):
        pass
    
