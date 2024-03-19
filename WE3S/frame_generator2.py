from numpy import random

from WE3S.frame import *
from WE3S.timestamp import *

class Aggregated_frame_generator:

    def __init__(self, sender_ID, receiver_ID, label):
        self.sender_ID = sender_ID
        self.receiver_ID = receiver_ID
        self.label = label
        
        self.frame_generator_table = []
        self.current_frame = None
        self.next_frame_time = None

    def add_frame_generator(self, generator_type, arg_dict, generation_start, generation_end):
        frame_generator = None
        if generator_type == "CBR":
            frame_size = arg_dict["Frame size"]
            frame_interval = arg_dict["Frame interval"]
            frame_generator = Frame_generator_CBR(frame_size, frame_interval)
        elif generator_type == "Poisson":
            frame_size = arg_dict["Frame size"]
            frame_interval = arg_dict["Frame interval"]
            frame_generator = Frame_generator_Poisson(frame_size, frame_interval)
        elif generator_type == "Hyperexponential":
            frame_size = arg_dict["Frame size"]
            frame_interval_1 = arg_dict["Frame interval 1"]
            frame_interval_2 = arg_dict["Frame interval 2"]
            interval_probability = arg_dict["Interval probability"]
            frame_generator = Frame_generator_hyperexponential(frame_size,
                                                               frame_interval_1, frame_interval_2, interval_probability)
        elif generator_type == "Trace":
            trace_filename = arg_dict["Trace filename"]
            frame_generator = Frame_generator_trace(trace_filename)
        else:
            print(f"{Fore.RED}Unrecognized traffic type")
            print("Possible traffic type: CBR, Poisson, Hyperexponential, Trace")
            print("Given traffic type:", generator_type)
            print(f"{Style.RESET_ALL}")
            assert(False)
        assert(frame_generator is not None)
        frame_generator.set_generation_start(generation_start)
        frame_generator.set_generation_end(generation_end)
        frame_generator.set_sender_ID(self.sender_ID)
        frame_generator.set_receiver_ID(self.receiver_ID)
        frame_generator.set_label(self.label)
        self.frame_generator_table.append(frame_generator)

    def get_current_frame_time(self):
        return self.current_frame.creation_time

    def get_next_frame_time(self):
        return self.next_frame_time

    def get_frame(self):
        return self.current_frame

    def get_sender_ID(self):
        return self.sender_ID

    def get_receiver_ID(self):
        return self.receiver_ID

    def load_next_frame(self):
        min_frame_generator = None
        min_frame_time = None
        for frame_generator in self.frame_generator_table:
            frame_time = frame_generator.get_current_frame_time()
            if frame_time is not None:
                if min_frame_time is None:
                    min_frame_generator = frame_generator
                    min_frame_time = frame_time
                elif frame_time < min_frame_time:
                    min_frame_generator = frame_generator
                    min_frame_time = frame_time
        if min_frame_time is not None:
            self.current_frame = min_frame_generator.get_current_frame()
            min_frame_generator.load_next_frame()
            self.next_frame_time = None
            for frame_generator in self.frame_generator_table:
                frame_time = frame_generator.get_current_frame_time()
                if self.next_frame_time is None:
                    self.next_frame_time = frame_time
                elif frame_time < self.next_frame_time:
                    self.next_frame_time = frame_time
        else:
            self.current_frame = None
            self.next_frame_time = None

    def get_dictionary(self):
        pass


class Frame_generator:

    def __init__(self):
        self.sender_ID = None
        self.receiver_ID = None
        self.label = None
        self.generation_start = None
        self.generation_end = None

    def set_sender_ID(self, sender_ID):
        self.sender_ID = sender_ID

    def set_receiver_ID(self, receiver_ID):
        self.receiver_ID = receiver_ID

    def set_label(self, label):
        self.label = label

    def set_generation_start(self, generation_start):
        self.generation_start = generation_start

    def set_generation_end(self, generation_end):
        self.generation_end = generation_end

    def verify_initialization(self):
        if self.sender_ID is None:
            print(f"{Fore.RED}No sender ID set for Frame_generator[Style.RESET_ALL}")
            assert(False)
        if self.receiver_ID is None:
            print(f"{Fore.RED}No receiver ID set for Frame_generator[Style.RESET_ALL}")
            assert(False)


class Frame_generator_CBR (Frame_generator):

    def __init__(self, frame_size, frame_interval):
        Frame_generator.__init__(self)
        self.frame_size = frame_size
        self.frame_interval = frame_interval
        self.current_frame = None
        self.current_frame_time = None

    def get_current_frame(self):
        pass

    def load_next_frame(self):
        Frame_generator.verify_initialization(self)
        pass

class Frame_generator_Poisson (Frame_generator):

    def __init__(self, frame_size, frame_interval):
        Frame_generator.__init__(self)
        pass


class Frame_generator_Hyperexponential (Frame_generator):

    def __init__(self):
        Frame_generator.__init__(self)


class Frame_generator_trace_file (Frame_generator):

    def __init__(self):
        Frame_generator.__init__(self)
        
