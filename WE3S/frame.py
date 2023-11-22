from WE3S.timestamp import *

frame_ID = 0

class Frame:
    
    def __init__(self, creation_time, sender_ID, receiver_ID, label, priority, size = 1440*8):
        global frame_ID

        self.ID = frame_ID
        frame_ID += 1
        
        self.creation_time = Timestamp(creation_time)
        self.sender_ID = sender_ID
        self.receiver_ID = receiver_ID
        self.size = size
        self.label = label.replace('\n', '')
        self.priority = priority

        self.nb_of_transmissions = 0

        self.has_collided = False
        self.is_in_error = False
        self.EOSP = False
        

    def get_dictionary(self):
        result = {
            "ID": self.ID,
            "Creation time" : float(self.creation_time),
            "Sender ID" : self.sender_ID,
            "Receiver ID" : self.receiver_ID,
            "Size" : self.size,
            "Label" : self.label,
            "Priority" : self.priority,
            "Collision" : self.has_collided,
            "Error" : self.is_in_error,
            "Number of transmissions" : self.nb_of_transmissions
        }
        return result
        
    def copy(self):
        frame_copy = Frame(self.creation_time, self.sender_ID, self.receiver_ID, self.label, self.priority, self.size)
        frame_copy.has_collided = self.has_collided
        frame_copy.is_in_error = self.is_in_error
        return frame_copy
    
    def __eq__(self, frame):
        return self.ID == frame.ID

    def __str__(self):
        return self.get_dictionary().__str__()
