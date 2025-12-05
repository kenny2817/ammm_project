from math import pow
from common_types import solution_type
from constants import LS_TARGET_INDEX, LS_TARGET_PATTERNS, LS_TARGET_AVAILABILITY

class LocalSearch:
    def local_search_1(self, solution: solution_type) -> solution_type:
        solution_out: solution_type = solution.copy()
        # try to reduce patterns length
        for i, (model, pattern, crossing) in enumerate(solution_out):
            if pattern > 13: # only patterns with active time > 2
                mapping = self.cross_model_reach[crossing][self.R[model]]
                for day, target, availability in zip(target_index[pattern - 14], target_patterns[pattern - 14], target_availability[pattern - 14]):
                    if all(self.coverage[covered][day] > 1 for covered in mapping): # all covered more than once
                        possible_k = [k for k in range(self.K) if self.A[k] >= availability]
                        best_k = min(possible_k, key=lambda k: self.compute_cost(k, target))
                        solution_out[i] = (best_k, target, crossing)
                        for covered in mapping: # update coverage
                            self.coverage[covered][day] -= 1

        # for n in range(self.N):
        #     print(self.coverage[n])
        # print()

        return solution_out
 
    def local_search_2(
        self, 
        solution: solution_type,
        exponent: int = 5,
        remove_percent: int = 10
    ) -> solution_type:

        solution_out: solution_type = solution.copy()
        values: list[float] = []

        for (model, pattern, crossing) in solution_out:
            reachable: list[int] = self.cross_model_reach[crossing][self.R[model]]
            benefit: float = 0
            for d in self.pattern_indexes[pattern]:
                for target in reachable:
                    benefit += 1/ pow(self.coverage[target][d], exponent)
            cost: int = self.compute_cost(model, pattern)
            value: float = (benefit / cost)
            values.append(value)
            # print(f"camera: {model:2}, crossing: {crossing:2}, pattern {pattern:2}, value: {value:2.3f}, reachable: {reachable}")
        
        sorted_values: list[tuple[int, float]] = sorted(enumerate(values), key=lambda x: x[1])

        # try to remove the less efficient cameras
        for index, value in sorted_values[0:len(sorted_values)//(100//remove_percent)]: # remove 10% of cameras
            model, pattern, crossing = solution[index]
            reachable: list[int] = self.cross_model_reach[crossing][self.R[model]]

            for d in self.pattern_indexes[pattern]:
                for target in reachable:
                    self.coverage[target][d] -= 1
            print(f"{solution[index]} removed, v: {value:2.5f}")
            solution_out.remove(solution[index])
        
        result = self.greedy(solution_out, self.coverage)

        return result
    
    def local_search_0(
        self, 
        solution: solution_type,
        search_strategy: callable
    ) -> solution_type:
        cost_0: int = solver.check_validity_and_cost(solution)
        cost_1: int = cost_0 -1
        while (cost_0 > cost_1):
            cost_0 = cost_1
            solution = search_strategy(solution)
            cost_1 = solver.check_validity_and_cost(solution)
            print(f"cost: {cost_0:5} > {cost_1:5} | % {(cost_0 - cost_1)/cost_0 * 100:2.2f}%")

        return solution
