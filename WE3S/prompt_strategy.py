from numpy import random
from colorama import Fore
from colorama import Style

from WE3S.frame import *

class Prompt_strategy:

    def __init__(self):
        self.next_interval = 0

    def get_next_prompt_interval(self):
        return self.next_interval

    def update_prompt_answer(self, complete_frame_table):
        pass


class Prompt_strategy_None (Prompt_strategy):

    def __init__(self, prompt_interval, first_prompt=None):
        Prompt_strategy.__init__(self)
        self.prompt_interval = prompt_interval
        if first_prompt is None:
            self.next_interval = random.randint(1, 100) * (self.prompt_interval / 100)
        else:
            assert(first_prompt >= 0)
            self.next_interval = first_prompt

    def update_prompt_answer(self, complete_frame_table):
        self.next_interval = self.prompt_interval

    def get_dictionary(self):
        return {
            "Strategy name": "None",
            "Prompt interval": self.prompt_interval
        }

class Prompt_strategy_TCP_like (Prompt_strategy):

    def __init__(self, min_prompt_interval, max_prompt_interval, prompt_interval_incrementation_step,
                 objective_nb_returned_frames, max_nb_returned_frames):
        Prompt_strategy.__init__(self)
        self.min_prompt_interval = min_prompt_interval
        self.max_prompt_interval = max_prompt_interval
        self.prompt_interval_incrementation_step = prompt_interval_incrementation_step
        self.objective_nb_returned_frames = objective_nb_returned_frames
        self.max_nb_returned_frames = max_nb_returned_frames
        self.next_interval = self.min_prompt_interval

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

    def get_dictionary(self):
        return {
            "Strategy name": "TCP-like",
            "Min prompt interval": self.min_prompt_interval,
            "Max prompt interval": self.max_prompt_interval,
            "Prompt interval incrementation step": self.prompt_interval_incrementation_step,
            "Objective nb returned frames": self.objective_nb_returned_frames,
            "Max nb returned frames": self.max_nb_returned_frames
        }

