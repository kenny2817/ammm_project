
execute {
    cplex.threads = 1;
}

// Parameters =====================================================================================
int K             = ...;
int P[1..K]       = ...;
int R[1..K]       = ...;
int A[1..K]       = ...;
int C[1..K]       = ...;

int N             = ...;
int M[1..N][1..N] = ...;

// Preprocessing ==================================================================================
range Week = 1..7;
range Permutation_range = 1..49;
range available_range = 2..6;
range K_range = 1..K;
range N_range = 1..N;

// Week up time permutations
int permutations[Week][Permutation_range] = [
  [1,0,0,0,0,0,1, 1,0,1,1,0,0,1, 1,0,0,0,0,1,1, 1,0,1,1,1,0,1, 1,0,0,1,1,1,1, 1,0,1,1,1,1,1, 1,0,1,1,1,1,1], // Day 1
  [1,1,0,0,0,0,0, 1,1,0,1,1,0,0, 1,1,0,0,0,0,1, 1,1,0,1,1,1,0, 1,1,0,0,1,1,1, 1,1,0,1,1,1,1, 1,1,0,1,1,1,1], // Day 2
  [0,1,1,0,0,0,0, 0,1,1,0,1,1,0, 1,1,1,0,0,0,0, 0,1,1,0,1,1,1, 1,1,1,0,0,1,1, 1,1,1,0,1,1,1, 1,1,1,0,1,1,1], // Day 3
  [0,0,1,1,0,0,0, 0,0,1,1,0,1,1, 0,1,1,1,0,0,0, 1,0,1,1,0,1,1, 1,1,1,1,0,0,1, 1,1,1,1,0,1,1, 1,1,1,1,0,1,1], // Day 4
  [0,0,0,1,1,0,0, 1,0,0,1,1,0,1, 0,0,1,1,1,0,0, 1,1,0,1,1,0,1, 1,1,1,1,1,0,0, 1,1,1,1,1,0,1, 1,1,1,1,1,0,1], // Day 5
  [0,0,0,0,1,1,0, 1,1,0,0,1,1,0, 0,0,0,1,1,1,0, 1,1,1,0,1,1,0, 0,1,1,1,1,1,0, 1,1,1,1,1,1,0, 1,1,1,1,1,1,0], // Day 6
  [0,0,0,0,0,1,1, 0,1,1,0,0,1,1, 0,0,0,0,1,1,1, 0,1,1,1,0,1,1, 0,0,1,1,1,1,1, 0,1,1,1,1,1,1, 0,1,1,1,1,1,1]  // Day 7
];

// cost in days
int permut_cost[p in Permutation_range] = sum(d in Week) permutations[d][p];

// number of permutation for each availability
int permut_number[available_range] = [14,28,35,42,49];

// coverage power of a camera
int CanCover[j in N_range][i in N_range][k in K_range] = ((R[k] >= M[i][j]) && (M[i][j] < 50));

// helper to decide if p is good
int IsValidPermut[k in K_range][p in Permutation_range] = (p <= permut_number[A[k]]);

// Decision variables =============================================================================
dvar boolean x[N_range][K_range][Permutation_range];

// Objective function =============================================================================
minimize
  sum(i in N_range, k in K_range, p in Permutation_range) 
    x[i][k][p] * (P[k] + C[k] * permut_cost[p]);

// Constraints ====================================================================================
subject to {
  // Constraint 1: single camera
  forall(i in N_range)
    sum(k in K_range, p in Permutation_range) x[i][k][p] <= 1;

  // Constraint 2: Autonomy constraint
  forall(i in N_range,k in K_range,  p in Permutation_range)
    x[i][k][p] <= IsValidPermut[k][p]; 

  // Constraint 3: Full coverage
  forall(j in N_range, d in Week)
    sum(i in N_range,k in K_range,  p in Permutation_range) 
      (x[i][k][p] * CanCover[j][i][k] * permutations[d][p]) >= 1;
}


execute {
	for (var i in N_range) for(var k in K_range) for(var p in Permutation_range)
		if (x[i][k][p] == 1) {
			write("crossing:",i," model:",k, "\t[");
      for (var d in Week)
        write(" ", permutations[d][p]);
      writeln(" ]");
    }
}
