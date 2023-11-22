import sys
import os
import json

from WE3S.simulation import *
from WE3S.results import *

def main():
    directory_name = sys.argv[1]
    specification_filename = sys.argv[2]
    filename = specification_filename.split(".")[0]

    print("\t", filename, " - Reading specifications...")
    f = open(os.path.join(directory_name, specification_filename), "r")
    simulation_spec = json.load(f)
    f.close()

    print("\t", filename, " - Running simulation...")
    simulation = Simulation()
    simulation.read_spec_from_dict(simulation_spec)
    simulation.run_simulation()

    print("\t", filename, " - Writing report... (", simulation.get_chrono(), ")")
    simulation_report = simulation.get_record()
    report_filename = filename + "_report.json"
    f = open(os.path.join(directory_name, report_filename), "w")
    f.write(json.dumps(simulation_report, indent=4))
    f.close()

    print("\t", filename, " - Computing results...")
    simulation_results = Results(simulation_report)
    results_filename = filename + "_results.json"
    f = open(os.path.join(directory_name, results_filename), "w")
    f.write(json.dumps(simulation_results.get_dictionary(), indent=4))
    f.close()

if __name__ == "__main__":
    main()
