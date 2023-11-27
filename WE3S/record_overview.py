import json
from colorama import Fore
from colorama import Style
import matplotlib.pyplot as plt

from .record import *
from .results import *


class Record_overview:

    def __init__(self, record, time_step):
        self.record = record.copy()
        self.time_step = time_step
        self.record_slice_table = []
        self.result_slice_table = []

        self.slice_record()
        self.compute_results()


    def slice_record(self):
        global_STA_dict = self.record["STAs"]
        offset = 0
        current_record_slice = dict()
        for event in self.record["Events"]:
            event_dict = self.record["Events"][event]
            while offset + self.time_step <= event_dict["Start"]:
                if len(current_record_slice) != 0:
                    total_slice = {"STAs": global_STA_dict, "Events": current_record_slice}
                    # self.record_slice_table.append(current_record_slice)
                    self.record_slice_table.append(total_slice)
                else:
                    self.record_slice_table.append(dict())
                current_record_slice = dict()
                offset += self.time_step
            self.shift_event(event_dict, offset)
            current_record_slice[event] = event_dict

    def shift_event(self, event_dict, offset):
        event_start = event_dict["Start"] - offset
        event_end = event_dict["End"] - offset
        event_dict["Start"] = event_start
        event_dict["End"] = event_end
        for frame in event_dict["Frames"]:
            frame_dict = event_dict["Frames"][frame]
            frame_creation = frame_dict["Creation time"] - offset
            frame_dict["Creation time"] = frame_creation

    def compute_results(self):
        for record_slice in self.record_slice_table:
            result_slice = None
            if record_slice != {}:
                result_slice = Results(record_slice)
            self.result_slice_table.append(result_slice)


    def visualize_throughput(self, STA_ID, window_start_time, window_end_time):
        involved_DL_slot = self.get_involved_DL_slot(STA_ID, window_start_time, window_end_time)
        involved_UL_slot = self.get_involved_UL_slot(STA_ID, window_start_time, window_end_time)
        
        offset_start_index = int(window_start_time // self.time_step)
        offset_end_index = int(window_end_time // self.time_step) + 1
        if len(self.result_slice_table) < offset_start_index:
            print(f"{Fore.RED}Visualization out of record.{Style.RESET_ALL}")
            return
        time_table = self.generate_time_table(window_start_time, window_end_time)

        DL_sent_frames = []
        UL_sent_frames = []
        tot_sent_frames = []

        DL_generated_frames = []
        UL_generated_frames = []
        tot_generated_frames = []
        already_DL_generated = 0
        already_UL_generated = 0
        already_tot_generated = 0

        for i in range(offset_start_index):
            result_slice = self.result_slice_table[i]
            if result_slice is not None:
                already_DL_generated = result_slice.DL_generated_frames_STA[STA_ID - 1]
                already_UL_generated = result_slice.UL_generated_frames_STA[STA_ID - 1]
                already_tot_generated = already_DL_generated + already_UL_generated
        
        for i in range(offset_start_index, offset_end_index+1):
            if i >= len(self.result_slice_table):
                DL_sent_frames.append(0)
                UL_sent_frames.append(0)
                tot_sent_frames.append(0)

                DL_generated_frames.append(0)
                UL_generated_frames.append(0)
                tot_generated_frames.append(0)
            else:
                result_slice = self.result_slice_table[i]
                if result_slice is None:
                    DL_sent_frames.append(0)
                    UL_sent_frames.append(0)
                    tot_sent_frames.append(0)

                    DL_generated_frames.append(0)
                    UL_generated_frames.append(0)
                    tot_generated_frames.append(0)
                else:
                    DL_sent_frames.append(-result_slice.DL_sent_frames_STA[STA_ID - 1])
                    UL_sent_frames.append(-result_slice.UL_sent_frames_STA[STA_ID - 1])
                    tot_sent_frames.append(-result_slice.tot_sent_frames_STA[STA_ID - 1])

                    DL_tmp = result_slice.DL_generated_frames_STA[STA_ID - 1]
                    UL_tmp = result_slice.UL_generated_frames_STA[STA_ID - 1]
                    tot_tmp = result_slice.tot_generated_frames_STA[STA_ID - 1]
                    DL_generated_frames.append(DL_tmp - already_DL_generated)
                    UL_generated_frames.append(UL_tmp - already_UL_generated)
                    tot_generated_frames.append(tot_tmp - already_tot_generated)
                    already_DL_generated = DL_tmp
                    already_UL_generated = UL_tmp
                    already_tot_generated = tot_tmp

        window_size = window_end_time - window_start_time
        real_window_start = window_start_time - 0.5 * window_size
        showing_window_start = window_start_time - 0.05 * window_size
        real_window_end = window_end_time + 0.5 * window_size
        showing_window_end = window_end_time + 0.05 * window_size
        ax = plt.subplot(211)
        plt.suptitle("Simulation monitoring", fontsize=17)
        plt.title("Time step: " + str(self.time_step))

        plt.axvspan(real_window_start, window_start_time, color="grey")
        plt.axvspan(window_end_time, real_window_end, color="grey")
        for DL_slot in involved_DL_slot:
            plt.axvspan(DL_slot[0], DL_slot[1], color="green", alpha=0.1)
        plt.bar(time_table, DL_generated_frames, width = 0.75*self.time_step, color="teal", label="Generated frames")
        plt.bar(time_table, DL_sent_frames, width=0.75*self.time_step, color="mediumturquoise", label="Sent frames")
        plt.legend(loc="upper right")
        plt.grid(linestyle=":", color="gray", alpha=0.5, axis="y")
        plt.ylabel("Nb of sent frames (DL)")
        ax.set_xlim([showing_window_start, showing_window_end])
        ticks = ax.get_yticks()
        # ax.set_yticklabels([int(abs(tick)) for tick in ticks])
        
        ax = plt.subplot(212)
        plt.axvspan(real_window_start, window_start_time, color="grey")
        plt.axvspan(window_end_time, real_window_end, color="grey")
        for UL_slot in involved_UL_slot:
            plt.axvspan(UL_slot[0], UL_slot[1], color="orange", alpha=0.5)
        plt.bar(time_table, UL_generated_frames, width = 0.75*self.time_step, color="teal", label="Generated frames")
        plt.bar(time_table, UL_sent_frames, width=0.75*self.time_step, color="mediumturquoise", label="Sent frames")
        plt.grid(linestyle=":", color="gray", alpha=0.5, axis="y")
        plt.legend(loc="upper right")
        plt.ylabel("Nb of sent frames (UL)")
        plt.xlabel("Simulation time (s)", fontsize=13)
        ax.set_xlim([showing_window_start, showing_window_end])
        # ax.set_yticklabels([int(abs(tick)) for tick in ticks])

        # plt.subplot(313)
        # plt.plot(tot_sent_frames)
        # plt.grid(linestyle=":", color="gray", alpha=0.5)

        plt.show()


    def generate_time_table(self, window_start_time, window_end_time):
        first_offset_index = int(window_start_time // self.time_step)
        last_offset_index = int(window_end_time // self.time_step) + 1
        return [offset_index * self.time_step for offset_index in range(first_offset_index, last_offset_index+1)]

    def get_involved_DL_slot(self, STA_ID, window_start, window_end):
        if not self.record["STAs"][str(STA_ID)]["use DL slot"]:
            return []
        result = []
        DL_slot_start = self.record["STAs"][str(STA_ID)]["DL slot"]["Start"]
        DL_slot_duration = self.record["STAs"][str(STA_ID)]["DL slot"]["Duration"]
        DL_slot_interval = self.record["STAs"][str(STA_ID)]["DL slot"]["Interval"]

        slot_start = DL_slot_start
        slot_end = slot_start + DL_slot_duration
        while slot_start < window_end:
            if slot_end > window_start:
                result.append([slot_start, slot_end])
            slot_start += DL_slot_interval
            slot_end = slot_start + DL_slot_duration
        return result

    def get_involved_UL_slot(self, STA_ID, window_start, window_end):
        if not self.record["STAs"][str(STA_ID)]["use UL slot"]:
            return []
        result = []
        UL_slot_start = self.record["STAs"][str(STA_ID)]["UL slot"]["Start"]
        UL_slot_duration = self.record["STAs"][str(STA_ID)]["UL slot"]["Duration"]
        UL_slot_interval = self.record["STAs"][str(STA_ID)]["UL slot"]["Interval"]

        slot_start = UL_slot_start
        slot_end = slot_start + UL_slot_duration
        while slot_start < window_end:
            if slot_end > window_start:
                result.append([slot_start, slot_end])
            slot_start += UL_slot_interval
            slot_end = slot_start + UL_slot_duration
        return result
