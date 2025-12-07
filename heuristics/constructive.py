from math import pow
import random
from common_types import solution_type
import time

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

                # loop for each crossing in which we want to put the camera
                for loc in range(self.N):
                    if loc in used_locations:
                        continue

                    # for each camera
                    for cam_index in range(self.K):

                        # autonomy is from 2 to 6, starting offset from zero
                        autonomy = self.A[cam_index] - 2
                        max_pattern_index = self.pattern_number[autonomy]

                        # check the pattern, across all week,
                        # the best gain and then select the best choice
                        # given by cam_index pattern_index and loc (crossing where the camera is located) 
                        for pattern_index in range(max_pattern_index):
                            gain = 0

                            for d in self.pattern_indexes[pattern_index]:
                                for target in self.cross_model_reach[loc][self.R[cam_index]]:
                                    if coverage[exp - 1][target][d] == 0:
                                        gain += weight_list[target]

                            if gain > 0:
                                move_cost = self.compute_cost(cam_index, pattern_index)
                                ratio = move_cost / gain
                                # print(f"pattern {pattern_index}, ratio: {ratio} camera: {cam_index} incrocio: {loc}")
                                # if the ratio is better than the last one, chose this
                                # combination of camera, pattern and crossing
                                if ratio < current_best_ratio:
                                    current_best_ratio = ratio
                                    best_move = (cam_index, pattern_index, loc, gain)

                if best_move:
                    best_cam, best_pattern, best_loc, _ = best_move

                    # add the combination to the set of solutions
                    solution[exp - 1].append((best_cam, best_pattern, best_loc))
                    used_locations.add(best_loc)

                    reachable = []
                    # add to the reachable the crossings covered from camera at
                    # best_loc crossing
                    for target in range(self.N):
                        if (self.M[best_loc][target] <= self.R[best_cam]) and (self.M[best_loc][target] < 50): 
                            reachable.append(target)

                    for d in self.pattern_indexes[best_pattern]:
                            # add a crossing in covered crossing to coverage (if it's not in it)
                            # and increment current_covered by 1 
                        for target in reachable:
                            if coverage[exp - 1][target][d] == 0:
                                current_covered += 1
                            coverage[exp - 1][target][d] += 1
                else:
                    # if we haven't managed to find a best move it means that
                    # we haven't covered some crossings in some days of the week
                    print(f"Only covered {current_covered}/{total_slots_to_cover} slots.")
                    break
                
            for (k, p, c) in solution[exp -1]:
                cost[exp - 1] += self.compute_cost(k, p) 
            # print("cost:", exp, cost[exp - 1])

        min_index = cost.index(min(cost))
        result = solution[min_index]
        self.coverage = coverage[min_index]

        return result
    
    def camera_gain(
        self, 
        camera: int
    ) -> float:
        purchase_cost: int = self.P[camera] # numberofcameras
        active_cost: int = self.C[camera]   # numberofcameras * activedays
        availability: int  = self.A[camera] # activedays
        reach: int = self.R[camera]         # numberofcameras

        # we multiply availability (active days) by 8,16 in order to reach the number of available pattern

        ratio: float = (purchase_cost + active_cost * 2) / (availability * 8.16 + reach)

        return ratio

    def greedy_camera_first(
            self,
            start_solution: solution_type | None = None,
            start_coverage: list[list[int]] | None = None,
            debug: bool = False
        ) -> solution_type:

        cameras = [c for c in range(self.K)]

        sorted_cameras = sorted(cameras, key=lambda k: self.camera_gain(k))

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

        cost: list[int] = []
        total_slots_to_cover = self.N * 7
        
        for cam_index in sorted_cameras:

            for exp in range(1, self.exponent + 1):

                current_covered = sum(coverage[exp - 1][n][d] > 0 for n in range(self.N) for d in range(7))
                used_locations: set[int] = set([c for _, _, c in solution[exp - 1]])

                weight_list: list = []
                for n in range(self.N):
                    weight_list.append(pow(sum(self.M[n]), exp * self.exponent_multiplier))

                while current_covered < total_slots_to_cover:

                    # print(self.coverage)
                    # for n in range(self.N):
                    #     print(self.coverage[n])
                    # print()

                    current_best_ratio = float('inf')
                    best_move  = None

                    # loop for each crossing in which we want to put the camera
                    for loc in range(self.N):
                        if loc in used_locations:
                            continue

                        # autonomy is from 2 to 6, starting offset from zero
                        autonomy = self.A[cam_index] - 2
                        max_pattern_index = self.pattern_number[autonomy]

                         # check the pattern, across all week,
                        # the best gain and then select the best choice
                        # given by cam_index pattern_index and loc (crossing where the camera is located) 
                        for pattern_index in range(max_pattern_index):
                            move_cost = self.compute_cost(cam_index, pattern_index)

                            gain = 0

                            for d in self.pattern_indexes[pattern_index]:
                                for target in self.cross_model_reach[loc][self.R[cam_index]]:
                                    if coverage[exp - 1][target][d] == 0:
                                        gain += weight_list[target]

                            if gain > 0:
                                ratio = move_cost / gain
                                # print(f"pattern {pattern_index}, ratio: {ratio} camera: {cam_index} incrocio: {loc}")
                                # if the ratio is better than the last one, chose this
                                # combination of camera, pattern and crossing
                                if ratio < current_best_ratio:
                                    
                                    current_best_ratio = ratio
                                    best_move = (cam_index, pattern_index, loc, gain)

                    if best_move:
                        best_cam, best_pattern, best_loc, _ = best_move

                        # add the combination to the set of solutions
                        solution[exp - 1].append((best_cam, best_pattern, best_loc))
                        used_locations.add(best_loc)

                        reachable = []
                        # add to the reachable the crossings covered from camera at
                        # best_loc crossing
                        for target in range(self.N):
                            if (self.M[best_loc][target] <= self.R[best_cam]) and (self.M[best_loc][target] < 50): 
                                reachable.append(target)

                        for d in self.pattern_indexes[best_pattern]:
                                # add a crossing in covered crossing to coverage (if it's not in it)
                                # and increment current_covered by 1
                            for target in reachable:
                                if coverage[exp - 1][target][d] == 0:
                                    current_covered += 1
                                coverage[exp - 1][target][d] += 1
                    else:
                        # if we haven't managed to find a best move it means that
                        # we haven't covered some crossings in some days of the week
                        print(f"Only covered {current_covered}/{total_slots_to_cover} slots.")
                        break
                
                if current_covered == total_slots_to_cover:
                    cost.append(0)
                    for (k, p, c) in solution[exp -1]:
                        cost[-1] += self.compute_cost(k, p) 
                    if debug:
                        print("cost:", exp, cost[-1])
            
            if len(cost) > 0:
                break

        min_index = cost.index(min(cost))
        result = solution[min_index]
        self.coverage = coverage[min_index]

        return result
    
    # Here we modified the greedy algo because by only using
    # ratio < best_current_ratio it would became deterministic
    # and the rcl would be filled with always the same solution
    def grasp_construction(self, alpha: float) -> solution_type | None:
        """
        Builds a solution using a randomized greedy approach (RCL).
        alpha = 0: Pure Greedy (always pick best)
        alpha = 1: Pure Random (pick any valid move)
        """
        
        solutions_list: list = []

        for exp in range(1, self.exponent + 1):
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
                
                # Identify all valid candidate moves
                for loc in range(self.N):
                    if loc in used_locations:
                        continue

                    for cam_index in range(self.K):
                        # Check autonomy validity
                        autonomy = self.A[cam_index] - 2
                        
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

                if not candidates:
                    # Should not happen if a feasible solution exists
                    return None

                # Build RCL
                # We want to minimize ratio (Cost / Gain)
                candidates.sort(key=lambda x: x[0]) 
                
                min_ratio = candidates[0][0]
                
                # Threshold: moves with ratio <= min + alpha * (range)
                threshold = min_ratio * (1 + alpha)
                rcl = [move for ratio, move in candidates if ratio <= threshold]

                # Pick random move from RCL
                best_cam, best_pattern, best_loc = random.choice(rcl)
                
                # Update state
                solution.append((best_cam, best_pattern, best_loc))
                used_locations.add(best_loc)
                
                reachable = []

                # Control if crossing (target) is reachable by best_cam (M < Range_camera and M < 50)
                for target in range(self.N):
                    if (self.M[best_loc][target] <= self.R[best_cam]) and (self.M[best_loc][target] < 50): 
                        reachable.append(target)

                # mark crossing covered in current_covered count and increment current_coverage
                for d in self.pattern_indexes[best_pattern]:
                    for target in reachable:
                        if current_coverage[target][d] == 0:
                            current_covered_count += 1
                        current_coverage[target][d] += 1

            cost = self.check_validity_and_cost(solution)
            solutions_list.append((cost, solution, current_coverage))

        solutions_list.sort(key=lambda x: x[0])
        min_ratio = solutions_list[0][0]

        threshold = min_ratio * (1 + alpha)
        rcl = [(solution, current_coverage) for cost, solution, current_coverage in solutions_list if cost <= threshold]

        solution, coverage = random.choice(rcl)
            
        # Save the coverage state for the Local Search to use
        self.coverage = coverage 
        return solution
    
    def grasp_construction_elements(self, alpha: float) -> solution_type | None:
        """
        Builds a solution using a randomized greedy approach (RCL).
        alpha = 0: Pure Greedy (always pick best)
        alpha = 1: Pure Random (pick any valid move)
        """

        # we don't choose only the last solution, but we pick the best
        best_solution: list = []
        best_coverage: list = [[0 for _ in range(7)] for _ in range(self.N)]
        best_cost = float('inf')

        for exp in range(1, self.exponent + 1):
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
                
                # Identify all valid candidate moves
                for loc in range(self.N):
                    if loc in used_locations:
                        continue

                    for cam_index in range(self.K):
                        # Check autonomy validity
                        autonomy = self.A[cam_index] - 2
                        
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

                if not candidates:
                    # Should not happen if a feasible solution exists
                    return None

                # Build RCL
                # We want to minimize ratio (Cost / Gain)
                candidates.sort(key=lambda x: x[0]) 
                
                min_ratio = candidates[0][0]
                
                # Threshold: moves with ratio <= min + alpha * (range)
                threshold = min_ratio * (1 + alpha)
                rcl = [move for ratio, move in candidates if ratio <= threshold]

                # Pick random move from RCL
                best_cam, best_pattern, best_loc = random.choice(rcl)
                
                # Update state
                solution.append((best_cam, best_pattern, best_loc))
                used_locations.add(best_loc)
                
                reachable = []

                # Control if crossing (target) is reachable by best_cam (M < Range_camera and M < 50)
                for target in range(self.N):
                    if (self.M[best_loc][target] <= self.R[best_cam]) and (self.M[best_loc][target] < 50): 
                        reachable.append(target)

                # mark crossing covered in current_covered count and increment current_coverage
                for d in self.pattern_indexes[best_pattern]:
                    for target in reachable:
                        if current_coverage[target][d] == 0:
                            current_covered_count += 1
                        current_coverage[target][d] += 1

            current_cost = self.check_validity_and_cost(solution)

            if current_cost < best_cost:
                best_cost = current_cost
                best_solution = solution
                best_coverage = current_coverage
        
        if best_solution is not None:
            self.coverage = best_coverage 
            return solution
        else:
            return None

    def run_grasp(
        self, 
        grasp_type: str, 
        exec_time: int = 60, 
        alpha: float = 0.2,
        debug: bool = False
    ) -> tuple[solution_type, int]:
        """
        Main GRASP Loop.
        1. Randomized Construction
        2. Local Search
        3. Keep Best
        """
        best_solution: solution_type = []
        best_cost = float('inf')
        stopping_time = time.monotonic() + exec_time

        if debug:
            print(f"Starting GRASP: alpha={alpha}")

        while time.monotonic() < stopping_time:
            # Phase 1: Construction
            # We use a try-except block in case construction fails or produces invalid coverage

            if grasp_type == "full":
                candidate_sol = self.grasp_construction(alpha)
            elif grasp_type == "elements":
                candidate_sol = self.grasp_construction_elements(alpha)

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
                    if debug:
                        print(f"New best found! Cost: {best_cost}")
            except ValueError as e:
                pass

            # Phase 2: Local Search
            # Apply your existing local search logic. 
            # You can chain them (e.g., LS2 -> LS1)
            
            # Calculate final cost
        
        if not best_solution:
            print("GRASP failed to find any solution")
            return self.greedy()

        return (best_solution, best_cost)
    
