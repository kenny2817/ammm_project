# ammm_project

// combinantion of camera up time
// since the camera up time is at least 2 the combination of up times are limited:
// - 1 slot can be of all sizes [2,3,4,5,6]
// [slot 1 ]
// [ 2 ]
// [ 3 ]
// [ 4 ]
// [ 5 ]
// [ 6 ]
// - 2 slots can be of size [2,3] but that imply a limited size for the second one 2 <= slot_2.size <= 7-2-slot_1.size
// [slot 1 ][slot 2 ]
// [ 2 ][ 2,3 ]
// [ 3 ][ 2 ]
// the total cominations are: (A + A>=3)
// - 1 slot: 7 _ (A-1)
// - 2 slot 7 _ (1 + A>=3)
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
