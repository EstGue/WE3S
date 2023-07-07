from colorama import Fore
from colorama import Style


event_ID = 0

class Event:
    def __init__(self, start, duration, frame):
        global event_ID
        self.ID = event_ID
        event_ID += 1
        self.start = start
        self.duration = duration
        self.end = self.start + self.duration
        self.frames = []
        if frame is not None:
            self.frames.append(frame)

    def is_before(self, other_event):
        return (self.start < other_event.start)

    def set_start(self, start):
        self.start = start
        self.end = self.start + self.duration

    def set_duration(self, duration):
        self.duration = duration
        self.end = self.start + self.duration

    def set_sender_ID(self, STA_ID):
        for frame in self.frames:
            frame.sender_ID = STA_ID

    def set_receiver_ID(self, STA_ID):
        for frame in self.frames:
            frame.receiver_ID = STA_ID

    def is_collision(self):
        if len(self.frames) > 0:
            for frame in self.frames:
                if frame.has_collided:
                    return True
        return False

    def is_error(self):
        # TODO: Needs refinements! Currently returns True only if every frames is in error.
        if len(self.frames) > 0:
            for frame in self.frames:
                if not frame.is_in_error:
                    return False
            return True
        return False

    def is_beacon(self):
        if len(self.frames) == 0:
            return False
        if self.frames[0].label == "beacon":
            assert(len(self.frames) == 1 or self.frames[0].has_collided)
            if not self.frames[0].has_collided and not self.frames[0].is_in_error:
                return True
        return False

    def is_DL_prompt(self):
        if len(self.frames) == 0:
            return False
        if self.frames[0].label == "DL_prompt":
            assert(len(self.frames) == 1 or self.frames[0].has_collided)
            if not self.frames[0].has_collided and not self.frames[0].is_in_error:
                return True
        return False

    def is_ACK(self):
        if len(self.frames) == 0:
            return False
        if self.frames[0].label == "ACK":
            assert(len(self.frames) == 1 or self.frames[0].has_collided)
            if not self.frames[0].has_collided and not self.frames[0].is_in_error:
                return True
        return False

    def is_EOSP(self):
        if len(self.frames) == 0:
            return False
        error = False
        flag_EOSP = False
        for frame in self.frames:
            if frame.has_collided or frame.is_in_error:
                error = True
            if frame.EOSP:
                flag_EOSP = True
        return flag_EOSP and not error
    

    def get_datasize(self):
        datasize = 0
        for frame in self.frames:
            datasize += frame.length
        return datasize

    def is_sender(self, STA_ID):
        if self.frames == []:
            return False
        for frame in self.frames:
            if frame.sender_ID == STA_ID:
                return True
        return False

    def get_sender_ID(self):
        assert(self.frames is not None)
        return self.frames[0].sender_ID
    
    def is_receiver(self, STA_ID):
        if len(self.frames) == 0:
            return False
        for frame in self.frames:
            if frame.receiver_ID == STA_ID:
                return True
        return False            
    
    def get_dictionary(self):
        result = {
            "ID": self.ID,
            "Start": self.start,
            "Duration": self.duration,
            "End": self.end,
        }
        frames_dictionary = dict()
        for i,frame in enumerate(self.frames):
            frames_dictionary["Frame" + str(i)] = frame.get_dictionary()
        result["Frames"] = frames_dictionary
        return result

    def copy(self):
        event_copy = Event(self.start, self.duration, None)
        for frame in self.frames:
            event_copy.frames.append(frame.copy())
        return event_copy
        
    
    def __str__(self):
        result = str(self.ID)
        if len(self.frames) > 0:
            result += " " + self.frames[0].label
            if not self.is_collision():
                if self.frames[0].label == "DL Tx":
                    result += " to " + str(self.frames[0].receiver_ID)
                elif self.frames[0].label == "UL Tx":
                    result += " from " + str(self.frames[0].sender_ID)
        result += " ; start=" + str(float("{:.4f}".format(self.start)))
        result += " ; end=" + str(float("{:.4f}".format(self.end)))
        return result


    def __eq__(self, event):
        return self.ID == event.ID



