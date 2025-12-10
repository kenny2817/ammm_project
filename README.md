# Algorithmic Methods for Mathematical Models


## Project Course - Batman & Gotham City
> "That's the thing about Batman. Batman Thinks Of Everything."
Batman #681 (December 2008)


### Table of content
1. [Generate the test cases](#generate-the-test-cases)
2. [Run the solver](#run-the-solver)
3. [Execute the batch system](#execute-the-batch-system)
4. [Organization of the codebase](#organization-of-the-codebase)
5. [Repository tree](#repository-tree)

> The description of the problem is inside the file `project/project.pdf`

### Generate the test cases

To generate the test cases, modify the file `test_cases/config.dat`. You can edit **SEED**, **K** (number of cameras), **N** (number of crossings), **maxP** (maximum purchase price for the cameras) and **maxC** (maximum power consumption for the cameras).

Then, execute the generator with the command

> `python -m test_cases.problem_generator` 

and a file `output_seed_{seed}_K{K}_N{N}.dat` (where the text inside curly braces will be replaced with the respective values) will be created inside the folder `test_cases/generated`.

### Run the solver

To run the solver, run the following command

> `python main.py <data_file> <mode> <grasp_type> <exec_time>`

Where 
- `<data_file>` is the filename in which the input data is stored. If you have generated it with `problem_generator.py` it is located inside the folder `test_cases/generated`
- `<mode>` can be `greedy` or `grasp`, to select the algorithm that runs during the execution
- `<grasp_type>` can be `full` (for the full hierarchical construction) or `elements` (for the moves-only construction). Needed only when the selected `mode` is `grasp`.
- `<exec_time>` maximum execution time in seconds of the GRASP algorithm. Needed only when the selected `mode` is `grasp`.

For instance, if you want to run the solver for the data `example.dat` inside the folder `test_cases` with the GRASP algorithm, full hierarchical construction and a maximum execution time of 60 seconds, you should run 

> `python main.py test_cases/example.dat grasp full 60`

### Execute the batch system

To easily execute multiple solvers with all three approaches (CPLEX, Greedy, GRASP), the file batch.py can be used.
However, this file needs a json config file, that can be generated with `batch/batch_final_generator.py`. This script only needs a data folder, where all of your .dat files are located. By default is `test_case/generated` but the variable `data_folder` can be changed accordingly.
After that, you can run the batch json generator with

> `python -m batch.batch_final_generator`

It will be created in the `json/` folder.
Then, to execute the batch system, run 

> `python -m batch.batch <config_file.json> <result_file.csv> [max_workers]`

Where 
- `config_file.json` is the path of the json configuration file. If you have generated with `batch_final_generator.py`, the path is `json/final_test_config.json`
- `result_file.csv` is the name of the output file that contains all the execution results. It will be created inside the `results` folder
- `[max_workers]` is the amount of threads involved in the batch system. This is not a mandatory parameter. By default is equal to the maximum thread worker available for your CPU.

The logs will be added to the `logs` folder.

### Organization of the codebase

The Mixin Pattern has been adopted to organize this codebase.

The `main.py` file contains the **GreedySolver** class, and that can execute Greedy, GRASP or CPLEX algorithms to resolve the problem. based on the user input.

`core.py` contains the `SolverBase` class, a superclass with methods common to all the algorithms: `get_from_file`, `compute_cost`, `print_cost` and `check_validity_and_cost` (that contains a call to `compute_cost`).

All the algorithms implementations can be found inside `heuristics` folder.

#### Repository tree

    [ammm_project]
      ├── batch
      │   ├── batch_final_generator.py
      │   ├── batch.py
      │   └── batch_tuning_generator.py
      ├── common_types.py
      ├── config_tuning_1.json
      ├── constants.py
      ├── core.py
      ├── dat_parser.py
      ├── heuristics
      │   ├── constructive.py
      │   ├── __init__.py
      │   └── local_search.py
      ├── __init__.py
      ├── json
      │   ├── example.json
      │   └── final.json
      ├── logs
      ├── main.py
      ├── opl_models
      │   ├── problem_description.md
      │   ├── project.mod
      │   └── project_optimized.mod
      ├── output_.dat
      ├── out.txt
      ├── plotters
      │   ├── plotter_results.py
      │   └── plotter_tuning.py
      ├── project
      │   ├── project.1.dat
      │   ├── project.1.sol
      │   ├── project.2.dat
      │   ├── project.2.sol
      │   ├── project.3.dat
      │   ├── project.3.sol
      │   ├── project.4.dat
      │   ├── project.4.sol
      │   ├── project.5.dat
      │   ├── project.5.sol
      │   ├── project.pdf
      │   └── project.template.mod
      ├── project.zip
      ├── random_output1.dat
      ├── README.md
      ├── results
      │   └── example.csv
      └── test_cases
          ├── config.dat
          ├── generated
          │   ├── output_seed_1384_K10_N40.dat
          │   ├── output_seed_1592_K20_N20.dat
          │   ├── output_seed_1807_K5_N30.dat
          │   ├── output_seed_2726_K5_N20.dat
          │   ├── output_seed_3279_K20_N40.dat
          │   ├── output_seed_3456_K10_N30.dat
          │   ├── output_seed_4017_K10_N20.dat
          │   ├── output_seed_772_K5_N40.dat
          │   └── output_seed_806_K20_N30.dat
          ├── problem_generator.py
          └── random_output.dat
