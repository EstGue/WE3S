from numpy import random

from WE3S.frame import *
from WE3S.timestamp import *



class Frame_generator:

    def __init__(self, sender_ID, receiver_ID, label):
        self.sender_ID = sender_ID
        self.receiver_ID = receiver_ID
        self.label = label
        self.priority = "LOW"

        self.next_frame_time = -1
        self.current_frame = None
        self.frame_counter = 0
        self.total_generated_data = 0

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
        self.frame_counter += 1
        self.total_generated_data += self.current_frame.size
    
    def get_dictionary(self):
        return {
            "Sender ID": self.sender_ID,
            "Destination ID": self.receiver_ID,
            "Label": self.label,
            "Frame counter": self.frame_counter,
            "Total generated data": self.total_generated_data
        }



class Constant_frame_generator (Frame_generator):

    def __init__(self, sender_ID, receiver_ID, label, frame_interval, frame_size):
        Frame_generator.__init__(self, sender_ID, receiver_ID, label)
        self.frame_interval = frame_interval
        self.frame_size = frame_size
        self.load_next_frame()

    def load_next_frame(self):
        if self.next_frame_time == -1:
            self.next_frame_time = Timestamp((random.randint(1, 100) / 100) * float(self.frame_interval))
        frame = Frame(self.next_frame_time, self.sender_ID, self.receiver_ID, self.label, self.priority, self.frame_size)
        self.current_frame = frame
        self.next_frame_time += self.frame_interval
        Frame_generator.load_next_frame(self)

    def get_dictionary(self):
        result = Frame_generator.get_dictionary(self)
        result["Frame size"] = self.frame_size
        result["Frame interval"] = self.frame_interval
        result["Type"] = "Constant"
        return result



class Poisson_frame_generator (Frame_generator):

    def __init__(self, sender_ID, receiver_ID, label, frame_interval, frame_size):
        Frame_generator.__init__(self, sender_ID, receiver_ID, label)
        self.frame_interval = frame_interval
        self.frame_size = frame_size
        self.load_next_frame()

    def load_next_frame(self):
        if self.next_frame_time == -1:
            self.next_frame_time = random.exponential(self.frame_interval, size=1)[0]
        frame = Frame(self.next_frame_time, self.sender_ID, self.receiver_ID, self.label, self.priority, self.frame_size)
        self.current_frame = frame
        self.next_frame_time += random.exponential(self.frame_interval, size=1)[0]
        Frame_generator.load_next_frame(self)

    def get_dictionary(self):
        result = Frame_generator.get_dictionary(self)
        result["Frame size"] = self.frame_size
        result["Frame interval"] = self.frame_interval
        result["Type"] = "Poisson"
        return result
        


class Hyperexponential_frame_generator (Frame_generator):

    def __init__(self, sender_ID, receiver_ID, label, frame_size, frame_interval_1, frame_interval_2, probability):
        Frame_generator.__init__(self, sender_ID, receiver_ID, label)
        self.frame_size = frame_size
        self.frame_interval_1 = frame_interval_1
        self.frame_interval_2 = frame_interval_2
        self.probability = probability
        self.load_next_frame()

    def load_next_frame(self):
        if self.next_frame_time == -1:
            if random.binomial(size=1, n=1, p=self.probability):
                self.next_frame_time = random.exponential(self.frame_interval_1, size=1)[0]
            else:
                self.next_frame_time = random.exponential(self.frame_interval_2, size=1)[0]
        frame = Frame(self.next_frame_time, self.sender_ID, self.receiver_ID, self.label, self.priority, self.frame_size)
        self.current_frame = frame
        if random.binomial(size=1, n=1, p=self.probability):
            self.next_frame_time += random.exponential(self.frame_interval_1, size=1)[0]
        else:
            self.next_frame_time += random.exponential(self.frame_interval_2, size=1)[0]
        Frame_generator.load_next_frame(self)

    def get_dictionary(self):
        result = Frame_generator.get_dictionary(self)
        result["Frame size"] = self.frame_size
        result["Frame interval 1"] = self.frame_interval_1
        result["Frame interval 2"] = self.frame_interval_2
        result["Probability"] = self.probability
        result["Type"] = "Hyperexponential"
        return result


class Frame_generator_from_trace_file (Frame_generator):

    def __init__(self, sender_ID, receiver_ID, label, trace_filename):
        Frame_generator.__init__(self, sender_ID, receiver_ID, label)
        self.trace_file = open(trace_filename, "r")
        self.time_offset = 0
        self.load_next_frame()

    def load_next_frame(self):
        line = self.trace_file.readline()
        if len(line) == 0:
            self.trace_file.seek(0)
            self.time_offset = self.get_current_frame_time()
            line = self.trace_file.readline()
        creation_time = Timestamp(self.time_offset + float(line.split(" ")[0]))
        size = int(line.split(" ")[1])
        label = line.split(" ")[2]
        self.current_frame = Frame(creation_time, self.sender_ID, self.receiver_ID, label, self.priority, size)
        Frame_generator.load_next_frame(self)

    def get_dictionary(self):
        result = Frame_generator.get_dictionary(self)
        result["Type"] = "Trace"
        return result


