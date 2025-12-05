from math import pow
import random
from common_types import solution_type

class GreedyGrasp:
    def greedy(
        self,
        start_solution: solution_type | None = None,
        start_coverage: list[list[int]] | None = None
    ) -> solution_type:
        
        if start_solution is None:
            solution: list[solution_type] = [
                []
                for _ in range(self.exponent)
            ]
        else:
            solution: list[solution_type] = [
                list(start_solution)
                for _ in range(self.exponent)
            ] 

        if start_coverage is None:
            coverage: list[list[list[int]]] = [
                [[0
                for _ in range(7)] 
                for _ in range(self.N)] 
                for _ in range(self.exponent)
            ]
        else:
            coverage: list[list[list[int]]] = [
                [[daily_coverage 
                for daily_coverage in weekly_coverage] 
                for weekly_coverage in start_coverage] 
                for _ in range(self.exponent)
            ]


        cost: list[int] = [0 for _ in range(self.exponent)]
        total_slots_to_cover = self.N * 7
        

        for exp in range(1, self.exponent + 1):

            current_covered = sum(coverage[exp - 1][n][d] > 0 for n in range(self.N) for d in range(7))
            used_locations: set[int] = set([c for _, _, c in solution[exp - 1]])

            weight_list: list = []
            for n in range(self.N):
                weight_list.append(pow(sum(self.M[n]), exp * self.exponent_multiplier))

            while current_covered < total_slots_to_cover:

                current_best_ratio = float('inf')
                best_move  = None

                # loop per ogni incrocio dove voglio posizionare la mia camera
                for loc in range(self.N):
                    if loc in used_locations:
                        continue

                    # per ogni camera
                    for cam_index in range(self.K):

                        # l'autonomia è da 2 a 6, risolvo l'offset partendo da zero
                        autonomy = self.A[cam_index] - 2
                        if 0 <= autonomy < len(self.pattern_number):
                            max_pattern_index = self.pattern_number[autonomy]
                        else:
                            continue

                        # salvo gli incroci raggiungibili dalla videocamera con indice cam_index
                        crossing_reachable: list = []
                        for target in range(self.N):
                            if (self.M[loc][target] <= self.R[cam_index]) and (self.M[loc][target] < 50):
                                crossing_reachable.append(target)
                                
                        if not crossing_reachable:
                            continue

                        # verifico per pattern, durante tutta la settimana,
                        # il migliore gain e quindi seleziono la migliore scelta
                        # data da cam_index, pattern_index e loc (incrocio dove si trova la camera)
                        for pattern_index in range(max_pattern_index):
                            move_cost = self.compute_cost(cam_index, pattern_index)

                            gain = 0

                            for d in self.pattern_indexes[pattern_index]:
                                for target in crossing_reachable:
                                    if coverage[exp - 1][target][d] == 0:
                                        gain += weight_list[target]

                            if gain > 0:
                                ratio = move_cost / gain
                                # print(f"pattern {pattern_index}, ratio: {ratio} camera: {cam_index} incrocio: {loc}")
                                # se il ratio è migliore di quello trovato precedentemente
                                # scelgo questa combinazione di camera, pattern e incrocio
                                if ratio < current_best_ratio:
                                    
                                    current_best_ratio = ratio
                                    best_move = (cam_index, pattern_index, loc, gain)

                if best_move:
                    best_cam, best_pattern, best_loc, _ = best_move

                    # aggiungo la combinazione all'insieme di soluzioni
                    solution[exp - 1].append((best_cam, best_pattern, best_loc))
                    used_locations.add(best_loc)

                    reachable = []
                    # aggiungo ai reachable gli incroci coperti dalla videocamera
                    # posta all'incrocio best_loc
                    for target in range(self.N):
                        if (self.M[best_loc][target] <= self.R[best_cam]) and (self.M[best_loc][target] < 50): 
                            reachable.append(target)

                    for d in self.pattern_indexes[best_pattern]:
                            # per ogni incrocio coperto (cioè presente in reachable)
                            # se non è presente in coverage lo aggiungo e incremento di 1
                            # il contatore dei current_covered
                        for target in reachable:
                            if coverage[exp - 1][target][d] == 0:
                                current_covered += 1
                            coverage[exp - 1][target][d] += 1
                else:
                    # se non sono riuscito a trovare una best move significa che
                    # non avrò coperto alcuni incrocio in alcuni giorni della settimana
                    print(f"Only covered {current_covered}/{total_slots_to_cover} slots.")
                    break
                
            for (k, p, c) in solution[exp -1]:
                cost[exp - 1] += self.compute_cost(k, p) 
            print("cost:", exp, cost[exp - 1])

        min_index = cost.index(min(cost))
        result = solution[min_index]
        self.coverage = coverage[min_index]

        return result


    def grasp_construction(self, alpha: float) -> solution_type | None:
        """
        Builds a solution using a randomized greedy approach (RCL).
        alpha = 0: Pure Greedy (always pick best)
        alpha = 1: Pure Random (pick any valid move)
        """
        solution: solution_type = []
        
        # Reset coverage for this construction
        current_coverage = [[0 for _ in range(7)] for _ in range(self.N)]
        current_covered_count = 0
        total_slots_to_cover = self.N * 7
        
        used_locations: set[int] = set()
        effective_exponent = self.exponent * self.exponent_multiplier

        # We calculate the weight list by elevating the sum of all crossings reachability for each crossing
        # by self.exponent times a user defined multiplier. In this way if from a crossing other crossings 
        # require an higher reachability, the cross will have an higher weight
        weight_list: list = []
        for n in range(self.N):
            weight_list.append(pow(sum(self.M[n]), effective_exponent))

        # we continue to perform the algorithm until each slot is covered
        while current_covered_count < total_slots_to_cover:
            candidates = [] # List of tuples: (ratio, move)
            
            # 1. Identify all valid candidate moves
            for loc in range(self.N):
                if loc in used_locations:
                    continue

                for cam_index in range(self.K):
                    # Check autonomy validity
                    autonomy = self.A[cam_index] - 2
                    if not (0 <= autonomy < len(self.pattern_number)):
                        continue
                    
                    # We can select for this camera up to max_pattern_index different patterns
                    max_pattern_index = self.pattern_number[autonomy]
                    
                    # Find reachable crossings: the camera range must be higher or equal than the crossing
                    # reachability, and the crossing we're looking must have a reachability < 50
                    crossing_reachable: list = []
                    for target in range(self.N):
                        if (self.M[loc][target] <= self.R[cam_index]) and (self.M[loc][target] < 50):
                            crossing_reachable.append(target)
                    
                    if not crossing_reachable:
                        continue

                    # Evaluate patterns
                    for pattern_index in range(max_pattern_index):
                        # move_cost = self.compute_cost(cam_index, pattern_index)
                        gain = 0
                        
                        # Calculate gain based on uncovered slots
                        for d in self.pattern_indexes[pattern_index]:
                            for target in crossing_reachable:
                                if current_coverage[target][d] == 0:
                                    gain += weight_list[target] 

                        if gain > 0:
                            move_cost = self.compute_cost(cam_index, pattern_index)
                            ratio = move_cost / gain
                            move = (cam_index, pattern_index, loc)
                            candidates.append((ratio, move))
                        else:
                            print(f"gain {gain}")

            if not candidates:
                # Should not happen if a feasible solution exists
                return None

            # 2. Build Restricted Candidate List (RCL)
            # We want to MINIMIZE ratio (Cost / Gain)
            candidates.sort(key=lambda x: x[0]) 
            
            min_ratio = candidates[0][0]
            
            # Threshold: moves with ratio <= min + alpha * (range)
            threshold = min_ratio * (1 + alpha)
            rcl = [move for ratio, move in candidates if ratio <= threshold]
            print(f"rcl: {rcl}")
            
            # 3. Pick random move from RCL
            best_cam, best_pattern, best_loc = random.choice(rcl)
            
            # 4. Update state
            solution.append((best_cam, best_pattern, best_loc))
            used_locations.add(best_loc)
            
            reachable = []
            for target in range(self.N):
                if (self.M[best_loc][target] <= self.R[best_cam]) and (self.M[best_loc][target] < 50): 
                    reachable.append(target)

            for d in self.pattern_indexes[best_pattern]:
                for target in reachable:
                    if current_coverage[target][d] == 0:
                        current_covered_count += 1
                    current_coverage[target][d] += 1
        
        # Save the coverage state for the Local Search to use
        self.coverage = current_coverage 
        return solution

    def run_grasp(self, max_iterations: int = 50, alpha: float = 0.2) -> solution_type:
        """
        Main GRASP Loop.
        1. Randomized Construction
        2. Local Search
        3. Keep Best
        """
        best_solution: solution_type = []
        best_cost = float('inf')

        print(f"Starting GRASP: {max_iterations} iterations, alpha={alpha}")

        for i in range(max_iterations):
            # Phase 1: Construction
            # We use a try-except block in case construction fails or produces invalid coverage
            candidate_sol = self.grasp_construction(alpha)

            if candidate_sol is None:
                continue

            try:
                # Check feasibility immediately
                improved_sol = self.local_search_2(candidate_sol, remove_percent=5) # Pruning
                improved_sol = self.local_search_1(improved_sol) # Pattern optimization
                
                final_cost = self.check_validity_and_cost(improved_sol)

                if final_cost < best_cost:
                    best_cost = final_cost
                    best_solution = improved_sol
                    print(f"Iter {i+1}: New best found! Cost: {best_cost}")
            except ValueError:
                pass

            # Phase 2: Local Search
            # Apply your existing local search logic. 
            # You can chain them (e.g., LS2 -> LS1)
            
            # Calculate final cost
        
        if not best_solution:
            print("GRASP failed to find any solution")
            return self.greedy()

        return best_solution
    
