from PIL import Image

class Overview_visualization:

    def __init__(self, step_ms, nb_STAs, simulation_duration):
        self.image = None
        self.step = step_ms * 10**-3
        self.current_step_start = 0
        self.nb_STAs = nb_STAs
        self.simulation_duration = simulation_duration
        self.record = []

        self.rect_width = 1 #px
        self.rect_height = 15 #px
        self.prepare_image()

        self.min_throughput = 0
        self.max_throughput = 100*10**6
        self.min_delay = 0
        self.max_delay = 1 * 10**-3
        self.min_collision = 0
        self.max_collision = 0.1

    def add_event(self, event):
        # The vent goes to the current step if it's start is within. (We do not look at its end)
        if event.start < self.current_step_start + self.step:
            self.record.append(event)
        else:
            self.draw_step()
            self.current_step_start += self.step
            self.record = [event]

    def prepare_image(self):
        # Gets the right size for the image (nb STAs, simulation duration).
        # Puts legends (if I have time)

        nb_metrics = 5 # Throughput UL / DL, delays UL/DL, collision rate

        image_vertical_size = (self.nb_STAs + 1) * ((nb_metrics + 1) * self.rect_height)
        image_horizontal_size = round((self.simulation_duration / self.step)) * self.rect_width
        

        self.image = Image.new('RGB', (image_horizontal_size, image_vertical_size))


    def show_image(self):
        self.image.save("/var/tmp/toto.png")
        self.image.show()
        
    def draw_step(self):
        # The record finished the current step, so the image can be updated with the new step.

        # First convert to dictionary to use the record module --> I will do it dirtly for now
        # events_dict = {str(i): self.record[i] for i in range(len(self.record))}

        UL_throughput_table = [0 for i in range(self.nb_STAs)]
        DL_throughput_table = [0 for i in range(self.nb_STAs)]
        UL_delay_table = [0 for i in range(self.nb_STAs)]
        nb_frames_UL_table = [0 for i in range(self.nb_STAs)]
        DL_delay_table = [0 for i in range(self.nb_STAs)]
        nb_frames_DL_table = [0 for i in range(self.nb_STAs)]
        collision_rate_table = [0 for i in range(self.nb_STAs)]

        AP_throughput = 0
        AP_delay = 0
        AP_frame = 0
        AP_collision_rate = 0

        for event in self.record:
            for frame in event.frames:
                if frame.label == "DL Tx":
                    receiver_ID = frame.receiver_ID - 1
                    AP_frame += 1
                    nb_frames_DL_table[receiver_ID] += 1
                    if not frame.has_collided and not frame.is_in_error:
                        DL_throughput_table[receiver_ID] += frame.length
                        AP_throughput += frame.length
                        DL_delay_table[receiver_ID] += (event.start - frame.creation_time)
                        AP_delay += (event.start - frame.creation_time)
                    elif frame.has_collided:
                        AP_collision_rate += 1
                elif frame.label == "UL Tx":
                    sender_ID = frame.sender_ID - 1
                    nb_frames_UL_table[sender_ID] += 1
                    if not frame.has_collided and not frame.is_in_error:
                        UL_throughput_table[sender_ID] += frame.length
                        UL_delay_table[sender_ID] += (event.start - frame.creation_time)
                    elif frame.has_collided:
                        collision_rate_table[sender_ID] += 1

        for i in range(self.nb_STAs):
            UL_throughput_table[i] /= self.step
            DL_throughput_table[i] /= self.step
            if nb_frames_UL_table[i] != 0:
                UL_delay_table[i] /= nb_frames_UL_table[i]
                collision_rate_table[i] /= nb_frames_UL_table[i]
            if nb_frames_DL_table[i] != 0:
                DL_delay_table[i] /= nb_frames_DL_table[i]
            AP_throughput /= self.step
            if AP_frame != 0:
                AP_delay /= AP_frame
                AP_collision_rate /= AP_frame

        # Drawing the squares at the right place, and at the right color
        # The x position is the same for everyone.
        x_position = round(self.current_step_start / self.step) * self.rect_width
        
        # AP: throughput
        y_position = 0
        value = self.compute_value_throughput(AP_throughput)
        for j in range(self.rect_width):
            for k in range(self.rect_height):
                self.image.putpixel((x_position+j, y_position+k), (value, 0, 0))
        # AP: delay
        y_position += self.rect_height
        value = self.compute_value_delay(AP_delay)
        for j in range(self.rect_width):
            for k in range(self.rect_height):
                self.image.putpixel((x_position+j, y_position+k), (0, value, 0))
        # AP: collision_rate
        y_position += self.rect_height
        value = self.compute_value_collision(AP_collision_rate)
        for j in range(self.rect_width):
            for k in range(self.rect_height):
                self.image.putpixel((x_position+j, y_position+k), (0, 0, value))

        for i in range(self.nb_STAs):
            # STA: UL throughput
            y_position += (self.rect_height * 2)
            value = self.compute_value_throughput(UL_throughput_table[i])
            for j in range(self.rect_width):
                for k in range(self.rect_height):
                    self.image.putpixel((x_position+j, y_position+k), (value, 0, 0))
            # STA: UL delay
            y_position += self.rect_height
            value = self.compute_value_delay(UL_delay_table[i])
            for j in range(self.rect_width):
                for k in range(self.rect_height):
                    self.image.putpixel((x_position+j, y_position+k), (0, value, 0))
            # STA: DL throughput
            y_position += self.rect_height
            value = self.compute_value_throughput(DL_throughput_table[i])
            for j in range(self.rect_width):
                for k in range(self.rect_height):
                    self.image.putpixel((x_position+j, y_position+k), (value, 0, 0))
            # STA: DL delay
            y_position += self.rect_height
            value = self.compute_value_delay(DL_delay_table[i])
            for j in range(self.rect_width):
                for k in range(self.rect_height):
                    self.image.putpixel((x_position+j, y_position+k), (0, value, 0))
            # STA: collision_rate
            y_position += self.rect_height
            value = self.compute_value_collision(collision_rate_table[i])
            for j in range(self.rect_width):
                for k in range(self.rect_height):
                    self.image.putpixel((x_position+j, y_position+k), (0, 0, value))
        

    def compute_value_throughput(self, throughput):
        assert(throughput >= 0)
        relative_score = 0
        if throughput >= self.max_throughput:
            relative_score = 1
        elif throughput <= self.min_throughput:
            relative_score = 0
        else:
            relative_score = (throughput - self.min_throughput) / (self.max_throughput - self.min_throughput)
        return round(relative_score * 255)

    def compute_value_delay(self, delay):
        print(delay)
        assert(delay >= 0)
        relative_score = 0
        if delay <= self.min_delay:
            relative_score = 1
        elif delay >= self.max_delay:
            relative_score = 0
        else:
            relative_score = (self.max_delay - delay) / (self.max_delay - self.min_delay)
        return round(relative_score * 255)

    def compute_value_collision(self, collision):
        assert(collision >= 0 and collision <=1)
        relative_score = 0
        if collision <= self.min_collision:
            relative_score = 1
        elif collision >= self.max_collision:
            relative_score = 0
        else:
            relative_score = (self.max_collision - collision) / (self.max_collision - self.min_collision)
        return round(relative_score * 255)
