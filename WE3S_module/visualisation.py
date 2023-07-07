class Visualisation:
    def __init__(self, scale=50*10**-6):
        self.timeline = ""
        self.timeline_current_time = 0
        self.scale = scale
        self.max_timeline_length = 200
        self.timeline_file = None

    def open_file(self, filename):
        self.timeline_file = open(filename, "a")
        self.timeline_file.write("\n")
        
    def add_for(self, duration, symbol):
        if duration < 0:
            duration = 0
        end_time = self.timeline_current_time + duration
        self.add_until(end_time, symbol)
                
    def add_until(self, end_time, symbol):
        while self.timeline_current_time <= end_time:
            self.write_timeline(symbol)
            self.timeline_current_time += self.scale

    def add_separation(self):
        self.write_timeline("|")

    def write_timeline(self, symbol):
        if self.timeline_file is not None:
            self.timeline_file.write(symbol)
        else:
            self.timeline += symbol
            self.timeline = self.timeline[-self.max_timeline_length:]

    def reset(self):
        self.timeline = ""
        self.timeline_current_time = 0
        # How to handle reset if wriiting in a file?
            
    def __str__(self):
        return self.timeline

    def __del__(self):
        if self.timeline_file is not None:
            self.timeline_file.close()
        # Close file
        # Delete other parameters
        pass
