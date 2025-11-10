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
int permut_cost[p in Permutation_range] = sum(d in Week) permutations[p][d];
// int permut_cost[Permutation_range] = [
//     2,2,2,2,2,2,2,
//     4,4,4,4,4,4,4,
//     3,3,3,3,3,3,3,
//     5,5,5,5,5,5,5,
//     4,4,4,4,4,4,4,
//     5,5,5,5,5,5,5,
//     6,6,6,6,6,6,6
// ];

// number of permutation for each availability
int permut_number[available_range] = [14,28,35,42,49];

// coverage power of a camera
int CanCover[k in K_range][i in N_range][j in N_range] = ((R[k] >= M[i][j]) && (M[i][j] < 50));

// helper to decide if p is good
int IsValidPermut[k in K_range][p in Permutation_range] = (p <= permut_number[A[k]]);

execute {
    cplex.threads = 1;

    for (var k in K_range) {
        var sumCanCover = 0;
        for (var i in N_range)
            for (var j in N_range)
                sumCanCover += CanCover[k][i][j];

        writeln(
          "k:", k, 
          " | P:", P[k], 
          " R:", R[k], 
          " A:", A[k], 
          " C:", C[k], 
          " | sum(CanCover):", sumCanCover
        );

        writeln(CanCover[k]);
    }
    writeln();
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
	for (var i in N_range) for(var k in K_range) for(var p in Permutation_range)
		if (x[k][i][p] == 1)
			writeln("crossing:",i," model:",k,permutations[p]);
}

