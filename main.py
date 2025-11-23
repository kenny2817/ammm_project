from collections import defaultdict
from typing import DefaultDict
from pydantic import BaseModel, Field, model_validator, computed_field # type: ignore
from parser import parse_dat_file
from math import pow

solution_type = list[tuple[int, int, int]]  # camera_model, pattern_index, crossing
class GreedySolver(BaseModel):

    filename: str
    exponent: int
    exponent_multiplier: int = 2

    K: int = 0
    N: int = 0

    P: list[int] = Field(default_factory=list)
    R: list[int] = Field(default_factory=list)
    A: list[int] = Field(default_factory=list)
    C: list[int] = Field(default_factory=list)

    M: list[list[int]] = Field(default_factory=list)

    pattern: list[list[int]] = [
        [1,0,0,0,0,0,1, 1,0,1,1,0,0,1, 1,0,0,0,0,1,1, 1,0,1,1,1,0,1, 1,0,0,1,1,1,1, 1,0,1,1,1,1,1, 1,0,1,1,1,1,1],  # Day 1
        [1,1,0,0,0,0,0, 1,1,0,1,1,0,0, 1,1,0,0,0,0,1, 1,1,0,1,1,1,0, 1,1,0,0,1,1,1, 1,1,0,1,1,1,1, 1,1,0,1,1,1,1],  # Day 2
        [0,1,1,0,0,0,0, 0,1,1,0,1,1,0, 1,1,1,0,0,0,0, 0,1,1,0,1,1,1, 1,1,1,0,0,1,1, 1,1,1,0,1,1,1, 1,1,1,0,1,1,1],  # Day 3
        [0,0,1,1,0,0,0, 0,0,1,1,0,1,1, 0,1,1,1,0,0,0, 1,0,1,1,0,1,1, 1,1,1,1,0,0,1, 1,1,1,1,0,1,1, 1,1,1,1,0,1,1],  # Day 4
        [0,0,0,1,1,0,0, 1,0,0,1,1,0,1, 0,0,1,1,1,0,0, 1,1,0,1,1,0,1, 1,1,1,1,1,0,0, 1,1,1,1,1,0,1, 1,1,1,1,1,0,1],  # Day 5
        [0,0,0,0,1,1,0, 1,1,0,0,1,1,0, 0,0,0,1,1,1,0, 1,1,1,0,1,1,0, 0,1,1,1,1,1,0, 1,1,1,1,1,1,0, 1,1,1,1,1,1,0],  # Day 6
        [0,0,0,0,0,1,1, 0,1,1,0,0,1,1, 0,0,0,0,1,1,1, 0,1,1,1,0,1,1, 0,0,1,1,1,1,1, 0,1,1,1,1,1,1, 0,1,1,1,1,1,1]   # Day 7
    ]
    pattern_indexes: list[list[int]] = Field(default_factory=list)

    pattern_cost: list[int] = Field(default_factory=list)

    pattern_number: list = [14, 28, 35, 42, 49]
    coverage: list[list[int]] = Field(default_factory=list)
    cross_model_reach: list[DefaultDict[int, set[int]]] = Field(default_factory=list)

    @model_validator(mode="after")
    def deserializer(self) -> "GreedySolver":
        
        data = parse_dat_file(self.filename)
        self.K = data["K"]
        self.N = data["N"]
        self.P = data["P"]
        self.R = data["R"]
        self.A = data["A"]
        self.C = data["C"]

        self.M = data["M"]

        self.coverage = [[0 for _ in range(7)] for _ in range(self.N)]

        num_patterns = len(self.pattern[0])

        self.pattern_indexes = [
            [d for d in range(7) if self.pattern[d][p] == 1]
            for p in range(num_patterns)
        ]

        self.pattern_cost: list = [len(self.pattern_indexes[p]) for p in range(num_patterns)]

        self.cross_model_reach: list[dict[int, set[int]]] = [defaultdict(set) for _ in range(self.N)] # crossing - model = set(reachable crossings) 
        for n in range(self.N):
            distance_crossings: dict[int, list[int]] = defaultdict(list) # distance - list(crossings)
            for m in range(self.N):
                distance_crossings[self.M[n][m]].append(m)
            # distance_crossings.pop(0, None)
            distance_crossings.pop(50, None)
            sorted_distance_crossing = dict(sorted(distance_crossings.items()))
            
            for k in range(self.K):
                r = self.R[k]
                for dist, v in sorted_distance_crossing.items():
                    if dist <= r:
                        self.cross_model_reach[n][r].update(v)
        
            # print(f"Crossing {n} reachability:")
            # for model, covered in self.cross_model_reach[n].items():
            #     print(f"  Model with range {model} covers crossings {covered}")
            # print()
        
        return self

    def print_costs(self, cameras: solution_type):
        cost = 0
        try:
            _ = solver.simple_solver(solution)
            print(f"Valid solution.")
            for (k, p, c) in cameras:
                cost += self.P[k] + len(self.pattern_indexes[p])*self.C[k] 
                # print pattern
                pattern_str = ""
                for d in range(7):
                    pattern_str += str(self.pattern[d][p])
                print(f"camera: {k:3}, crossing: {c:3}, pattern {p:3}: {pattern_str}")
            print(f"Total cost: {cost}")
        except ValueError as e:
            for (k, p, c) in cameras:
                cost += self.P[k] + len(self.pattern_indexes[p])*self.C[k] 
                # print pattern
                pattern_str = ""
                for d in range(7):
                    pattern_str += str(self.pattern[d][p])
                print(f"camera: {k:3}, crossing: {c:3}, pattern {p:3}: {pattern_str}")
            print(f"Invalid solution: {e}")
            cost = 0

    def __str__(self):
        first = f"K = {self.K} N = {self.N} P = {self.P} R = {self.R} A = {self.A} C = {self.C}"
        last = ""
        for line in self.M:
            last += "   [ "
            for a in line:
                last += f"{a} " 
            last += "]\n"

        return first + "\nM: [\n" + last + "\n]"

    # A list of tuple[camera_model, pattern_index, crossing]
    def simple_solver(self, cameras: solution_type) -> int:
        covered_crossings: set = set()

        # at most one camera can be placed at a given crossing
        # we do this whithout and not checking "item not in set"
        # bc in this way we make only a single hash and lookup
        for _, _, crossing in cameras:
            covered_crossings_len = len(covered_crossings)
            covered_crossings.add(crossing)
            if covered_crossings_len == len(covered_crossings):
                raise ValueError(f"Crossing {crossing} selected twice")

        current_coverage = [set() for _ in range(7)]

        for camera, pattern_idx, crossing in cameras:
            # controlliamo la validità del pattern per la camera 
            # "key" selezionata
            if (
                pattern_idx > self.pattern_number[self.A[camera] - 2]
            ):  # a self.A sottraggo 2 perchè andiamo da 2 a 6 per l'autonomia
                raise ValueError(f"The pattern {pattern_idx} is not valid for camera {camera}")

            # we check that for each day in the pattern whether a camera can or not cover a crossing
            for day in range(7):
                if self.pattern[day][pattern_idx] == 1:
                    for i in range(self.N):
                        if self.R[camera] >= self.M[crossing][i] and self.M[crossing][i] < 50:
                            current_coverage[day].add(i)

        # verify complete coverage (all crossing must be always monitored)
        all_crossing = set(range(self.N))
        for day in range(7):
            if current_coverage[day] != all_crossing:
                raise ValueError(f"Day {day+1} not fully covered")

        # cost = purchase + operational, where operational is C times number of the days on
        purchase_cost = sum(self.P[cam_model] for cam_model, _, _ in cameras)
        operational_cost = sum(self.C[cam_model] * sum(self.pattern[day][pattern_idx] for day in range(7)) for cam_model, pattern_idx, _ in cameras)

        return purchase_cost + operational_cost

    def greedy(self) -> solution_type:
        cost: list[int] = [0 for _ in range(self.exponent)]
        solution: list[solution_type] = []
        coverage: list[list[list[int]]] = []

        for exp in range(1, self.exponent + 1):
            solution.append([])
            coverage.append([[0 for _ in range(7)] for _ in range(self.N)])
                
            total_slots_to_cover = self.N * 7
            current_covered = 0
            used_locations: set[int] = set()
            
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
                            days_active = self.pattern_cost[pattern_index]

                            move_cost = self.P[cam_index] + (days_active * self.C[cam_index])

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
                cost[exp - 1] += self.P[k] + len(self.pattern_indexes[p])*self.C[k] 
            # print("cost:", exp, cost[exp - 1])

        min_index = cost.index(min(cost))
        result = solution[min_index]
        self.coverage = coverage[min_index]

        return result

    def local_search_1(self, solution: solution_type) -> solution_type:
        
        target_index: list[list[int]] = [
            [0,2],[1,3],[2,4],[3,5],[4,6],[5,0],[6,1],
            [3,5],[4,6],[5,0],[6,1],[0,2],[1,3],[2,4],
            [0,3],[1,4],[2,5],[3,6],[4,0],[5,1],[6,2],
            [0,2,4],[1,3,5],[2,4,6],[3,5,0],[4,6,1],[5,0,2],[6,1,3],
            [0,2,3,5],[1,3,4,6],[2,4,5,0],[3,5,6,1],[4,6,0,2],[5,0,1,3],[6,1,2,4]
        ] # indexes of days for each pattern > 13 that can be removed to reduce cost
        target_patterns: list[list[int]] = [
            [1,0],[2,1],[3,2],[4,3],[5,4],[6,5],[0,6],
            [7,10],[8,11],[9,12],[10,13],[11,7],[12,8],[13,9],
            [15,14],[16,15],[17,16],[18,17],[19,18],[20,19],[21,20],
            [29,10,28],[30,11,29],[31,12,30],[32,13,31],[33,7,32],[34,8,33],[35,9,34],
            [36,28,32,35],[37,29,33,36],[38,30,34,37],[39,31,28,38],[40,32,29,39],[41,33,30,40],[42,34,31,41]
        ] # target patterns to switch to for each pattern > 13 after removing days
        target_availability: list[list[int]] = [
            [2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],
            [2,2],[2,2],[2,2],[2,2],[2,2],[2,2],[2,2],
            [3,3],[3,3],[3,3],[3,3],[3,3],[3,3],[3,3],
            [4,2,4],[4,2,4],[4,2,4],[4,2,4],[4,2,4],[4,2,4],[4,2,4],
            [5,3,3,5],[5,3,3,5],[5,3,3,5],[5,3,3,5],[5,3,3,5],[5,3,3,5],[5,3,3,5]
        ] # target min availability for each pattern > 13 after removing days

        solution_out: solution_type = solution.copy()
        # try to reduce patterns length
        for i, (model, pattern, crossing) in enumerate(solution_out):
            if pattern > 13: # only patterns with active time > 2
                mapping = self.cross_model_reach[crossing][self.R[model]]
                for day, target, availability in zip(target_index[pattern - 14], target_patterns[pattern - 14], target_availability[pattern - 14]):
                    if all(self.coverage[covered][day] > 1 for covered in mapping): # all covered more than once
                        possible_k = [k for k in range(self.K) if self.A[k] >= availability]
                        best_k = min(possible_k, key=lambda k: self.P[k] + self.pattern_cost[target] * self.C[k])
                        solution_out[i] = (best_k, target, crossing)
                        for covered in mapping: # update coverage
                            self.coverage[covered][day] -= 1

        # for n in range(self.N):
        #     print(self.coverage[n])
        # print()

        return solution_out
    
    def greedy_from_solution(
            self,
            solution: solution_type,
            coverage: list[list[int]]
    ) -> solution_type:
        cost: list[int] = [0 for _ in range(self.exponent)]
        solution: list[solution_type] = [solution for _ in range(self.exponent)]
        coverage: list[list[list[int]]] = [coverage for _ in range(self.exponent)]

        total_slots_to_cover = self.N * 7
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
                            days_active = self.pattern_cost[pattern_index]

                            move_cost = self.P[cam_index] + (days_active * self.C[cam_index])

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
                cost[exp - 1] += self.P[k] + len(self.pattern_indexes[p])*self.C[k] 
            # print("cost:", exp, cost[exp - 1])

        min_index = cost.index(min(cost))
        result = solution[min_index]
        self.coverage = coverage[min_index]

        return result

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
            cost: int = self.P[model] + len(self.pattern_indexes[pattern])*self.C[model]
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
        
        result = self.greedy_from_solution(solution_out, self.coverage)

        return result
    
    def local_search_0(
        self, 
        solution: solution_type,
        search_strategy: callable
    ) -> solution_type:
        cost_0: int = solver.simple_solver(solution)
        cost_1: int = cost_0 -1
        while (cost_0 > cost_1):
            cost_0 = cost_1
            solution = search_strategy(solution)
            cost_1 = solver.simple_solver(solution)
            print(f"cost: {cost_0:5} > {cost_1:5} | % {(cost_0 - cost_1)/cost_0 * 100:2.2f}%")

        return solution

if __name__ == "__main__":
    solver = GreedySolver(
        filename="random_output.dat",
        exponent=10 # greedy weight exponent
    )
    # print(solver)
    solution = solver.greedy()
    cost_0: int = solver.simple_solver(solution)
    print(f"cost: {cost_0:5}")
    solution = solver.local_search_1(solution)
    cost_1: int = solver.simple_solver(solution)
    print(f"cost: {cost_0:5} > {cost_1:5} | % {(cost_0 - cost_1)/cost_0 * 100:2.2f}%")
    solution = solver.local_search_0(solution, solver.local_search_2)
    cost_1: int = solver.simple_solver(solution)
    print(" FINAL RESULT ")
    print(f"cost: {cost_0:5} > {cost_1:5} | % {(cost_0 - cost_1)/cost_0 * 100:2.2f}%")
    solver.print_costs(solution)
    
