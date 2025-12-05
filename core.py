from collections import defaultdict
from typing import DefaultDict
from pydantic import BaseModel, Field, model_validator, computed_field # type: ignore
from dat_parser import parse_dat_file
from common_types import solution_type
from constants import PATTERN, PATTERN_NUMBER

class SolverBase(BaseModel):

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

    pattern: list[list[int]] = PATTERN
    pattern_number: list = PATTERN_NUMBER
    pattern_indexes: list[list[int]] = Field(default_factory=list)
    pattern_cost: list[int] = Field(default_factory=list)
    coverage: list[list[int]] = Field(default_factory=list)
    cross_model_reach: list[DefaultDict[int, set[int]]] = Field(default_factory=list)
    cross_reach_exclusive: list[DefaultDict[int, set[int]]] = Field(default_factory=list)
    ranges : list[int] = Field(default_factory=list)

    @model_validator(mode="after")
    def deserializer(self) -> "SolverBase":
        self.get_from_file()

        self.coverage = [[0 for _ in range(7)] for _ in range(self.N)]

        num_patterns = len(self.pattern[0])

        self.pattern_indexes = [
            [d for d in range(7) if self.pattern[d][p] == 1]
            for p in range(num_patterns)
        ]

        self.pattern_cost = [len(self.pattern_indexes[p]) for p in range(num_patterns)]

        self.cross_model_reach = [defaultdict(set) for _ in range(self.N)] # crossing - model = set(reachable crossings) 
        self.cross_reach_exclusive = [defaultdict(set) for _ in range(self.N)]

        self.ranges: list[int] = sorted(set(self.R))
        for n in range(self.N):
            distance_crossings: dict[int, list[int]] = defaultdict(list) # distance - list(crossings)
            for m in range(self.N):
                distance_crossings[self.M[n][m]].append(m)
            # distance_crossings.pop(0, None)
            distance_crossings.pop(50, None)
            
            seen_crossings: set[int] = set()
            for r in self.ranges:
                for dist, v in distance_crossings.items():
                    if dist <= r:
                        self.cross_model_reach[n][r].update(v)
        
                current_reach = self.cross_model_reach[n][r]                
                self.cross_reach_exclusive[n][r] = current_reach - seen_crossings                
                seen_crossings.update(current_reach)
                    
            # print(f"Crossing {n} reachability:")
            # for model, covered in self.cross_model_reach[n].items():
            #     print(f"  Model with range {model} covers crossings {covered}")
            # print()
        
        return self

    def get_from_file(self):
        data = parse_dat_file(self.filename)
        self.K = data["K"]
        self.N = data["N"]
        self.P = data["P"]
        self.R = data["R"]
        self.A = data["A"]
        self.C = data["C"]
        self.M = data["M"]

    def compute_cost(self, camera_model: int, pattern_index: int) -> int:
        return self.P[camera_model] + self.pattern_cost[pattern_index] * self.C[camera_model]

    def print_costs(self, cameras: solution_type):
        cost = 0
        try:
            _ = self.check_validity_and_cost(cameras)
            print(f"Valid solution.")
            for (k, p, c) in cameras:
                cost += self.compute_cost(k, p)
                # print pattern
                pattern_str = ""
                for d in range(7):
                    pattern_str += str(self.pattern[d][p])
                print(f"camera: {k:3}, crossing: {c:3}, pattern {p:3}: {pattern_str}")
            print(f"Total cost: {cost}")
        except ValueError as e:
            for (k, p, c) in cameras:
                cost += self.compute_cost(k, p)
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
    def check_validity_and_cost(self, cameras: solution_type) -> int:
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

        cost = sum(self.compute_cost(cam_model, pattern_idx) for cam_model, pattern_idx, _ in cameras)

        return cost
