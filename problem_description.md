# MILP formulation

## Parameters

### Inputs

- `K` - number of models of camera available
- `N` - number of crossings
- `maxP` - maximum cost for the purchase of a model
- `maxR` - maximum range of a model
- `maxA` - maximum number of consecutive days a camera can be kept on
- `maxC` - maximum cost per day of a model
- `maxM` - maximum visibility of a crossing compared to other corrsing

### Internal

- `P` - cost of each model - index: k
- `R` - range of each model - index: k
- `A` - availability of each value - index: k
- `C` - cost per day of each model - index: k
- `M` - map of visibility between crossings - indexes: n, n

### Preprocessing

- `permutations` - hardcoded all the permutations available based on the problem specification - indexes: p, w
- `permut_cost` - the cost in terms of days of each permutation, basically the sum of up days - index: p
- `permut_number` - number of permutations available based on the availability - index: a
- `can_cover` - for aeach camera what can be covered - indexes: k, n, n
- `permut_valid` - uses permut_number to preprocess the available permutations - indexes: k, p

## Decison Variables

- `x` - boolean - which model, which crossing, which permutation is active - indexes: k, n, p

## Objective Functions

- minimize costs - cost is composed of purchase cost and daily cost for each crossing that has an active model

## Constraints

- `single camera per crossing` - each crossing can only have one model
- `autonomy contraints` - cameras can at most be active as much as their own autonomy
- `full coverage` - all the crossings must be covered all the time
