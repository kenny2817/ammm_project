from pydantic import BaseModel, Field, model_validator
from parser import parse_dat_file
import sys


class GreedySolver(BaseModel):
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

    pattern_number: list = [14, 28, 35, 42, 49]

    @model_validator(mode="after")
    def deserializer(self) -> "GreedySolver":
        
        data = parse_dat_file("data.dat")
        self.K = data["K"]
        self.N = data["N"]
        self.P = data["P"]
        self.R = data["R"]
        self.A = data["A"]
        self.C = data["C"]

        self.M = data["M"]

        return self

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
    def simple_solver(self, cameras: list[tuple[int, int, int]]):
        covered_crossings: set = set()

        # at most one camera can be placed at a given crossing
        # we do this whithout and not checking "item not in set"
        # bc in this way we make only a single hash and lookup
        for _, _, crossing in cameras:
            covered_crossings_len = len(covered_crossings)
            covered_crossings.add(crossing)
            if covered_crossings_len == len(covered_crossings):
                raise ValueError(f"Crossing {crossing} selected twice")

        coverage = [set() for _ in range(7)]

        for camera, pattern_idx, crossing in cameras:
            # controlliamo la validità del pattern per la camera 
            # "key" selezionata
            if (
                pattern_idx > self.pattern_number[self.A[camera - 2]]
            ):  # a self.A sottraggo 2 perchè andiamo da 2 a 6 per l'autonomia
                raise ValueError(f"The pattern {pattern_idx} is not valid for camera {camera}")

            # we check that for each day in the pattern whether a camera can or not cover a crossing
            for day in range(7):
                if self.pattern[day][pattern_idx] == 1:
                    for i in range(self.N):
                        if self.R[camera] >= self.M[crossing][i] and self.M[crossing][i] < 50:
                            coverage[day].add(i)

        # verify complete coverage (all crossing must be always monitored)
        all_crossing = set(range(self.N))
        for day in range(7):
            if coverage[day] != all_crossing:
                raise ValueError(f"Day {day+1} not fully covered")

        # cost = purchase + operational, where operational is C times number of the days on
        purchase_cost = sum(self.P[cam_model] for cam_model, _, _ in cameras)
        operational_cost = sum(self.C[cam_model] * sum(self.pattern[day][pattern_idx] for day in range(7)) for cam_model, pattern_idx, _ in cameras)

        return purchase_cost + operational_cost

    def greedy(self) -> list[tuple[int, int, int]]:
        coverage = [[False for _ in range(7)] for _ in range(self.N)]
        total_slots_to_cover = self.N * 7
        current_covered = 0
        solution: list[tuple[int, int, int]] = []
        used_locations = set()
        
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
                        days_active = 0
                        for d in range(7):
                            if self.pattern[d][pattern_index] == 1:
                                days_active += 1

                        move_cost = self.P[cam_index] + (days_active * self.C[cam_index])

                        gain = 0
                        for d in range(7):
                            if self.pattern[d][pattern_index] == 1:
                                for target in crossing_reachable:
                                    if not coverage[target][d]:
                                        gain += 1

                        if gain > 0:
                            ratio = move_cost / gain
                            # se il ratio è migliore di quello trovato precedentemente
                            # scelgo questa combinazione di camera, pattern e incrocio
                            if ratio < current_best_ratio:
                                current_best_ratio = ratio
                                best_move = (cam_index, pattern_index, loc, gain)

            if best_move:
                best_cam, best_pattern, best_loc, _ = best_move

                # aggiungo la combinazione all'insieme di soluzioni
                solution.append((best_cam, best_pattern, best_loc))
                used_locations.add(best_loc)

                reachable = []
                # aggiungo ai reachable gli incroci coperti dalla videocamera
                # posta all'incrocio best_loc
                for target in range(self.N):
                    if (self.M[best_loc][target] <= self.R[best_cam]) and (self.M[best_loc][target] < 50): 
                        reachable.append(target)

                for d in range(7):
                    if self.pattern[d][best_pattern] == 1:
                        # per ogni incrocio coperto (cioè presente in reachable)
                        # se non è presente in coverage lo aggiungo e incremento di 1
                        # il contatore dei current_covered
                        for target in reachable:
                            if not coverage[target][d]:
                                coverage[target][d] = True
                                current_covered += 1
            else:
                # se non sono riuscito a trovare una best move significa che
                # non avrò coperto alcuni incrocio in alcuni giorni della settimana
                print(f"Only covered {current_covered}/{total_slots_to_cover} slots.")
                break

        return solution


if __name__ == "__main__":
    solver = GreedySolver()
    print(solver)
    solution = solver.greedy()

    print(solution)
    try:
        cost = solver.simple_solver(solution)
        print(f"Valid solution. Total cost: {cost}")
    except ValueError as e:
        print(f"Invalid solution: {e}")

