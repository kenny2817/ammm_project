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
                for day, target, availability in zip(LS_TARGET_INDEX[pattern - 14], LS_TARGET_PATTERNS[pattern - 14], LS_TARGET_AVAILABILITY[pattern - 14]):
                    if all(self.coverage[covered][day] > 1 for covered in mapping): # all covered more than once
                        possible_k = [k for k in range(self.K) if self.A[k] >= availability]
                        best_k = min(possible_k, key=lambda k: self.compute_cost(k, target))
                        solution_out[i] = (best_k, target, crossing)
                        for covered in mapping: # update coverage
                            self.coverage[covered][day] -= 1


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
                    benefit += 1/ pow(self.coverage[target][d], self.exponent)
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
            # print(f"{solution[index]} removed, v: {value:2.5f}")
            solution_out.remove(solution[index])
        
        result = self.greedy(solution_out, self.coverage)

        return result

    def local_search_3(
        self, 
        solution: solution_type
    ) -> solution_type:

        solution_out: solution_type = solution.copy()

        removable_pattern: list[tuple[int, int, int, int]] = []
        removable_range: dict[int, int] = {}
        for i, (model, pattern, crossing) in enumerate(solution_out):
            if pattern > 13: # only patterns with active time > 2
                mapping = self.cross_model_reach[crossing][self.R[model]]
                for day, target, availability in zip(LS_TARGET_INDEX[pattern - 14], LS_TARGET_PATTERNS[pattern - 14], LS_TARGET_AVAILABILITY[pattern - 14]):
                    if all(self.coverage[covered][day] > 1 for covered in mapping): # all covered more than once
                        removable_pattern.append((i, day, target, availability))

            for r in reversed(self.ranges[0 : self.ranges.index(self.R[model])+1]):
                if all(self.coverage[covered][day] > 1 
                       for covered in self.cross_reach_exclusive[crossing][r] 
                       for day in self.pattern_indexes[pattern]):
                    # print(crossing, r, "l", *self.cross_reach_exclusive[crossing][r])
                    removable_range[i] = r
                else:
                    break

        # find the best option
        options: dict[tuple[int, int, int, int], int] = {}

        for i, day, target, availability in removable_pattern:
            possible_k = [k for k in range(self.K) if self.A[k] >= availability and self.R[k] >= self.R[solution[i][0]]]
            best_k = min(possible_k, key=lambda k: self.compute_cost(k, target))
            options[(i, best_k, target, 0)] = self.compute_cost(solution_out[i][0], solution_out[i][1]) - self.compute_cost(best_k, target)
        
        for i, r in removable_range.items():
            possible_k = [k for k in range(self.K) if self.R[k] >= r]
            best_k = min(possible_k, key=lambda k: self.compute_cost(k, solution_out[i][1]))
            options[(i, best_k, solution_out[i][1], 1)] = self.compute_cost(solution_out[i][0], solution_out[i][1]) - self.compute_cost(best_k, solution_out[i][1])

        if options:
            target_for_removal = max(options.items(), key=lambda o : o[1])[0]
            # print(target_for_removal)
            target = solution_out[target_for_removal[0]]
            # print(self.cross_model_reach[target[2]][self.R[target[0]]])
            for covered in self.cross_model_reach[target[2]][self.R[target[0]]]: # update coverage
                for day in self.pattern_indexes[target[1]]:
                    self.coverage[covered][day] -= 1

            # for n in range(self.N):
            #     print(self.coverage[n])
            # print(1)
            # print(solution_out)

            solution_out[target_for_removal[0]] = (target_for_removal[1], target_for_removal[2], target[2])
            # print(solution_out)

            target = solution_out[target_for_removal[0]]
            # print(self.cross_model_reach[target[2]][self.R[target[0]]])
            for covered in self.cross_model_reach[target[2]][self.R[target[0]]]: # update coverage
                for day in self.pattern_indexes[target[1]]:
                    self.coverage[covered][day] += 1
            
            # for n in range(self.N):
            #     print(self.coverage[n])
            # print(2)

        return solution_out
    
    def local_search_0(
        self, 
        solution: solution_type,
        search_strategy: callable
    ) -> solution_type:
                
        cost_0: int = 1
        cost_1: int = 0
        safe_sol : solution_type
        
        while (cost_0 > cost_1):
            safe_sol = solution
            cost_0 = self.check_validity_and_cost(solution)
            solution = search_strategy(solution)
            try:
                cost_1 = self.check_validity_and_cost(solution)
                print(f"cost: {cost_0:5} > {cost_1:5} | % {(cost_0 - cost_1)/cost_0 * 100:2.2f}%")
            except:
                break

        return safe_sol
