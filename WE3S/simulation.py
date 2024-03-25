import time
import os
from datetime import datetime

from WE3S.event_handler import *
from WE3S.record import *
from WE3S.overview_visualization import *

class Simulation():

    def __init__(self):
        self.event_handler = Event_handler()
        self.simulation_duration = 1 #s
        self.chrono_start = 0
        self.chrono_end = 0
        self.overview_visualization = None


## SET SIMULATION PARAMETERS

    def set_nb_STAs(self, nb_STAs):
        assert(nb_STAs >= 0)
        self.event_handler.set_nb_STAs(nb_STAs)

    # Possible traffic types:
    # "Constant" -> needs "Frame size", "Frame interval"
    # "Poisson" -> needs "Frame size", "Frame interval"
    # "Hyperexponential" -> needs "Frame size", "Frame interval 1", "Frame interval 2", "Probability"
    # "Trace" -> "Trace filename"
    def add_DL_traffic(self, STA_ID, traffic_type, arg_dict, label="DL Tx", start=None, end=None):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        self.event_handler.add_DL_traffic(STA_ID, traffic_type, arg_dict, label, start, end)

    # See set_DL_traffic to get possible traffic types.
    def add_UL_traffic(self, STA_ID, traffic_type, arg_dict, label="UL Tx", start=None, end=None):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        self.event_handler.add_UL_traffic(STA_ID, traffic_type, arg_dict, label, start, end)

    def set_link_capacity(self, STA_ID, link_capacity):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        assert(link_capacity > 0)
        self.event_handler.set_link_capacity(STA_ID, link_capacity)

    def set_buffer_capacity_AP(self, buffer_capacity):
        assert(buffer_capacity > 0)
        self.event_handler.set_buffer_capacity_AP(buffer_capacity)

    def set_buffer_capacity_STA(self, STA_ID, buffer_capacity):
        assert(STA_ID > 0)
        assert(buffer_capacity > 0)
        self.event_handler.set_buffer_capacity_STA(STA_ID, buffer_capacity)

    # Possible slot type:
    # "Static" -> Needs "First start" (float), "Duration" (float), "Interval" (float)
    # "Dynamic" -> Needs "Start" (table of float), "Duration" (table of float)
    def initialize_DL_slot(self, STA_ID, slot_type, arg_dict):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        self.event_handler.initialize_DL_slot(STA_ID, slot_type, arg_dict)

    # Possible prompt strategies:
    # "None" -> Needs "Prompt interval", optionally "First prompt"
    # "AIMD" -> Needs "Min prompt interval", "Max prompt interval", "Prompt interval incrementation step",
    # "Objective nb returned frames", "Max nb returned frames"
    def initialize_DL_prompt(self, STA_ID, strategy_name, arg_dict):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        self.event_handler.initialize_DL_prompt(STA_ID, strategy_name, arg_dict)

    def initialize_UL_slot(self, STA_ID, first_start, duration, interval):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        assert(duration < interval)
        assert(first_start < interval)
        self.event_handler.initialize_UL_slot(STA_ID, first_start, duration, interval)

    def initialize_UL_prompt(self, STA_ID, strategy_name, arg_dict):
        assert(STA_ID > 0 and STA_ID <= len(self.event_handler.contenders))
        self.event_handler.initialize_UL_prompt(STA_ID, strategy_name, arg_dict)

    def disable_random_error_on_frame(self):
        self.event_handler.disable_random_error_on_frame()


    def read_spec_from_dict(self, spec_dict):
        self.simulation_duration = spec_dict["Simulation duration"]
        if not spec_dict["Random channel error"]:
            self.disable_channel_error()
        self.set_buffer_capacity_AP(spec_dict["AP buffer capacity"])
        self.set_nb_STAs(spec_dict["Nb STAs"])
        for sta in spec_dict["STAs"]:
            STA_ID = int(sta)
            sta_dict = spec_dict["STAs"][sta]
            self.set_link_capacity(STA_ID, sta_dict["Datarate"])
            for traffic in sta_dict["DL traffic"]:
                traffic_dict = sta_dict["DL traffic"][traffic]
                traffic_type = traffic_dict["Type"]
                traffic_start = None
                if "Start" in traffic_dict:
                    traffic_start = traffic_dict["Start"]
                traffic_end = None
                if "End" in traffic_dict:
                    traffic_end = traffic_dict["End"]
                self.add_DL_traffic(STA_ID, traffic_type, traffic_dict,
                                    traffic, traffic_start, traffic_end)
            for traffic in sta_dict["UL traffic"]:
                traffic_dict = sta_dict["UL traffic"][traffic]
                traffic_type = traffic_dict["Type"]
                traffic_start = None
                if "Start" in traffic_dict:
                    traffic_start = traffic_dict["Start"]
                traffic_end = None
                if "End" in traffic_dict:
                    traffic_end = traffic_dict["End"]
                self.add_UL_traffic(STA_ID, traffic_type, traffic_dict,
                                    traffic, traffic_start, traffic_end)
            self.set_buffer_capacity_STA(STA_ID, sta_dict["Buffer capacity"])
            if sta_dict["Use DL slot"]:
                start = sta_dict["DL slot"]["Start"]
                duration = sta_dict["DL slot"]["Duration"]
                interval = sta_dict["DL slot"]["Interval"]
                arg_dict = {"First start": start, "Duration": duration, "Interval": interval}
                self.initialize_DL_slot(STA_ID, "Static", arg_dict)
            if sta_dict["Use DL prompt"]:
                strategy_name = sta_dict["DL prompt"]["Strategy name"]
                arg_dict = sta_dict["DL prompt"]
                self.initialize_DL_prompt(STA_ID, strategy_name, arg_dict)
            if sta_dict["Use UL slot"]:
                start = sta_dict["UL slot"]["Start"]
                duration = sta_dict["UL slot"]["Duration"]
                interval = sta_dict["UL slot"]["Interval"]
                arg_dict = {"First start": start, "Duration": duration, "Interval": interval}
                self.initialize_UL_slot(STA_ID, start, duration, interval)
            if sta_dict["Use UL prompt"]:
                strategy_name = sta_dict["UL prompt"]["Strategy name"]
                arg_dict = sta_dict["UL prompt"]
                self.initialize_UL_prompt(STA_ID, strategy_name, arg_dict)

    def get_nb_STAs(self):
        return len(self.event_handler.contenders)-1

    def get_DL_frame_frequency(self, STA_ID):
        return self.event_handler.contenders[STA_ID].DL_frame_generator.frame_frequency
    
    def get_UL_frame_frequency(self, STA_ID):
        return self.event_handler.contenders[STA_ID].UL_frame_generator.frame_frequency
        
        
## RUN SIMULATION
    

    def run_simulation(self):
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
        for contender in self.event_handler.contenders:
            contender.initialize()
        # self.overview_visualization = Overview_visualization(0.5, len(self.event_handler.contenders)-1, self.simulation_duration)
        self.chrono_start = time.time()
        while self.event_handler.current_time < self.simulation_duration:
            print(f"{Fore.BLUE}\t\t--- Current time: ", self.event_handler.current_time, f" ---{Style.RESET_ALL}")
            self.event_handler.retrieve_events()
            tot_doze = Timestamp(0)
            for i, event in enumerate(self.event_handler.events):
                print("\tID: ", event.get_sender_ID(), "  |  Event: ", event, "  |  Frames: ", len(event.frame_table))
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
                mean_doze = float(tot_doze) / ((len(self.event_handler.contenders) - 1) * float(self.event_handler.current_time))
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

    # def get_record(self):
    #     result_AP = self.event_handler.contenders[0].get_dictionary()
    #     result_STA = dict()
    #     for contender in self.event_handler.contenders[1:]:
    #         result_STA["STA " + str(contender.ID)] = contender.get_dictionary()
    #     result_events = self.event_handler.record.get_dictionary()
    #     result = {
    #         "AP": result_AP,
    #         "STAs": result_STA,
    #         "Events": result_events
    #     }
    #     return result

    def get_record(self):
        return self.event_handler.get_record()

    def print_timeline(self):
        self.event_handler.print_timeline()

    
