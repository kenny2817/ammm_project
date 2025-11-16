from pydantic import BaseModel, Field, model_validator
from parser import parse_dat_file


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

    # function to compute combinations of the patterns
    # that cover the whole weekly schedule
    def weekly_cover(
        self,
    ):
        return

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

    def greedy(self) -> None:

        return


if __name__ == "__main__":
    solver = GreedySolver()
    print(solver)
    cameras = [
            (0, 9, 1),
            (0, 11, 2),
    ]

    print(solver.simple_solver(cameras))

    solver.greedy()
