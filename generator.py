import random
from dat_parser import parse_dat_file


def generate_dat_file(config_filename: str, output_filename: str, debug: bool = False) -> str:
    """
    Generates the content for a new .dat file based on config parameters.
    """

    config = parse_dat_file(config_filename)

    try:
        seed = config['SEED']
        K = config['K']
        N = config['N']
        maxP = config['maxP']
        maxC = config['maxC']
    except KeyError as e:
        print(f"Error: Missing required config parameter: {e}")
        return ""

    random.seed(seed)

    parts = []

    # Add K and N
    parts.append(f"K = {K};\n")
    parts.append(f"N = {N};\n\n")

    # P: 0 <= value <= maxP
    P = [random.randint(0, maxP) for _ in range(K)]
    # R: 0 < value < 50 (i.e., 1 to 49)
    R = [random.randint(1, 49) for _ in range(K)]
    # A: 1 < value < 7 (i.e., 2 to 6)
    A = [random.randint(2, 6) for _ in range(K)]
    # C: 0 <= value <= maxC
    C = [random.randint(0, maxC) for _ in range(K)]

    # Format arrays for the file
    parts.append(f"P = [ {' '.join(map(str, P))} ];\n")
    parts.append(f"R = [ {' '.join(map(str, R))} ];\n")
    parts.append(f"A = [ {' '.join(map(str, A))} ];\n")
    parts.append(f"C = [ {' '.join(map(str, C))} ];\n\n")

    parts.append("M = [\n")

    # Create the matrix in memory first to ensure symmetry
    matrix = [[0 for _ in range(N)] for _ in range(N)]

    for i in range(N):
        for j in range(i, N): # Iterate from diagonal to upper triangle
            if i == j:
                matrix[i][j] = 0
            else:
                # 0 < value < 51 (i.e., 1 to 50)
                val = random.randint(1, 50)
                matrix[i][j] = val  # Set upper triangle
                matrix[j][i] = val  # Set mirrored lower triangle
    # Now format the pre-generated matrix
    for i in range(N):
        row = matrix[i]

        # Format the row with consistent spacing
        # We find the max possible value (50) and pad to that width (2 chars)
        row_str = " ".join(f"{val: >2}" for val in row)
        parts.append(f"    [ {row_str} ]\n")

    parts.append("];\n")

    if debug:
        print("\nGenerated .dat content:")
        print("".join(parts))

    with open(output_filename, 'w') as f:
        f.write("".join(parts))


if __name__ == "__main__":
    config_filename = "test_case/p.dat"
    output_filename = "random_output1.dat"
    generate_dat_file(config_filename, output_filename, debug=True)
