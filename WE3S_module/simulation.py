import json
import time
import os
from datetime import datetime

from event_handler import *
from record import *
from overview_visualization import *

class Simulation():

    def __init__(self):
        self.event_handler = Event_handler()
        self.simulation_duration = 400 #s
        self.chrono_start = 0
        self.chrono_end = 0
        self.overview_visualization = None


## SET SIMULATION PARAMETERS
        
    def set_nb_STAs(self, nb_STAs):
        assert(nb_STAs >= 0)
        self.event_handler.set_nb_STAs(nb_STAs)

    def set_DL_throughput(self, STA_ID, throughput, is_interval_random=True):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        assert(throughput > 0)
        self.event_handler.set_DL_throughput(STA_ID, throughput, is_interval_random)

    def set_UL_throughput(self, STA_ID, throughput, is_interval_random=True):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        assert(throughput > 0)
        self.event_handler.set_UL_throughput(STA_ID, throughput, is_interval_random)

    def set_link_capacity(self, STA_ID, link_capacity):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        assert(link_capacity > 0)
        self.event_handler.set_link_capacity(STA_ID, link_capacity)

    def set_buffer_size_AP(self, buffer_size):
        assert(buffer_size > 0)
        self.event_handler.set_buffer_size_AP(buffer_size)

    def set_buffer_size_STA(self, STA_ID, buffer_size):
        assert(STA_ID > 0)
        assert(buffer_size > 0)
        self.event_handler.set_buffer_size_STA(STA_ID, buffer_size)

    def toggle_DL_slot(self, STA_ID, first_start, duration, interval):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        assert(duration < interval)
        assert(first_start < interval)
        self.event_handler.toggle_DL_slot(STA_ID, first_start, duration, interval)

    def toggle_DL_prompt(self, STA_ID, prompt_interval):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        assert(prompt_interval > 0)
        self.event_handler.toggle_DL_prompt(STA_ID, prompt_interval)

    def toggle_UL_slot(self, STA_ID, first_start, duration, interval):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        assert(duration < interval)
        assert(first_start < interval)
        self.event_handler.toggle_UL_slot(STA_ID, first_start, duration, interval)

    def toggle_UL_prompt(self, STA_ID, prompt_interval):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        assert(prompt_interval > 0)
        self.event_handler.toggle_UL_prompt(STA_ID, prompt_interval)
    
    def deactivate_random_error_on_frame(self):
        self.event_handler.deactivate_random_error_on_frame()
        


    def get_nb_STAs(self):
        return len(self.event_handler.contenders)-1

    def get_DL_frame_frequency(self, STA_ID):
        return self.event_handler.contenders[STA_ID].DL_frame_generator.frame_frequency
    
    def get_UL_frame_frequency(self, STA_ID):
        return self.event_handler.contenders[STA_ID].UL_frame_generator.frame_frequency
        
        
## RUN SIMULATION
    

    def run_simulation(self):
        self.verify_simulation_parameters()
        for contender in self.event_handler.contenders:
            contender.initialize()
        self.chrono_start = time.time()
        loop_number = 0
        retrieve_time = 0
        elect_time = 0
        inform_time = 0
        loop_start = time.time()
        while self.event_handler.current_time < self.simulation_duration:
            retrieve_start = time.time()
            self.event_handler.retrieve_events()
            retrieve_end = time.time()
            elect_start = time.time()
            self.event_handler.elect_next_event()
            elect_end = time.time()
            inform_start = time.time()
            self.event_handler.inform_contenders()
            inform_end = time.time()
            loop_number += 1
            retrieve_time += retrieve_end - retrieve_start
            elect_time += elect_end - elect_start
            inform_time += inform_end - inform_start
        self.chrono_end = time.time()


    def run_simulation_debug(self):
        self.verify_simulation_parameters()
        for contender in self.event_handler.contenders:
            contender.initialize()
        # self.overview_visualization = Overview_visualization(0.5, len(self.event_handler.contenders)-1, self.simulation_duration)
        self.chrono_start = time.time()
        while self.event_handler.current_time < self.simulation_duration:
            print(f"{Fore.BLUE}\t\t--- Current time: ", self.event_handler.current_time, f" ---{Style.RESET_ALL}")
            self.event_handler.retrieve_events()
            tot_doze = 0
            for i, event in enumerate(self.event_handler.events):
                print("\tID: ", event.get_sender_ID(), "  |  Event: ", event, "  |  Frames: ", len(event.frames))
                contender = self.event_handler.contenders[i]
                print("\t            Backoff: ", contender.backoff, " out of 1 -", contender.contention_window)
                print("\t            Waiting time: ", event.start - self.event_handler.current_time)
                tot_doze += contender.state_counter.doze
            self.event_handler.elect_next_event()
            # self.overview_visualization.add_event(self.event_handler.next_event)
            print(f"\t\tNext event: {Fore.BLUE}", self.event_handler.next_event, end=f"{Style.RESET_ALL}\t")
            print("EOSP? ", self.event_handler.next_event.is_EOSP())
            print("\t\tCollision? ", self.event_handler.next_event.is_collision(), end="\t")
            print("Error? ", self.event_handler.next_event.is_error())
            if len(self.event_handler.contenders) > 1:
                mean_doze = tot_doze / ((len(self.event_handler.contenders) - 1) * self.event_handler.current_time)
                print(f"{Fore.RED}\t\tMean doze time: ", mean_doze, f"{Style.RESET_ALL}")
            self.event_handler.inform_contenders()
            self.print_timeline()
            print("___________________________________________________________________________________________________________________________________________________________________________________________________________")
        print("\n")
        self.chrono_end = time.time()
        # self.overview_visualization.show_image()


## GET RESULTS

    def get_chrono(self):
        return self.chrono_end - self.chrono_start
        
    def get_report(self):
        result_STA = dict()
        for contender in self.event_handler.contenders[1:]:
            result_STA[str(contender.ID)] = contender.get_dictionary()
        result_events = self.event_handler.record.get_dictionary()
        result = {
            "STAs": result_STA,
            "Events": result_events
        }
        return result

    def write_report(self, repertory_name, file_name):
        report = self.get_report()
        f = open(os.path.join(repertory_name, file_name), "w")
        f.write(json.dumps(report, indent=4))
        f.close()

    def print_timeline(self):
        self.event_handler.print_timeline()

    

## VERIFY PARAMETERS

    def verify_simulation_parameters(self):
        pass
