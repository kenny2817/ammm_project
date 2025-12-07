import os
import json
import re

# --- CONFIGURATION ---
# The folder where your .dat files are located
# (Make sure this path is correct relative to where you run this script)
data_folder = "test_case/final" 

# If you need the path in the JSON to look slightly different 
# (e.g. "test_case" vs "test_cases"), change this. Otherwise leave it equal to data_folder.
json_path_prefix = "test_case/final" 

output_data = []

# This acts as your internal counter 'x'
test_counter = 1 

# Get all .dat files and sort them so 'x' stays consistent between runs
try:
    files = sorted([f for f in os.listdir(data_folder) if f.endswith(".dat")])
except FileNotFoundError:
    print(f"Error: Directory '{data_folder}' not found.")
    files = []

for filename in files:
    # Use Regex to parse: output_seed_{w}_K{y}_N{z}.dat
    # Group 1 = Seed, Group 2 = K, Group 3 = N
    match = re.match(r"output_seed_(\d+)_K(\d+)_N(\d+)\.dat", filename)
    
    if match:
        seed = match.group(1) # w
        k_val = match.group(2) # y
        n_val = match.group(3) # z
        
        # Create the suffix part: Sw_Ky_Nz
        id_suffix = f"S{seed}_K{k_val}_N{n_val}"
        full_path = f"{json_path_prefix}/{filename}"

        # 1. Greedy Entry
        greedy_entry = {
            "id": f"test_{test_counter}_greedy_{id_suffix}",
            "type": "python",
            "data_file": full_path,
            "mode": "greedy",
            "exponent": 10
        }

        # 2. GRASP Entry
        grasp_entry = {
            "id": f"test_{test_counter}_grasp_{id_suffix}",
            "type": "python",
            "data_file": full_path,
            "mode": "grasp",
            "grasp_type": "full",
            "exponent": 2,
            "alpha": 0.1,
            "max_time": 60
        }

        # 3. OPL Entry
        opl_entry = {
            "id": f"test_{test_counter}_opl_{id_suffix}",
            "type": "opl",
            "model_file": "opl_models/project_optimized.mod",
            "data_file": full_path
        }

        # Add all three to the list
        output_data.extend([greedy_entry, grasp_entry, opl_entry])
        
        # Increment x for the next file
        test_counter += 1

#  Save to file
with open('final_test_config.json', 'w') as f:
    json.dump(output_data, f, indent=4)