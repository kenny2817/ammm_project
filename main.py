import sys
from core import SolverBase
from heuristics.constructive import GreedyGrasp
from heuristics.local_search import LocalSearch


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

    if sys.argv[2].lower().strip() == "grasp" and len(sys.argv) < 4:
        print(f"Usage: python {sys.argv[0]} <data_file> <mode> <grasp_type>")
        print("  <grasp_type> : 'full', 'elements' or 'solutions'")
        sys.exit(1)

    data_file = sys.argv[1]
    mode = sys.argv[2].lower().strip()
    grasp_type = sys.argv[3].lower().strip()

    # 2. Initialize Solver
    solver = GreedySolver(
        filename=str(data_file),
        exponent=10
    )
    print(solver)

    # 3. Execute based on mode
    if mode == "greedy":
        print("---- Standard Greedy exec ----")
        
        # Try the new greedy_camera_first, fallback to standard greedy if it fails
        solution = solver.greedy_camera_first()
        try:
            cost_0: int = solver.check_validity_and_cost(solution)
        except Exception as e:
            print(f"greedy_camera_first failed ({e}), reverting to standard greedy...")
            solution = solver.greedy()
            cost_0: int = solver.check_validity_and_cost(solution)
            
        print(f"Initial Cost: {cost_0:5}")
        solver.print_costs(solution)

        # Apply Local Search
        print("\n--- Running Local Search ---")
        solution = solver.local_search_0(solution, solver.local_search_3)
        cost_1: int = solver.check_validity_and_cost(solution)
        print(f"LS Cost: {cost_0:5} > {cost_1:5} | Improvement: {(cost_0 - cost_1)/cost_0 * 100:2.2f}%")
        
        solution = solver.local_search_0(solution, solver.local_search_2)
        cost_final: int = solver.check_validity_and_cost(solution)
        solver.print_costs(solution)

    elif mode == "grasp":
        if grasp_type != "full" and grasp_type != "elements":
            print(f"Error: invalid grasp type: '{grasp_type}'.")
            print("Available choices: 'full' or 'elements'")
            sys.exit(1)
        
        
        # Uncommented and active GRASP logic
        grasp_sol, cost_2 = solver.run_grasp(grasp_type, max_iterations=20, alpha=0.1)
        
        print(" FINAL RESULT ")
        print(f"GRASP Cost: {cost_2:5}")
        solver.print_costs(grasp_sol)

    else:
        # 4. Handle invalid mode
        print(f"Error: Invalid mode '{mode}'.")
        print("Please choose either 'greedy' or 'grasp'.")
        sys.exit(1)