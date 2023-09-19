# WE3S (WLAN Energy-saving Strategies Simulator)

## How to get started
The simplest way to get started is to use a JSON file to describe the simulation specification, such as `specification_dir/specification_model.json`.

In this file, all the possible fields are present, but they will be ignored when not necessary. For example, if a STA indicates `"use DL slot":false`, then the field named `DL slot` will be ignored.

The script `run_simulation_from_specification.py` can run simulations from JSON specification files.
It takes as argument a directory which contains only specification files (one or multiple).
The script will take each file inside the directory, and will run the simulation described in the file.
The script will output 2 files for a specification file. For example, if the specification file is named `specification_model.json`:
+ `specification_model_simulation.json` reports the events that occured during the simulation, one by one.
+ `specification_model_results.json` computes the different metrics observed during the simulation.

If you have a fresh copy of the repository, you can run a simulation directly with the following command:
```
python3 run_simulation_from_specification.py specification_dir/
```

## Global architecture

The entry point of the module is the class Simulation, in the file of the same name. It gathers the specifications and follows them to the concerned classes.
It also creates and operates the Event_handler.
Basically, a simulation is a circle between the Event_handler and the different Contenders (AP and STA).
The Contenders tell to the Event_handler their next event (as if no other Contender were present).
Then, the Event_handler will elect one event among those returned by the Contenders. This event becomes the actual next event of the simulation.
Finallly, the Event_handler informs the Contenders of the next event, so that the Contenders can update their inner state.
