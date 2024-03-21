from numpy import random

from WE3S.frame import *
from WE3S.timestamp import *



class Aggregated_frame_generator:

    def __init__(self, sender_ID, receiver_ID, priority="LOW"):
        self.sender_ID = sender_ID
        self.receiver_ID = receiver_ID
        self.priority = priority

        self.generator_table = []
        self.current_index = None
        self.next_index = None

    def add_frame_generator(self, label, traffic_type, arg_dict, start, end):
        generator = None
        if traffic_type == "CBR":
            generator = Frame_generator_CBR(label, arg_dict, start, end)
        elif traffic_type == "Poisson":
            generator = Frame_generator_Poisson(label, arg_dict, start, end)
        elif traffic_type == "Hyperexponential":
            generator = Frame_generator_hyperexponential(label, arg_dict, start, end)
        elif traffic_type == "Trace":
            generator = Frame_generator_trace(label, arg_dict, start, end)
        else:
            print(f"{Fore.RED}Unrecognized traffic type")
            print("Possible traffic type: CBR, Poisson, Hyperexponential, Trace")
            print("Given traffic type:", traffic_type)
            print(f"{Style.RESET_ALL}")
            assert(False)

        if generator is not None:
            self.generator_table.append(generator)
        else:
            print(f"{Fore.RED}The generator should not be null here{Style.RESET_ALL}")
            assert(False)

        self.init_first_frame()
            

    def get_current_frame(self):
        if self.current_index == -1:
            return None
        frame = self.generator_table[self.current_index].get_current_frame()
        frame.sender_ID = self.sender_ID
        frame.receiver_ID = self.receiver_ID
        frame.priority = self.priority
        return frame

    def get_current_frame_time(self):
        if self.current_index == -1:
            return -1
        return self.generator_table[self.current_index].get_current_frame_time()

    def get_next_frame_time(self):
        if self.current_index == self.next_index:
            return self.generator_table[next_frame_generator_index].get_next_frame_time()
        else:
            return self.generator_table[self.next_index].get_current_frame_time()

    def init_first_frame(self):
        time_table = []
        reducted_time_table = []
        for i in range(len(self.generator_table)):
            time = self.generator_table[i].get_current_frame_time()
            time_table.append(time)
            if time > 0:
                reducted_time_table.append(time)

        if len(reducted_time_table) == 0:
            self.current_index = -1
            self.next_index = -1
        else:
            current_frame_time = min(reducted_time_table)
            self.current_index = time_table.index(current_frame_time)
            updated_time = self.generator_table[self.current_index].get_next_frame_time()
            time_table[self.current_index] = updated_time
            reducted_time_table.remove(current_frame_time)
            if updated_time > 0:
                reducted_time_table.append(updated_time)
            if len(reducted_time_table) == 0:
                self.next_index = -1
            else:
                next_frame_time = min(reducted_time_table)
                self.next_index = time_table.index(next_frame_time)
            
        
    
    def load_next_frame(self):
        if self.current_index == -1:
            return
        self.generator_table[self.current_index].load_next_frame()
        self.current_index = self.next_index
        if self.current_index == -1:
            return
        current_index = self.current_index

        time_table = []
        for i in range(len(self.generator_table)):
            time = 0
            if i == current_index:
                time = self.generator_table[i].get_next_frame_time()
            else:
                time = self.generator_table[i].get_current_frame_time()
            time_table.append(time)

        reducted_time_table = [i for i in time_table if i>0]
        if len(reducted_time_table) == 0:
            self.next_index = -1
        else:
            next_frame_time = min(reducted_time_table)
            self.next_index = time_table.index(next_frame_time)

    def get_frame_counter(self):
        res = 0
        for gen in self.generator_table:
            res += gen.frame_counter
        return res

    def get_total_generated_data(self):
        res = 0
        for gen in self.generator_table:
            res += gen.total_generated_data
        return res

    def get_dictionary(self):
        return {
            "Sender ID": self.sender_ID,
            "Destination ID": self.receiver_ID,
            "Frame counter": self.get_frame_counter(),
            "Total generated data": self.get_total_generated_data()
        }


        
class Frame_generator_CBR:

    def __init__(self, label, arg_dict, start, end):
        self.label = label
        
        assert("Frame size" in arg_dict)
        self.frame_size = arg_dict["Frame size"]
        assert("Frame interval" in arg_dict)
        self.frame_interval = arg_dict["Frame interval"]
        if "First frame time" in arg_dict:
            self.first_frame_time = arg_dict["First frame time"]
        else:            
            self.first_frame_time = Timestamp((random.randint(1, 100) / 100) * float(self.frame_interval))

        if start is not None and end is not None:
            assert(start < end)
        self.generation_start = start
        self.generation_end = end

        self.current_frame = None
        self.next_frame_time = None

        self.frame_counter = 0
        self.total_generated_data = 0
        self.init_first_frame()

    def get_current_frame(self):
        if self.label != "beacon":
            print("Current frame", self.current_frame)
        return self.current_frame

    def get_current_frame_time(self):
        if self.current_frame is not None:
            return self.current_frame.creation_time
        else:
            return -1

    def get_next_frame_time(self):
        return self.next_frame_time
        
    def load_next_frame(self):
        assert(self.next_frame_time is not None)
        if self.next_frame_time == -1:
            self.current_frame = None
        else:
            self.current_frame = Frame(self.next_frame_time, None, None,
                                       self.label, None, self.frame_size)
            self.frame_counter += 1
            self.total_generated_data += self.frame_size
            self.next_frame_time += self.frame_interval
            if self.generation_end is not None and self.next_frame_time > self.generation_end:
                self.next_frame_time = -1

    def init_first_frame(self):
        current_frame_time = self.first_frame_time
        if self.generation_start is not None:
            while current_frame_time < self.generation_start:
                current_frame_time += self.frame_interval

        if self.generation_end is not None and current_frame_time > self.generation_end:
            self.current_frame = None
            self.next_frame_time = -1
        else:
            self.current_frame = Frame(current_frame_time, None, None,
                                       self.label, None, self.frame_size)
            self.frame_counter += 1
            self.total_generated_data += self.frame_size
            self.next_frame_time = current_frame_time + self.frame_interval
            if self.generation_end is not None and self.next_frame_time > self.generation_end:
                self.next_frame_time = -1
            

# class Frame_generator_Poisson:
    
