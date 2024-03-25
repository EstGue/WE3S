from numpy import random
from colorama import Fore
from colorama import Style

from WE3S.frame import *

class Prompt_strategy:

    def __init__(self, strategy_name, arg_dict):
        self.strategy = None
        if strategy_name == "Constant":
            assert("Prompt interval" in arg_dict)
            interval = arg_dict["Prompt interval"]
            if "First prompt" in arg_dict:
                first_prompt = arg_dict["First prompt"]
            self.strategy = Prompt_strategy_Constant(interval, first_prompt)

        elif strategy_name == "AIMD":
            self.strategy = Prompt_strategy_AIMD(arg_dict["Min prompt interval"],
                                                 arg_dict["Max prompt interval"],
                                                 arg_dict["Prompt interval step"],
                                                 arg_dict["Objective nb returned frames"],
                                                 arg_dict["Max nb returned frames"])
        elif strategy_name == "Disabling AIMD":
            event_handler = arg_dict["Event handler"]
            STA_ID = arg_dict["STA ID"]
            self.strategy = Prompt_strategy_Disabling_AIMD(STA_ID, event_handler)
        else:
            print(f"{Fore.RED}This prompt strategy does not exist.")
            print("Must be in: Constant, AIMD, Disabling AIMD")
            print("Is:", strategy_name)
            print(f"{Style.RESET_ALL}")
            assert(0)

    def get_next_prompt_interval(self):
        return self.strategy.get_next_prompt_interval()

    def update_prompt_answer(self, complete_frame_table):
        self.strategy.update_prompt_answer(complete_frame_table)

    def monitor_events(self, event):
        self.strategy.monitor_events(event)

class Prompt_strategy_Constant :

    def __init__(self, prompt_interval, first_prompt=None):
        self.prompt_interval = prompt_interval
        if first_prompt is None:
            self.next_interval = random.randint(1, 100) * (self.prompt_interval / 100)
        else:
            assert(first_prompt >= 0)
            self.next_interval = first_prompt

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

    def __init__(self, min_prompt_interval, max_prompt_interval, prompt_interval_incrementation_step,
                 objective_nb_returned_frames, max_nb_returned_frames):
        self.min_prompt_interval = min_prompt_interval
        self.max_prompt_interval = max_prompt_interval
        self.prompt_interval_incrementation_step = prompt_interval_incrementation_step
        self.objective_nb_returned_frames = objective_nb_returned_frames
        self.max_nb_returned_frames = max_nb_returned_frames
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

    def __init__(self, STA_ID, event_handler):
        self.STA_ID = STA_ID
        self.event_handler = event_handler
        self.next_interval = 0.01
        self.is_active = True
        self.last_received_frame = -1
        self.time_before_enabling = 20 * 10**-3

    def get_next_prompt_interval(self):
        return self.next_interval

    def update_prompt_answer(self, complete_frame_table):
        nb_returned_frames = 0
        for frame in complete_frame_table:
            if not frame.is_in_error:
                nb_returned_frames += 1

        if self.is_active and nb_returned_frames > 20:
            print(f"{Fore.YELLOW}Prompt strategy: Disabling{Style.RESET_ALL}")
            self.is_active = False
            self.event_handler.disable_DL_prompt(self.STA_ID)

    
    def monitor_events(self, event):
        if event.is_receiver(self.STA_ID):
            if not event.is_collision():
                self.last_received_frame = event.end
        else:
            if event.end - self.last_received_frame > self.time_before_enabling:
                if not self.is_active:
                    print("Last received frame: ", self.last_received_frame)
                    print("Current time:", event.end)
                    print("Difference:", event.end - self.last_received_frame)
                    print(f"{Fore.YELLOW}Prompt strategy: Enabling {Style.RESET_ALL}")
                    self.is_active = True
                    self.event_handler.enable_DL_prompt(self.STA_ID)
