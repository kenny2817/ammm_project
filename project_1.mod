// ** PLEASE ONLY CHANGE THIS FILE WHERE INDICATED **
// In particular, do not change the names of the OPL variables.

int             K = ...;
int 	  P[1..K] = ...;
int 	  R[1..K] = ...;
int 	  A[1..K] = ...;
int 	  C[1..K] = ...;

int             N = ...;
int M[1..N][1..N] = ...;

// Define here your decision variables and
// any other auxiliary OPL variables you need.
// You can run an execute block if needed.


// Preprocessing ==================================================================================
range Week = 1..7;
range Permutation_range = 1..49;
range available_range = 2..6;
range K_range = 1..K;
range N_range = 1..N;

// Week up time permutations
int permutations[Permutation_range][Week] = [
    [1,1,0,0,0,0,0],[0,1,1,0,0,0,0],[0,0,1,1,0,0,0],[0,0,0,1,1,0,0],[0,0,0,0,1,1,0],[0,0,0,0,0,1,1],[1,0,0,0,0,0,1], // 1 slot
    [1,1,0,0,1,1,0],[0,1,1,0,0,1,1],[1,0,1,1,0,0,1],[1,1,0,1,1,0,0],[0,1,1,0,1,1,0],[0,0,1,1,0,1,1],[1,0,0,1,1,0,1], // 2 slot
    [1,1,1,0,0,0,0],[0,1,1,1,0,0,0],[0,0,1,1,1,0,0],[0,0,0,1,1,1,0],[0,0,0,0,1,1,1],[1,0,0,0,0,1,1],[1,1,0,0,0,0,1], // 1 slot
    [1,1,0,1,1,1,0],[0,1,1,0,1,1,1],[1,0,1,1,0,1,1],[1,1,0,1,1,0,1],[1,1,1,0,1,1,0],[0,1,1,1,0,1,1],[1,0,1,1,1,0,1], // 2 slot
    [1,1,1,1,0,0,0],[0,1,1,1,1,0,0],[0,0,1,1,1,1,0],[0,0,0,1,1,1,1],[1,0,0,0,1,1,1],[1,1,0,0,0,1,1],[1,1,1,0,0,0,1], // 1 slot
    [1,1,1,1,1,0,0],[0,1,1,1,1,1,0],[0,0,1,1,1,1,1],[1,0,0,1,1,1,1],[1,1,0,0,1,1,1],[1,1,1,0,0,1,1],[1,1,1,1,0,0,1], // 1 slot
    [1,1,1,1,1,1,0],[0,1,1,1,1,1,1],[1,0,1,1,1,1,1],[1,1,0,1,1,1,1],[1,1,1,0,1,1,1],[1,1,1,1,0,1,1],[1,1,1,1,1,0,1]  // 1 slot
];
// cost in days
int permut_cost[Permutation_range] = [
    2,2,2,2,2,2,2,
    4,4,4,4,4,4,4,
    3,3,3,3,3,3,3,
    5,5,5,5,5,5,5,
    4,4,4,4,4,4,4,
    5,5,5,5,5,5,5,
    6,6,6,6,6,6,6
];
// number of permutation for each availability
int permut_number[available_range] = [14,28,35,42,49];

// coverage power of a camera
int CanCover[K_range][N_range][N_range];

// helper to decide if p is good
int IsValidPermut[K_range][Permutation_range]; 

execute {
    cplex.threads = 1;

    for(var k in K_range) for(var p in Permutation_range)
        IsValidPermut[k][p] = (p <= permut_number[A[k]]);
    for(var k in K_range) for(var j in N_range) for(var i in N_range)
        CanCover[k][i][j] = ((R[k] >= M[i][j]) && (M[i][j] < 50));
}

// Decision variables =============================================================================
dvar boolean x[K_range][N_range][Permutation_range];


// Objective function =============================================================================
minimize
  sum(k in K_range, i in N_range, p in Permutation_range) 
    x[k][i][p] * (P[k] + C[k] * permut_cost[p]);


// Constraints ====================================================================================
subject to {
  // Constraint 1: single camera
  forall(i in N_range)
    sum(k in K_range, p in Permutation_range) 
        x[k][i][p] <= 1;

  // Constraint 2: Autonomy constraint
  forall(k in K_range, i in N_range, p in Permutation_range)
    x[k][i][p] <= IsValidPermut[k][p]; 

  // Constraint 3: Full coverage
  forall(j in N_range, d in Week)
    sum(k in K_range, i in N_range, p in Permutation_range) 
      (x[k][i][p] * CanCover[k][i][j] * permutations[p][d]) >= 1;
}


execute {
    // writeln(x)
    // writeln(CanCover);
}

