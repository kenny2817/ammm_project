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
    # print(solver)
    # print("---- Standard Greedy exec ----")
    # solution = solver.greedy()
    # cost_0: int = solver.check_validity_and_cost(solution)
    # print(f"cost: {cost_0:5}")
    # solver.print_costs(solution)
    # solution = solver.local_search_0(solution, solver.local_search_3)
    # cost_1: int = solver.check_validity_and_cost(solution)
    # print(f"cost: {cost_0:5} > {cost_1:5} | % {(cost_0 - cost_1)/cost_0 * 100:2.2f}%")
    # solution = solver.local_search_0(solution, solver.local_search_2)
    print("---- GRASP exec ----")
    grasp_sol = solver.run_grasp(max_iterations=50, alpha=0.1)
    
    cost_2 = solver.check_validity_and_cost(grasp_sol)
    print(" FINAL RESULT ")
    print(f"cost: {cost_2:5}")
    solver.print_costs(grasp_sol)
