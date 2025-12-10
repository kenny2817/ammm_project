import json

# --- CONFIGURATION SECTION ---
# Change these values to update your whole file
file_number = 0  # This controls the '2' in tuning_2.dat
max_time = 60    # Time limit in seconds

# Define the ranges you want to test
# Example: Test exponents 2, 5, and 10
exponents = [1, 2, 4, 8] 

# Example: Test alpha from 0.1 to 1.0
alphas = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
# -----------------------------

output_data = []

# 1. Add the Baseline (OPL) entry
# ID format: tuning_bl_{file_number}
baseline_entry = {
    "id": f"tuning_bl_{file_number}",
    "type": "opl",
    "model_file": "opl_models/p_01.mod",
    "data_file": f"test_case/tuning_{file_number}.dat"
}
output_data.append(baseline_entry)

# 2. Generate all combinations of Exponent and Alpha
for exp in exponents:
    for alpha in alphas:
        # Calculate the ID suffix (alpha * 10 converted to integer)
        # Using round() to avoid floating point errors (e.g., 0.3000000004)
        alpha_suffix = int(round(alpha * 10))
        
        entry = {
            "id": f"tuning_{file_number}_{exp}_{alpha_suffix}",
            "type": "python",
            "data_file": f"test_case/tuning_{file_number}.dat",
            "mode": "grasp",
            "grasp_type": "full",
            "exponent": exp,
            "alpha": alpha,
            "max_time": max_time
        }
        output_data.append(entry)

# 3. Write to a file
with open(f'json/config_tuning_{file_number}.json', 'w') as f:
    json.dump(output_data, f, indent=4)