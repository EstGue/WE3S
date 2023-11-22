import os
from sortedcontainers import SortedSet

from .common_parameters import *

class Results():
    def __init__(self, record_data):
        self.record_data = record_data
        self.last_key = list(record_data["Events"].keys())[-1]

        self.simulation_duration = -1
        self.nb_events = -1
        self.nb_STAs = -1
        
        ## THEORITICAL RESULTS: what was supposed to happen?
        self.th_busy_time_medium = -1
        
        self.th_busy_time_STA = []
        self.th_busy_time_avg = -1
        self.th_busy_time_std = -1

        self.th_DL_throughput_STA = []
        self.th_DL_throughput_avg = -1
        self.th_DL_throughput_std = -1
        
        self.th_UL_throughput_STA = []
        self.th_UL_throughput_avg = -1
        self.th_UL_throughput_std = -1

        self.th_tot_throughput_STA = []
        self.th_tot_throughput_avg = -1
        self.th_tot_throughput_std = -1

        self.datarate_STA = []
        self.datarate_avg = -1
        self.datarate_std = -1
        
        ## PRACTICAL RESULTS: what really happened in the simulation
        self.busy_time_medium = -1
        self.busy_time_STA = []
        self.busy_time_avg = -1
        self.busy_time_std = -1

        self.Tx_attempts_STA = []
        self.Tx_attempts_AP = -1
        self.nb_collisions_STA = []
        self.nb_collisions_AP = -1
        self.collision_rate_STA = []
        self.collision_rate_AP = -1
        self.collision_rate_STA_avg = -1
        self.collision_rate_STA_std = -1

        self.nb_errors_STA = []
        self.nb_errors_AP = -1
        self.sending_frame_attempts_STA = []
        self.sending_frame_attempts_AP = -1
        self.error_rate_STA = []
        self.error_rate_AP = -1
        self.error_rate_STA_avg = -1
        self.error_rate_STA_std = -1
        
        self.DL_throughput_STA = []
        self.DL_throughput_avg = -1
        self.DL_throughput_std = -1
        
        self.UL_throughput_STA = []
        self.UL_throughput_avg = -1
        self.UL_throughput_std = -1

        self.tot_throughput_STA = []
        self.tot_throughput_avg = -1
        self.tot_throughput_std = -1

        self.DL_sent_frames_STA = []
        self.DL_sent_frames_avg = -1
        self.DL_sent_frames_std = -1

        self.UL_sent_frames_STA = []
        self.UL_sent_frames_avg = -1
        self.UL_sent_frames_std = -1

        self.tot_sent_frames_STA = []
        self.tot_sent_frames_avg = -1
        self.tot_sent_frames_std = -1

        self.nb_DL_prompts_STA = []
        self.nb_DL_prompts_avg = -1
        self.nb_DL_prompts_std = -1

        self.nb_ACK_STA = []
        self.nb_ACK_avg = -1
        self.nb_ACK_std = -1
        
        self.DL_generated_frames_STA = []
        self.DL_generated_frames_avg = -1
        self.DL_generated_frames_std = -1

        self.UL_generated_frames_STA = []
        self.UL_generated_frames_avg = -1
        self.UL_generated_frames_std = -1

        self.tot_generated_frames_STA = []
        self.tot_generated_frames_avg = -1
        self.tot_generated_frames_std = -1

        self.DL_delay_STA = []
        self.DL_delay_avg = -1
        self.DL_delay_std = -1

        self.UL_delay_STA = []
        self.UL_delay_avg = -1
        self.UL_delay_std = -1

        self.tot_delay_STA = []
        self.tot_delay_avg = -1
        self.tot_delay_std = -1

        self.idle_STA = []
        self.idle_avg = -1
        self.idle_std = -1
        
        self.CCA_STA = []
        self.CCA_avg = -1
        self.CCA_std = -1

        self.Rx_STA = []
        self.Rx_avg = -1
        self.Rx_std = -1

        self.Tx_STA = []
        self.Tx_avg = -1
        self.Tx_std = -1

        self.doze_STA = []
        self.doze_avg = -1
        self.doze_std = -1

        self.consumption_STA = []
        self.consumption_avg = -1
        self.consumption_std = -1

        self.compute_results()


    def compute_results(self):
        self.get_th_throughput()
        self.get_th_busy_time()

        self.get_simulation_duration()
        self.get_number_of_events()
        self.get_nb_STAs()
        self.get_datarate()

        self.compute_busy_time()
        self.compute_throughput()
        self.compute_Tx_attempts()
        self.compute_collisions()
        self.compute_errors()
        self.compute_sent_frames()
        self.compute_DL_prompts()
        self.compute_ACK()
        self.compute_delay()
        self.compute_generated_frames()
        self.compute_counters()
        self.compute_energy_consumption()


    def get_th_throughput(self):
        if len(self.th_DL_throughput_STA) == 0 or len(self.th_UL_throughput_STA) == 0 or len(self.th_tot_throughput_STA) == 0:
            self.get_nb_STAs()
            self.get_simulation_duration()
            self.th_DL_throughput_STA = [0 for i in range(self.nb_STAs)]
            self.th_UL_throughput_STA = [0 for i in range(self.nb_STAs)]
            self.th_tot_throughput_STA = [0 for i in range(self.nb_STAs)]
            for sta in self.record_data["Events"][self.last_key]["STAs"]:                
                STA_dict = self.record_data["Events"][self.last_key]["STAs"][sta]
                STA_ID = int(sta) - 1 # Minus 1 to get the proper index
                UL_generated_data = STA_dict["UL traffic"]["Generated data"]
                self.th_UL_throughput_STA[STA_ID] += UL_generated_data / self.simulation_duration
                self.th_tot_throughput_STA[STA_ID] += UL_generated_data / self.simulation_duration
                DL_generated_data = STA_dict["DL traffic"]["Generated data"]
                self.th_DL_throughput_STA[STA_ID] += DL_generated_data / self.simulation_duration
                self.th_tot_throughput_STA[STA_ID] += DL_generated_data / self.simulation_duration
                
            assert(len(self.th_DL_throughput_STA) == self.nb_STAs)
            assert(len(self.th_UL_throughput_STA) == self.nb_STAs)
            assert(len(self.th_tot_throughput_STA) == self.nb_STAs)
            
            self.th_DL_throughput_avg = sum(self.th_DL_throughput_STA) / self.nb_STAs
            self.th_UL_throughput_avg = sum(self.th_UL_throughput_STA) / self.nb_STAs
            self.th_tot_throughput_avg = sum(self.th_tot_throughput_STA) / self.nb_STAs

            self.th_DL_throughput_std = sum([(DL_th - self.th_DL_throughput_avg)**2 for DL_th in self.th_DL_throughput_STA])
            self.th_DL_throughput_std = (self.th_DL_throughput_std / self.nb_STAs) **.5
            self.th_UL_throughput_std = sum([(UL_th - self.th_UL_throughput_avg)**2 for UL_th in self.th_UL_throughput_STA])
            self.th_UL_throughput_std = (self.th_UL_throughput_std / self.nb_STAs) **.5
            self.th_tot_throughput_std = sum([(tot_th - self.th_tot_throughput_avg)**2 for tot_th in self.th_tot_throughput_STA])
            self.th_tot_throughput_std = (self.th_tot_throughput_std / self.nb_STAs) **.5


    def get_th_busy_time(self):
        if len(self.th_busy_time_STA) == 0:
            self.get_nb_STAs()
            self.get_th_throughput()
            self.get_datarate()
            for th_tot_throughput, datarate in zip(self.th_tot_throughput_STA, self.datarate_STA):
                self.th_busy_time_STA.append(th_tot_throughput / datarate)
            assert(len(self.th_busy_time_STA) == self.nb_STAs)

            self.th_busy_time_avg = sum(self.th_busy_time_STA) / self.nb_STAs
            self.th_busy_time_std = sum([(bt - self.th_busy_time_avg)**2 for bt in self.th_busy_time_STA])
            self.th_busy_time_std = (self.th_busy_time_std / self.nb_STAs) **.5
            self.th_busy_time_medium = sum(self.th_busy_time_STA)


    def get_simulation_duration(self):
        if self.simulation_duration == -1:
            self.simulation_duration = self.record_data["Events"][self.last_key]["End"]

    def get_nb_STAs(self):
        if self.nb_STAs == -1:
            self.nb_STAs = 0
            for contender in self.record_data["STAs"]:
                self.nb_STAs += 1

    def get_number_of_events(self):
        if self.nb_events == -1:
            self.nb_events = len(self.record_data)

    def get_datarate(self):
        if len(self.datarate_STA) == 0 or self.datarate_avg == -1 or self.datarate_std == -1:
            self.get_nb_STAs()
            self.datarate_STA = [0 for i in range(self.nb_STAs)]
            for sta in self.record_data["STAs"]:
                STA_dict = self.record_data["STAs"][sta]
                STA_ID = int(sta) - 1 # Minus 1 to get the proper index
                self.datarate_STA[STA_ID] = STA_dict["Datarate"]

        self.datarate_avg = sum(self.datarate_STA) / self.nb_STAs
        self.datarate_std = sum([(x - self.datarate_avg)**2 for x in self.datarate_STA])
        self.datarate_std = (self.datarate_std / self.nb_STAs) **.5
            

    def compute_busy_time(self):
        if len(self.busy_time_STA) == 0:
            self.get_nb_STAs()
            self.get_simulation_duration()
            self.busy_time_STA = [0 for i in range(self.nb_STAs)]
            self.busy_time_medium = 0
            for event in self.record_data["Events"]:
                event_dict = self.record_data["Events"][event]
                STA_IDs = SortedSet()
                for frame in event_dict["Frames"]:
                    frame_dict = event_dict["Frames"][frame]
                    STA_IDs.add(frame_dict["Sender ID"])
                    STA_IDs.add(frame_dict["Receiver ID"])
                for sta in STA_IDs:
                    if sta != 0:
                        self.busy_time_STA[sta-1] += event_dict["Duration"]
                self.busy_time_medium += event_dict["Duration"]
            for i in range(self.nb_STAs):
                self.busy_time_STA[i] /= self.simulation_duration
            self.busy_time_medium /= self.simulation_duration

            self.busy_time_avg = sum(self.busy_time_STA) / (self.nb_STAs + 1)
            self.busy_time_std = sum([(x - self.busy_time_avg)**2 for x in self.busy_time_STA])
            self.busy_time_std = (self.busy_time_std / (self.nb_STAs + 1)) **.5
        

    def compute_throughput(self):
        if len(self.DL_throughput_STA) == 0 or len(self.UL_throughput_STA) == 0 or len(self.tot_throughput_STA) == 0:
            self.get_nb_STAs()
            self.get_simulation_duration()
            self.UL_throughput_STA = [0 for i in range(self.nb_STAs)]
            self.DL_throughput_STA = [0 for i in range(self.nb_STAs)]
            self.tot_throughput_STA = [0 for i in range(self.nb_STAs)]
            for event in self.record_data["Events"]:
                event_dict = self.record_data["Events"][event]
                for frame in event_dict["Frames"]:
                    frame_dict = event_dict["Frames"][frame]
                    if frame_dict["Label"] == "DL Tx" and not frame_dict["Collision"] and not frame_dict["Error"]:
                        STA_ID = frame_dict["Receiver ID"] - 1 # Minus 1 to get the proper index 
                        self.DL_throughput_STA[STA_ID] += frame_dict["Size"]
                        self.tot_throughput_STA[STA_ID] += frame_dict["Size"]
                    elif frame_dict["Label"] == "UL Tx" and not frame_dict["Collision"] and not frame_dict["Error"]:
                        STA_ID = frame_dict["Sender ID"] - 1 # Minus 1 to get the proper index
                        self.UL_throughput_STA[STA_ID] += frame_dict["Size"]
                        self.tot_throughput_STA[STA_ID] += frame_dict["Size"]
            for sta in range(self.nb_STAs):
                self.DL_throughput_STA[sta] /= self.simulation_duration
                self.UL_throughput_STA[sta] /= self.simulation_duration
                self.tot_throughput_STA[sta] /= self.simulation_duration
                
            self.DL_throughput_avg = sum(self.DL_throughput_STA) / self.nb_STAs
            self.UL_throughput_avg = sum(self.UL_throughput_STA) / self.nb_STAs
            self.tot_throughput_avg = sum(self.tot_throughput_STA) / self.nb_STAs
            
            self.DL_throughput_std = sum([(th - self.DL_throughput_avg)**2 for th in self.DL_throughput_STA])
            self.DL_throughput_std = (self.DL_throughput_std / self.nb_STAs) **.5
            self.UL_throughput_std = sum([(th - self.UL_throughput_avg)**2 for th in self.UL_throughput_STA])
            self.UL_throughput_std = (self.UL_throughput_std / self.nb_STAs) **.5
            self.tot_throughput_std = sum([(th - self.tot_throughput_avg)**2 for th in self.tot_throughput_STA])
            self.tot_throughput_std = (self.tot_throughput_std / self.nb_STAs) **.5

    def compute_sent_frames(self):
        if len(self.DL_sent_frames_STA) == 0 or len(self.UL_sent_frames_STA) == 0 or len(self.tot_sent_frames_STA) == 0:
            self.get_nb_STAs()
            self.DL_sent_frames_STA = [0 for i in range(self.nb_STAs)]
            self.UL_sent_frames_STA = [0 for i in range(self.nb_STAs)]
            self.tot_sent_frames_STA = [0 for i in range(self.nb_STAs)]
            for event in self.record_data["Events"]:
                for frame in self.record_data["Events"][event]["Frames"]:
                    frame_dict = self.record_data["Events"][event]["Frames"][frame]
                    if not frame_dict["Collision"] and not frame_dict["Error"]:
                        if not frame_dict["Label"] in ["beacon", "DL prompt", "UL prompt", "ACK"]:
                            if frame_dict["Sender ID"] == 0:
                                # DL Tx                            
                                STA_ID = frame_dict["Receiver ID"] - 1 # Minus 1 to get the proper index
                                self.DL_sent_frames_STA[STA_ID] += 1
                                self.tot_sent_frames_STA[STA_ID] += 1
                            elif frame_dict["Receiver ID"] == 0:
                                # UL Tx
                                STA_ID = frame_dict["Sender ID"] - 1 # Minus 1 to get the proper index
                                self.UL_sent_frames_STA[STA_ID] += 1
                                self.tot_sent_frames_STA[STA_ID] += 1
                        
            self.DL_sent_frames_avg = sum(self.DL_sent_frames_STA) / self.nb_STAs
            self.UL_sent_frames_avg = sum(self.UL_sent_frames_STA) / self.nb_STAs
            self.tot_sent_frames_avg = sum(self.tot_sent_frames_STA) / self.nb_STAs
            
            self.DL_sent_frames_std = sum([(st - self.DL_sent_frames_avg)**2 for st in self.DL_sent_frames_STA])
            self.DL_sent_frames_std = (self.DL_sent_frames_std / self.nb_STAs) **.5
            self.UL_sent_frames_std = sum([(st - self.UL_sent_frames_avg)**2 for st in self.UL_sent_frames_STA])
            self.UL_sent_frames_std = (self.UL_sent_frames_std / self.nb_STAs) **.5
            self.tot_sent_frames_std = sum([(st - self.tot_sent_frames_avg)**2 for st in self.tot_sent_frames_STA])
            self.tot_sent_frames_std = (self.tot_sent_frames_std / self.nb_STAs) **.5

    def compute_DL_prompts(self):
        if len(self.nb_DL_prompts_STA) == 0:
            self.get_nb_STAs()
            self.nb_DL_prompts_STA = [0 for i in range(self.nb_STAs)]
            for event in self.record_data["Events"]:
                for frame in self.record_data["Events"][event]["Frames"]:
                    frame_dict = self.record_data["Events"][event]["Frames"][frame]
                    if frame_dict["Label"] == "DL_prompt" and not frame_dict["Collision"] and not frame_dict["Error"]:
                        STA_ID = frame_dict["Sender ID"] - 1
                        self.nb_DL_prompts_STA[STA_ID] += 1
            self.nb_DL_prompts_avg = sum(self.nb_DL_prompts_STA) / self.nb_STAs
            self.nb_DL_prompts_std = sum([(x - self.nb_DL_prompts_avg)**2 for x in self.nb_DL_prompts_STA])
            self.nb_DL_prompts_std = (self.nb_DL_prompts_std / self.nb_STAs) **.5

    def compute_ACK(self):
        if len(self.nb_ACK_STA) == 0:
            self.get_nb_STAs()
            self.nb_ACK_STA = [0 for i in range(self.nb_STAs)]
            for event in self.record_data["Events"]:
                for frame in self.record_data["Events"][event]["Frames"]:
                    frame_dict = self.record_data["Events"][event]["Frames"][frame]
                    if frame_dict["Label"] == "ACK" and not frame_dict["Collision"] and not frame_dict["Error"]:
                        STA_ID = frame_dict["Receiver ID"] - 1
                        self.nb_ACK_STA[STA_ID] += 1
            self.nb_ACK_avg = sum(self.nb_ACK_STA) / self.nb_STAs
            self.nb_ACK_std = sum([(x - self.nb_ACK_avg)**2 for x in self.nb_ACK_STA])
            self.nb_ACK_std = (self.nb_ACK_std / self.nb_STAs) **.5
            
    def compute_delay(self):
        if len(self.DL_delay_STA) == 0 or len(self.UL_delay_STA) == 0 or len(self.tot_delay_STA) == 0:
            self.get_nb_STAs()
            self.compute_sent_frames()
            self.DL_delay_STA = [0 for i in range(self.nb_STAs)]
            self.UL_delay_STA = [0 for i in range(self.nb_STAs)]
            self.tot_delay_STA = [0 for i in range(self.nb_STAs)]
            for event in self.record_data["Events"]:
                event_dict = self.record_data["Events"][event]
                for frame in self.record_data["Events"][event]["Frames"]:
                    frame_dict = self.record_data["Events"][event]["Frames"][frame]
                    if frame_dict["Label"] == "DL Tx" and not frame_dict["Collision"] and not frame_dict["Error"]:
                        STA_ID = frame_dict["Receiver ID"] - 1 # Minus 1 to get the proper index
                        self.DL_delay_STA[STA_ID] += event_dict["End"] - frame_dict["Creation time"]
                        self.tot_delay_STA[STA_ID] += event_dict["End"] - frame_dict["Creation time"]
                    elif frame_dict["Label"] == "UL Tx" and not frame_dict["Collision"] and not frame_dict["Error"]:
                        STA_ID = frame_dict["Sender ID"] - 1 # Minus 1 to get the proper index
                        self.UL_delay_STA[STA_ID] += event_dict["End"] - frame_dict["Creation time"]
                        self.tot_delay_STA[STA_ID] += event_dict["End"] - frame_dict["Creation time"]
            for sta in range(self.nb_STAs):
                self.DL_delay_STA[sta] /= max(1, self.DL_sent_frames_STA[sta])
                self.UL_delay_STA[sta] /= max(1, self.UL_sent_frames_STA[sta])
                self.tot_delay_STA[sta] /= max(1, self.tot_sent_frames_STA[sta])
                
            self.DL_delay_avg = sum(self.DL_delay_STA) / self.nb_STAs
            self.UL_delay_avg = sum(self.UL_delay_STA) / self.nb_STAs
            self.tot_delay_avg = sum(self.tot_delay_STA) / self.nb_STAs
            
            self.DL_delay_std = sum([(dl - self.DL_delay_avg)**2 for dl in self.DL_delay_STA])
            self.UL_delay_std = sum([(dl - self.UL_delay_avg)**2 for dl in self.UL_delay_STA])
            self.tot_delay_std = sum([(dl - self.tot_delay_avg)**2 for dl in self.tot_delay_STA])
            self.DL_delay_std = (self.DL_delay_std / self.nb_STAs) **.5
            self.UL_delay_std = (self.UL_delay_std / self.nb_STAs) **.5
            self.tot_delay_std = (self.tot_delay_std / self.nb_STAs) **.5

    def compute_generated_frames(self):
        if len(self.DL_generated_frames_STA) == 0 or len(self.UL_generated_frames_STA) == 0 or len(self.tot_generated_frames_STA) == 0:
            self.DL_generated_frames_STA = [0 for i in range(self.nb_STAs)]
            self.UL_generated_frames_STA = [0 for i in range(self.nb_STAs)]
            self.tot_generated_frames_STA = [0 for i in range(self.nb_STAs)]
            for sta in self.record_data["Events"][self.last_key]["STAs"]:
                STA_dict = self.record_data["Events"][self.last_key]["STAs"][sta]
                STA_ID = int(sta) - 1 # Minus 1 to get the proper index
                self.UL_generated_frames_STA[STA_ID] += STA_dict["UL traffic"]["Frame counter"]
                self.tot_generated_frames_STA[STA_ID] += STA_dict["UL traffic"]["Frame counter"]
                self.DL_generated_frames_STA[STA_ID] += STA_dict["DL traffic"]["Frame counter"]
                self.tot_generated_frames_STA[STA_ID] += STA_dict["DL traffic"]["Frame counter"]
                    
            self.DL_generated_frames_avg = sum(self.DL_generated_frames_STA) / self.nb_STAs
            self.UL_generated_frames_avg = sum(self.UL_generated_frames_STA) / self.nb_STAs
            self.tot_generated_frames_avg = sum(self.tot_generated_frames_STA) / self.nb_STAs

            self.DL_generated_frames_std = sum([(x - self.DL_generated_frames_avg)**2 for x in self.DL_generated_frames_STA])
            self.UL_generated_frames_std = sum([(x - self.UL_generated_frames_avg)**2 for x in self.UL_generated_frames_STA])
            self.tot_generated_frames_std = sum([(x - self.tot_generated_frames_avg)**2 for x in self.tot_generated_frames_STA])
            self.DL_generated_frames_std = (self.DL_generated_frames_std / self.nb_STAs) **.5
            self.UL_generated_frames_std = (self.UL_generated_frames_std / self.nb_STAs) **.5
            self.tot_generated_frames_std = (self.tot_generated_frames_std / self.nb_STAs) **.5
                    
        
    def compute_counters(self):
        if len(self.idle_STA) == 0 or len(self.CCA_STA) == 0 or len(self.Rx_STA) == 0 or len(self.Tx_STA) == 0 or len(self.doze_STA) == 0:
            self.get_simulation_duration()
            self.idle_STA = [0 for i in range(self.nb_STAs)]
            self.CCA_STA = [0 for i in range(self.nb_STAs)]
            self.Rx_STA = [0 for i in range(self.nb_STAs)]
            self.Tx_STA = [0 for i in range(self.nb_STAs)]
            self.doze_STA = [0 for i in range(self.nb_STAs)]
            for sta in self.record_data["Events"][self.last_key]["STAs"]:
                if sta != "AP":
                    STA_ID = int(sta) - 1 # Minus 1 to get the proper index
                    self.idle_STA[STA_ID] += self.record_data["Events"][self.last_key]["STAs"][sta]["idle time"]
                    self.CCA_STA[STA_ID] += self.record_data["Events"][self.last_key]["STAs"][sta]["CCA time"]
                    self.Rx_STA[STA_ID] += self.record_data["Events"][self.last_key]["STAs"][sta]["Rx time"]
                    self.Tx_STA[STA_ID] += self.record_data["Events"][self.last_key]["STAs"][sta]["Tx time"]
                    self.doze_STA[STA_ID] += self.record_data["Events"][self.last_key]["STAs"][sta]["doze time"]
            for sta in range(self.nb_STAs):
                self.idle_STA[sta] /= self.simulation_duration
                self.CCA_STA[sta] /= self.simulation_duration
                self.Rx_STA[sta] /= self.simulation_duration
                self.Tx_STA[sta] /= self.simulation_duration
                self.doze_STA[sta] /= self.simulation_duration
                    
            self.idle_avg = sum(self.idle_STA) / self.nb_STAs
            self.CCA_avg = sum(self.CCA_STA) / self.nb_STAs
            self.Rx_avg = sum(self.Rx_STA) / self.nb_STAs
            self.Tx_avg = sum(self.Tx_STA) / self.nb_STAs
            self.doze_avg = sum(self.doze_STA) / self.nb_STAs
            
            self.idle_std = sum([(x - self.idle_avg)**2 for x in self.idle_STA])
            self.CCA_std = sum([(x - self.CCA_avg)**2 for x in self.CCA_STA])
            self.Rx_std = sum([(x - self.Rx_avg)**2 for x in self.Rx_STA])
            self.Tx_std = sum([(x - self.Tx_avg)**2 for x in self.Tx_STA])
            self.doze_std = sum([(x - self.doze_avg)**2 for x in self.doze_STA])
            self.idle_std = (self.idle_std / self.nb_STAs) **.5
            self.CCA_std = (self.CCA_std / self.nb_STAs) **.5
            self.Rx_std = (self.Rx_std / self.nb_STAs) **.5
            self.Tx_std = (self.Tx_std / self.nb_STAs) **.5
            self.doze_std = (self.doze_std / self.nb_STAs) **.5

    def compute_energy_consumption(self):
        if len(self.consumption_STA) == 0:
            self.get_nb_STAs()
            self.compute_counters()
            self.consumption_STA = [0 for i in range(self.nb_STAs)]
            for sta in range(self.nb_STAs):
                self.consumption_STA[sta] += self.idle_STA[sta] * IDLE_CONSUMPTION
                self.consumption_STA[sta] += self.CCA_STA[sta] * CCA_CONSUMPTION
                self.consumption_STA[sta] += self.Rx_STA[sta] * RX_CONSUMPTION
                self.consumption_STA[sta] += self.Tx_STA[sta] * TX_CONSUMPTION
                self.consumption_STA[sta] += self.doze_STA[sta] * DOZE_CONSUMPTION

            self.consumption_avg = sum(self.consumption_STA) / self.nb_STAs
            
            self.consumption_std = sum([(x - self.consumption_avg)**2 for x in self.consumption_STA])
            self.consumption_std = (self.consumption_std / self.nb_STAs) **.5
    

    def compute_Tx_attempts(self):
        if len(self.Tx_attempts_STA) == 0:
            self.get_nb_STAs()
            self.Tx_attempts_STA = [0 for i in range(self.nb_STAs)]
            self.Tx_attempts_AP = 0
            for event in self.record_data["Events"]:
                sender_IDs = SortedSet()
                for frame in self.record_data["Events"][event]["Frames"]:
                    frame_dict = self.record_data["Events"][event]["Frames"][frame]
                    sender_IDs.add(frame_dict["Sender ID"])
                for sender_ID in sender_IDs:
                    if sender_ID == 0:
                        self.Tx_attempts_AP += 1
                    else:
                        index = sender_ID - 1
                        self.Tx_attempts_STA[index] += 1
            for Tx_attempts in self.Tx_attempts_STA:
                if Tx_attempts == 0:
                    Tx_attempts = 1

    def compute_collisions(self):
        if len(self.nb_collisions_STA) == 0:
            self.get_nb_STAs()
            self.compute_Tx_attempts()
            self.nb_collisions_STA = [0 for i in range(self.nb_STAs)]
            self.nb_collisions_AP = 0
            for event in self.record_data["Events"]:
                sender_IDs = SortedSet()
                is_collision = False
                for frame in self.record_data["Events"][event]["Frames"]:
                    frame_dict = self.record_data["Events"][event]["Frames"][frame]
                    sender_IDs.add(frame_dict["Sender ID"])
                    is_collision = frame_dict["Collision"]
                if is_collision:
                    for sender_ID in sender_IDs:
                        if sender_ID == 0:
                            self.nb_collisions_AP += 1
                        else:
                            index = sender_ID - 1
                            self.nb_collisions_STA[index] += 1
            self.collision_rate_AP = self.nb_collisions_AP / max(1, self.Tx_attempts_AP)
            self.collision_rate_STA = [0 for i in range(self.nb_STAs)]
            for sta in range(self.nb_STAs):
                self.collision_rate_STA[sta] = self.nb_collisions_STA[sta] / max(1,self.Tx_attempts_STA[sta])

            self.collision_rate_STA_avg = sum(self.collision_rate_STA) / self.nb_STAs

            self.collision_rate_STA_std = sum([(x - self.collision_rate_STA_avg)**2 for x in self.collision_rate_STA])
            self.collision_rate_STA_std = (self.collision_rate_STA_std / self.nb_STAs) **.5

    def compute_errors(self):
        if len(self.nb_errors_STA) == 0 or len(self.sending_frame_attempts_STA) == 0 or len(self.error_rate_STA) == 0:
            self.get_nb_STAs()
            self.nb_errors_STA = [0 for i in range(self.nb_STAs)]
            self.nb_errors_AP = 0
            self.sending_frame_attempts_STA = [0 for i in range(self.nb_STAs)]
            self.sending_frame_attempts_AP = 0
            for event in self.record_data["Events"]:
                for frame in self.record_data["Events"][event]["Frames"]:
                    frame_dict = self.record_data["Events"][event]["Frames"][frame]
                    sender_ID = frame_dict["Sender ID"]
                    if sender_ID == 0:
                        self.sending_frame_attempts_AP += 1
                        if frame_dict["Error"]:
                            self.nb_errors_AP += 1
                    else:
                        index = sender_ID - 1
                        self.sending_frame_attempts_STA[index] += 1
                        if frame_dict["Error"]:
                            self.nb_errors_STA[index] += 1
            self.error_rate_AP = self.nb_errors_AP / max(1, self.sending_frame_attempts_AP)
            self.error_rate_STA = [0 for i in range(self.nb_STAs)]
            for sta in range(self.nb_STAs):
                self.error_rate_STA[sta] = self.nb_errors_STA[sta] / max(1,self.sending_frame_attempts_STA[sta])

            self.error_rate_STA_avg = sum(self.error_rate_STA) / self.nb_STAs

            self.error_rate_STA_std = sum([(x - self.error_rate_STA_avg)**2 for x in self.error_rate_STA])
            self.error_rate_STA_std = (self.error_rate_STA_std / self.nb_STAs) **.5
                    
                    

    def get_dictionary(self):
        result = dict()
        result["Simulation duration"] = self.simulation_duration
        result["Number of events"] = self.nb_events
        result["Number of STAs"] = self.nb_STAs
        datarate = dict()
        for x,y in enumerate(self.datarate_STA):
            datarate[str(x+1)] = y
        result["Datarate STA"] = datarate
        result["Datarate avg"] = self.datarate_avg
        result["Datarate std"] = self.datarate_std

        result["Theoritical busy time medium"] = self.th_busy_time_medium
        th_busy_time_dict = dict()
        for x,y in enumerate(self.th_busy_time_STA):
            th_busy_time_dict[str(x+1)] = y
        result["Theoritical busy time STA"] = th_busy_time_dict
        result["Theoritical busy time avg"] = self.th_busy_time_avg
        result["Theoritical busy time std"] = self.th_busy_time_std

        th_DL_throughput = dict()
        for x,y in enumerate(self.th_DL_throughput_STA):
            th_DL_throughput[str(x+1)] = y
        result["Theoritical DL throughput STA"] = th_DL_throughput
        result["Theoritical DL throughput avg"] = self.th_DL_throughput_avg
        result["Theoritical DL throughput std"] = self.th_DL_throughput_std

        th_UL_throughput = dict()
        for x,y in enumerate(self.th_UL_throughput_STA):
            th_UL_throughput[str(x+1)] = y
        result["Theoritical UL throughput STA"] = th_UL_throughput
        result["Theoritical UL throughput avg"] = self.th_UL_throughput_avg
        result["Theoritical UL throughput std"] = self.th_UL_throughput_std

        th_tot_throughput = dict()
        for x,y in enumerate(self.th_tot_throughput_STA):
            th_tot_throughput[str(x+1)] = y
        result["Theoritical tot throughput STA"] = th_tot_throughput
        result["Theoritical tot throughput avg"] = self.th_tot_throughput_avg
        result["Theoritical tot throughput std"] = self.th_tot_throughput_std

        busy_time = dict()
        for x,y in enumerate(self.busy_time_STA):
            busy_time[str(x+1)] = y
        result["Busy time STA"] = busy_time
        result["Busy time avg"] = self.busy_time_avg 
        result["Busy time std"] = self.busy_time_std
        result["Busy time medium"] = self.busy_time_medium

        DL_throughput = dict()
        for x,y in enumerate(self.DL_throughput_STA):
            DL_throughput[str(x+1)] = y
        result["DL throughput STA"] = DL_throughput
        result["DL throughput avg"] = self.DL_throughput_avg
        result["DL throughput std"] = self.DL_throughput_std

        UL_throughput = dict()
        for x,y in enumerate(self.UL_throughput_STA):
            UL_throughput[str(x+1)] = y
        result["UL throughput STA"] = UL_throughput
        result["UL throughput avg"] = self.UL_throughput_avg
        result["UL throughput std"] = self.UL_throughput_std

        tot_throughput = dict()
        for x,y in enumerate(self.tot_throughput_STA):
            tot_throughput[str(x+1)] = y
        result["Tot throughput STA"] = tot_throughput
        result["Tot throughput avg"] = self.tot_throughput_avg
        result["Tot throughput std"] = self.tot_throughput_std

        DL_sent_frames = dict()
        for x,y in enumerate(self.DL_sent_frames_STA):
            DL_sent_frames[str(x+1)] = y
        result["DL sent frames STA"] = DL_sent_frames
        result["DL sent frames avg"] = self.DL_sent_frames_avg
        result["DL sent frames std"] = self.DL_sent_frames_std

        UL_sent_frames = dict()
        for x,y in enumerate(self.UL_sent_frames_STA):
            UL_sent_frames[str(x+1)] = y
        result["UL sent frames STA"] = UL_sent_frames
        result["UL sent frames avg"] = self.UL_sent_frames_avg
        result["UL sent frames std"] = self.UL_sent_frames_std

        tot_sent_frames = dict()
        for x,y in enumerate(self.tot_sent_frames_STA):
            tot_sent_frames[str(x+1)] = y
        result["Tot sent frames STA"] = tot_sent_frames
        result["Tot sent frames avg"] = self.tot_sent_frames_avg
        result["Tot sent frames std"] = self.tot_sent_frames_std

        DL_prompts = dict()
        for x,y in enumerate(self.nb_DL_prompts_STA):
            DL_prompts[str(x+1)] = y
        result["DL_Prompts STA"] = DL_prompts
        result["DL_Prompts avg"] = self.nb_DL_prompts_avg
        result["DL_Prompts std"] = self.nb_DL_prompts_std

        ACK = dict()
        for x,y in enumerate(self.nb_ACK_STA):
            ACK[str(x+1)] = y
        result["ACK STA"] = ACK
        result["ACK avg"] = self.nb_ACK_avg
        result["ACK std"] = self.nb_ACK_std
        
        DL_gen = dict()
        for x,y in enumerate(self.DL_generated_frames_STA):
            DL_gen[str(x+1)] = y
        result["DL generated frames STA"] = DL_gen
        result["DL generated frames avg"] = self.DL_generated_frames_avg
        result["DL generated frames std"] = self.DL_generated_frames_std

        UL_gen = dict()
        for x,y in enumerate(self.UL_generated_frames_STA):
            UL_gen[str(x+1)] = y
        result["UL generated frames STA"] = UL_gen
        result["UL generated frames avg"] = self.UL_generated_frames_avg
        result["UL generated frames std"] = self.UL_generated_frames_std

        tot_gen = dict()
        for x,y in enumerate(self.tot_generated_frames_STA):
            tot_gen[str(x+1)] = y
        result["Tot generated frames STA"] = tot_gen
        result["Tot generated frames avg"] = self.tot_generated_frames_avg
        result["Tot generated frames std"] = self.tot_generated_frames_std

        DL_delay = dict()
        for x,y in enumerate(self.DL_delay_STA):
            DL_delay[str(x+1)] = y
        result["DL delay STA"] = DL_delay
        result["DL delay avg"] = self.DL_delay_avg
        result["DL delay std"] = self.DL_delay_std

        UL_delay = dict()
        for x,y in enumerate(self.UL_delay_STA):
            UL_delay[str(x+1)] = y
        result["UL delay STA"] = UL_delay
        result["UL delay avg"] = self.UL_delay_avg
        result["UL delay std"] = self.UL_delay_std

        tot_delay = dict()
        for x,y in enumerate(self.tot_delay_STA):
            tot_delay[str(x+1)] = y
        result["Tot delay STA"] = tot_delay
        result["Tot delay avg"] = self.tot_delay_avg
        result["Tot delay std"] = self.tot_delay_std

        collision_rate = dict()
        for x,y in enumerate(self.collision_rate_STA):
            collision_rate[str(x+1)] = y
        result["Collision rate STA"] = collision_rate
        result["Collision rate AP"] = self.collision_rate_AP
        result["Collision rate STA avg"] = self.collision_rate_STA_avg
        result["Collision rate STA std"] = self.collision_rate_STA_std
        
        error_rate = dict()
        for x,y in enumerate(self.error_rate_STA):
            error_rate[str(x+1)] = y
        result["Error rate STA"] = error_rate
        result["Error rate AP"] = self.error_rate_AP
        result["Error rate STA avg"] = self.error_rate_STA_avg
        result["Error rate STA std"] = self.error_rate_STA_std
        
        idle = dict()
        for x,y in enumerate(self.idle_STA):
            idle[str(x+1)] = y
        result["idle STA"] = idle
        result["idle avg"] = self.idle_avg
        result["idle std"] = self.idle_std

        CCA = dict()
        for x,y in enumerate(self.CCA_STA):
            CCA[str(x+1)] = y
        result["CCA STA"] = CCA
        result["CCA avg"] = self.CCA_avg
        result["CCA std"] = self.CCA_std

        Rx = dict()
        for x,y in enumerate(self.Rx_STA):
            Rx[str(x+1)] = y
        result["Rx STA"] = Rx
        result["Rx avg"] = self.Rx_avg
        result["Rx std"] = self.Rx_std

        Tx = dict()
        for x,y in enumerate(self.Tx_STA):
            Tx[str(x+1)] = y
        result["Tx STA"] = Tx
        result["Tx avg"] = self.Tx_avg
        result["Tx stdx"] = self.Tx_std

        doze = dict()
        for x,y in enumerate(self.doze_STA):
            doze[str(x+1)] = y
        result["doze STA"] = doze
        result["doze avg"] = self.doze_avg
        result["doze std"] = self.doze_std

        consumption = dict()
        for x,y in enumerate(self.consumption_STA):
            consumption[str(x+1)] = y
        result["Consumption STA"] = consumption
        result["Consumption avg"] = self.consumption_avg
        result["Consumption std"] = self.consumption_std
        
        return result
    
