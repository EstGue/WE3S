from numpy import random

from WE3S.frame import *
from WE3S.timestamp import *

class Frame_generator:
    def __init__(self, throughput, frame_size, sender_ID, destination_ID, label, is_interval_random = True):
        self.sender_ID = sender_ID
        self.destination_ID = destination_ID
        self.label = label
        self.priority = "LOW"

        self.throughput = throughput
        self.frame_size = frame_size
        self.frame_frequency = self.throughput / self.frame_size
        self.is_interval_random = is_interval_random

        self.frame_counter = 0
        self.current_frame_time = Timestamp()
        self.next_frame_time = Timestamp()
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
        frame = Frame(self.current_frame_time, self.sender_ID, self.destination_ID, self.label, self.priority, self.frame_size)
        return frame
    
    def get_STA_ID(self):
        return self.STA_ID

    def get_datasize(self):
        return self.frame_size

    def set_throughput(self, throughput):
        self.throughput = throughput
        self.frame_frequency = self.throughput / self.frame_size
        self.current_frame_time = Timestamp()
        self.next_frame_time = Timestamp()
        self.load_next_frame()
        self.load_next_frame()
    
    def set_frequency(self, frequency):
        self.frame_frequency = frequency
        self.throughput = self.frame_size * self.frame_frequency
        self.current_frame_time = Timestamp()
        self.next_frame_time = Timestamp()
        self.load_next_frame()
        self.load_next_frame()

    def set_frame_size(self, frame_size):
        # Keeps the thoughput, changes the frame frequency
        self.frame_size = frame_size
        self.frequency = self.throughput / self.frame_size
        self.current_frame_time = Timestamp()
        self.next_frame_time = Timestamp()
        self.load_next_frame()
        self.load_next_frame()
        
    def get_dictionary(self):
        result = {
            "Sender ID" : self.sender_ID,
            "Destination ID" : self.destination_ID,
            "Label" : self.label,
            "Priority" : self.priority,
            "Throughput": self.throughput,
            "Frame size": self.frame_size,
            "Random interval" : self.is_interval_random,
            "Frame counter" : self.frame_counter
        }
        return result
