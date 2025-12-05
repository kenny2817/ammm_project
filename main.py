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
    if len(sys.argv) < 2:
        print("Usage: python main.py <data_file>")
        sys.exit(1)

    data_file = sys.argv[1]
    
    solver = GreedySolver(
        filename=str(data_file),
        exponent=10
    )

    print("---- GRASP exec ----")
    grasp_sol = solver.run_grasp(max_iterations=50, alpha=0.1)
    
    cost_2 = solver.check_validity_and_cost(grasp_sol)
    print(" FINAL RESULT ")
    print(f"cost: {cost_2:5}")
    solver.print_costs(grasp_sol)
