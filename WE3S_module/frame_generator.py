from frame import *

from numpy import random

class Frame_generator:
    def __init__(self, throughput, frame_length, sender_ID, destination_ID, label, is_interval_random = True):
        self.sender_ID = sender_ID
        self.destination_ID = destination_ID
        self.label = label
        self.priority = "LOW"

        self.throughput = throughput
        self.frame_length = frame_length
        self.frame_frequency = self.throughput / self.frame_length
        self.is_interval_random = is_interval_random

        self.frame_counter = 0
        self.current_frame_time = 0
        self.next_frame_time = 0
        self.load_next_frame()
        self.load_next_frame()

    def get_current_frame_time(self):
        return self.current_frame_time

    def get_next_frame_time(self):
        return self.next_frame_time
    
    def load_next_frame(self):
        self.current_frame_time = self.next_frame_time
        interval = [0]
        if self.is_interval_random:
            interval = random.exponential(1 / self.frame_frequency, size=1)
        else:
            interval[0] = 1 / self.frame_frequency
        assert(interval[0] > 0)
        self.next_frame_time += interval[0]
        self.frame_counter += 1

    def get_frame(self):
        frame = Frame(self.current_frame_time, self.sender_ID, self.destination_ID, self.label, self.priority, self.frame_length)
        return frame
    
    def get_STA_ID(self):
        return self.STA_ID

    def get_datasize(self):
        return self.frame_length

    def set_throughput(self, throughput):
        self.throughput = throughput
        self.frame_frequency = self.throughput / self.frame_length
        self.current_frame_time = 0
        self.next_frame_time = 0
        self.load_next_frame()
        self.load_next_frame()
    
    def set_frequency(self, frequency):
        self.frame_frequency = frequency
        self.throughput = self.frame_length * self.frame_frequency
        self.current_frame_time = 0
        self.next_frame_time = 0
        self.load_next_frame()
        self.load_next_frame()

    def get_dictionary(self):
        result = {
            "Sender ID" : self.sender_ID,
            "Destination ID" : self.destination_ID,
            "Label" : self.label,
            "Priority" : self.priority,
            "Throughput": self.throughput,
            "Frame length": self.frame_length,
            "Random interval" : self.is_interval_random,
            "Frame counter" : self.frame_counter
        }
        return result
