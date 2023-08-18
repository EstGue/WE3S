import sys
import os
from colorama import Fore
from colorama import Style
import json

from WE3S.simulation import *
from WE3S.results import *


def main():
    directory_name = sys.argv[1]
    file_list = os.listdir(directory_name)
    for spec_file in file_list:
        print("FILE:", spec_file)
        print("\tReading specifications...")
        f = open(os.path.join(directory_name, spec_file), "r")
        simulation_spec = json.load(f)
        f.close()
        print("\tRunning simulation...")
        simulation_report = run_simulation(simulation_spec)
        print("\tWriting simulation report...")
        simulation_file_name = spec_file.split(".")[0]
        simulation_file_name += "_simulation.json"
        f = open(os.path.join(directory_name, simulation_file_name), "w")
        f.write(json.dumps(simulation_report, indent=4))
        f.close()
        print("\tComputing result metrics...")
        result_metrics = Results(simulation_report)
        print("\tWriting result metrics...")
        result_file_name = spec_file.split(".")[0]
        result_file_name += "_results.json"
        f = open(os.path.join(directory_name, result_file_name), "w")
        f.write(json.dumps(result_metrics.get_dictionary(), indent=4))
        f.close()


def run_simulation(simulation_spec):
    simulation = Simulation()
    simulation.read_spec_from_dict(simulation_spec)
    simulation.run_simulation()
    print(f"{Fore.YELLOW}\tSimulation ran in", simulation.get_chrono(), f"s.{Style.RESET_ALL}")
    return simulation.get_report()
    

    
    

if __name__ == "__main__":
    main()
