execute  {cplex.threads = 1;}

// Parameters =====================================================================================
int K=...; // number of models
int N=...; // number of crossings

range K_range = 1..K;
range N_range = 1..N;
range Week = 1..7;
range Permutation_range = 1..49;
range available_range = 2..6;

int P[K_range]=...; // price
int R[K_range]=...; // range [1,49]
int A[K_range]=...; // autonomy [2,6] - can work up to A days consecutively, must work at least 2 days
int C[K_range]=...; // power consumption [1,inf]

int M[N_range][N_range]=...; // crossing map


// Preprocessing ==================================================================================
//  combinantion of camera up time
    // since the camera up time is at least 2 the combination of up times are limited:
        // - 1 slot can be of all sizes [2,3,4,5,6]
            // [slot 1 ]
            // [   2   ]
            // [   3   ]
            // [   4   ]
            // [   5   ]
            // [   6   ]
        // - 2 slots can be of size [2,3] but that imply a limited size for the second one 2 <= slot_2.size <= 7-2-slot_1.size
            // [slot 1 ][slot 2 ]
            // [   2   ][  2,3  ]
            // [   3   ][   2   ]
    // the total cominations are: (A + A>=3)
        // - 1 slot: 7 * (A-1)
        // - 2 slot 7 * (1 + A>=3)
    // since 2 <= A <= 6, tot:
        // A = 2 then cominations = 2
        // A = 3 then cominations = 4
        // A = 4 then cominations = 5
        // A = 5 then cominations = 6
        // A = 6 then cominations = 7
    // order does matter: we count the cominations and the count how many times it is possible to shit them without repeatitions: 7 times     
    // the permutations are 7 times the cominations: [14,28,35,42,49]
        // A = 2 then permutations = 14
        // A = 3 then permutations = 28
        // A = 4 then permutations = 35
        // A = 5 then permutations = 42
        // A = 6 then permutations = 49

    // if harcoded they could return cover and cost in O(1)

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
int CanCover[N_range][N_range][K_range];

// helper to decide if p is good
int IsValidPermut[K_range][Permutation_range]; 

execute {
    for(var k in K_range) for(var p in Permutation_range)
        IsValidPermut[k][p] = (p <= permut_number[A[k]]);
    for(var k in K_range) for(var j in N_range) for(var i in N_range)
        CanCover[i][j][k] = ((R[k] >= M[i][j]) && (M[i][j] < 50));
}


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
    sum(k in K_range, p in Permutation_range) 
        x[i][k][p] <= 1;

  // Constraint 2: Autonomy constraint
  forall(i in N_range, k in K_range, p in Permutation_range)
    x[i][k][p] <= IsValidPermut[k][p]; 

  // Constraint 3: Full coverage
  forall(j in N_range, d in Week)
    sum(i in N_range, k in K_range, p in Permutation_range) 
      (x[i][k][p] * CanCover[i][j][k] * permutations[p][d]) >= 1;
}

// execute {
//     writeln(x);
//     writeln(CanCover);
// }