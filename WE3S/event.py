from colorama import Fore
from colorama import Style

from WE3S.timestamp import *

event_ID = 0

class Event:
    def __init__(self, start, duration, frame_table):
        global event_ID
        self.ID = event_ID
        event_ID += 1
        self.start = Timestamp(start)
        self.duration = Timestamp(duration)
        self.end = self.start + self.duration
        self.frame_table = frame_table

    def is_before(self, other_event):
        return (self.start < other_event.start)

    def set_start(self, start):
        self.start = Timestamp(start)
        self.end = self.start + self.duration

    def set_duration(self, duration):
        self.duration = Timestamp(duration)
        self.end = self.start + self.duration

    def set_sender_ID(self, STA_ID):
        for frame in self.frame_table:
            frame.sender_ID = STA_ID

    def set_receiver_ID(self, STA_ID):
        for frame in self.frame_table:
            frame.receiver_ID = STA_ID

    def is_collision(self):
        if len(self.frame_table) > 0:
            for frame in self.frame_table:
                if frame.has_collided:
                    return True
        return False

    def is_error(self):
        # TODO: Needs refinements! Currently returns True only if every frames is in error.
        if len(self.frame_table) > 0:
            for frame in self.frame_table:
                if not frame.is_in_error:
                    return False
            return True
        return False

    def is_beacon(self):
        if len(self.frame_table) == 0:
            return False
        if self.frame_table[0].label == "beacon":
            assert(len(self.frame_table) == 1 or self.frame_table[0].has_collided)
            if not self.frame_table[0].has_collided and not self.frame_table[0].is_in_error:
                return True
        return False

    def is_DL_prompt(self):
        if len(self.frame_table) == 0:
            return False
        if self.frame_table[0].label == "DL_prompt":
            assert(len(self.frame_table) == 1 or self.frame_table[0].has_collided)
            if not self.frame_table[0].has_collided and not self.frame_table[0].is_in_error:
                return True
        return False

    def is_ACK(self):
        if len(self.frame_table) == 0:
            return False
        if self.frame_table[0].label == "ACK":
            assert(len(self.frame_table) == 1 or self.frame_table[0].has_collided)
            if not self.frame_table[0].has_collided and not self.frame_table[0].is_in_error:
                return True
        return False

    def is_EOSP(self):
        if len(self.frame_table) == 0:
            return False
        error = False
        flag_EOSP = False
        for frame in self.frame_table:
            if frame.has_collided or frame.is_in_error:
                error = True
            if frame.EOSP:
                flag_EOSP = True
        return flag_EOSP and not error
    

    def get_datasize(self):
        datasize = 0
        for frame in self.frame_table:
            datasize += frame.size
        return datasize

    def is_sender(self, STA_ID):
        if self.frame_table == []:
            return False
        for frame in self.frame_table:
            if frame.sender_ID == STA_ID:
                return True
        return False

    def get_sender_ID(self):
        assert(self.frame_table is not None)
        return self.frame_table[0].sender_ID
    
    def is_receiver(self, STA_ID):
        if len(self.frame_table) == 0:
            return False
        for frame in self.frame_table:
            if frame.receiver_ID == STA_ID:
                return True
        return False            
    
    def get_dictionary(self):
        result = {
            "ID": self.ID,
            "Start": float(self.start),
            "Duration": float(self.duration),
            "End": float(self.end),
        }
        frames_dictionary = dict()
        for i,frame in enumerate(self.frame_table):
            frames_dictionary["Frame" + str(i)] = frame.get_dictionary()
        result["Frames"] = frames_dictionary
        return result

    def copy(self):
        event_copy = Event(self.start, self.duration, [])
        if self.frame_table is not None:
            for frame in self.frame_table:
                event_copy.frame_table.append(frame.copy())
        return event_copy
        
    
    def __str__(self):
        result = str(self.ID)
        if len(self.frame_table) > 0:
            result += " " + self.frame_table[0].label
            if not self.is_collision():
                if self.frame_table[0].label == "DL Tx":
                    result += " to " + str(self.frame_table[0].receiver_ID)
                elif self.frame_table[0].label == "UL Tx":
                    result += " from " + str(self.frame_table[0].sender_ID)
        result += " ; start=" + str(self.start)
        result += " ; end=" + str(self.end)
        return result


    def __eq__(self, event):
        return self.ID == event.ID



