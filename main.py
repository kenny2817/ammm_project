import sys
from core import SolverBase
from heuristics.constructive import GreedyGrasp
from heuristics.local_search import LocalSearch
import time


class GreedySolver(SolverBase, GreedyGrasp, LocalSearch):
    """
    Main solver class that combines:
    1. SolverBase (Data)
    2. ConstructiveMixin (Greedy/GRASP)
    3. LocalSearchMixin (Optimization)
    """
    pass


if __name__ == "__main__":
    import sys

    # 1. Check for correct number of arguments
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <data_file> <mode>")
        print("  <data_file>: Path to the input dataset")
        print("  <mode>     : 'greedy' or 'grasp'")
        sys.exit(1)

    if sys.argv[2].lower().strip() == "grasp" and len(sys.argv) < 5:
        print(f"Usage: python {sys.argv[0]} <data_file> <mode> <grasp_type> <exec_time>")
        print("  <grasp_type> : 'full' or 'elements'")
        print("  <exec_time> Execution time (in seconds) of the program")
        sys.exit(1)

    data_file: str = sys.argv[1]
    mode: str = sys.argv[2].lower().strip()

    # 2. Initialize Solver
    solver = GreedySolver(
        filename=str(data_file),
        exponent=10
    )
    print(solver)

    # 3. Execute based on mode
    if mode == "greedy":
        greedy_exec_time = 0
        print("---- Standard Greedy exec ----")
        
        greedy_time = time.monotonic()
        # Try the new greedy_camera_first, fallback to standard greedy if it fails
        solution = solver.greedy_camera_first()
        greedy_exec_time = time.monotonic() - greedy_time
        try:
            cost_0: int = solver.check_validity_and_cost(solution)
        except Exception as e:
            print(f"greedy_camera_first failed ({e}), reverting to standard greedy...")

            greedy_time = time.monotonic()
            solution = solver.greedy()
            greedy_exec_time = time.monotonic() - greedy_time
            
            cost_0: int = solver.check_validity_and_cost(solution)
            
        print(f"Initial Cost: {cost_0:5}. Time for greedy execution: {greedy_exec_time} ms, {greedy_exec_time / 1000} s")
        solver.print_costs(solution)

        # Apply Local Search
        print("\n--- Running Local Search ---")

        local_search_3_time = time.monotonic()
        solution = solver.local_search_0(solution, solver.local_search_3)
        greedy_exec_time += time.monotonic() - local_search_3_time
        cost_1: int = solver.check_validity_and_cost(solution)

        local_search_2_time = time.monotonic()
        solution = solver.local_search_0(solution, solver.local_search_2)
        greedy_exec_time += time.monotonic() - local_search_2_time

        print(f"LS Cost: {cost_0:5} > {cost_1:5} | Improvement: {(cost_0 - cost_1)/cost_0 * 100:2.2f}%")
        cost_final: int = solver.check_validity_and_cost(solution)
        solver.print_costs(solution)
        print(f"Greedy+local search execution time: {greedy_exec_time} ms, {greedy_exec_time / 1000} s")

    elif mode == "grasp":
        grasp_type: str = sys.argv[3].lower().strip()
        exec_time: int = int(sys.argv[4])
        if grasp_type != "full" and grasp_type != "elements":
            print(f"Error: invalid grasp type: '{grasp_type}'.")
            print("Available choices: 'full' or 'elements'")
            sys.exit(1)
        
        
        # Uncommented and active GRASP logic
        grasp_sol, cost_2 = solver.run_grasp(grasp_type, exec_time, alpha=0.1)
        
        print(" FINAL RESULT ")
        print(f"GRASP Cost: {cost_2:5}")
        solver.print_costs(grasp_sol)

    else:
        # 4. Handle invalid mode
        print(f"Error: Invalid mode '{mode}'.")
        print("Please choose either 'greedy' or 'grasp'.")
        sys.exit(1)