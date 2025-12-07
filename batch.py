import sys
import json
import csv
import time
import statistics
import subprocess
import re
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass

# IMPORT YOUR SOLVER
# Assuming your previous code is in a file named 'main.py'
try:
    from main import GreedySolver
except ImportError:
    print("Error: Could not import GreedySolver. Make sure 'main.py' is in the same directory.")
    sys.exit(1)

@dataclass
class TestResult:
    test_id: str
    avg_cost: float
    min_cost: float
    max_cost: float
    avg_time: float
    min_time: float
    max_time: float
    success_rate: float

def run_python_solver(config):
    """
    Instantiates and runs the Python GreedySolver directly.
    """
    # 1. Setup
    data_file = config['data_file']
    exponent = config.get('exponent', 10)
    mode = config.get('mode', 'greedy')
    
    solver = GreedySolver(filename=str(data_file), exponent=exponent)
    
    start_time = time.perf_counter()
    cost = float('inf')
    
    # 2. Execution Logic (Mirroring your main.py logic)
    try:
        if mode == "greedy":
            # Try camera first, fallback to standard
            try:
                solution = solver.greedy_camera_first()
                cost = solver.check_validity_and_cost(solution)
            except Exception:
                solution = solver.greedy()
                cost = solver.check_validity_and_cost(solution)
            
            # Local Search
            solution = solver.local_search_0(solution, solver.local_search_3)
            solution = solver.local_search_0(solution, solver.local_search_2)
            cost = solver.check_validity_and_cost(solution)

        elif mode == "grasp":
            grasp_type = config.get('grasp_type', 'full')
            max_time = config.get('max_time', 60)
            alpha = config.get('alpha', 0.1)
            
            # Run GRASP
            _, cost = solver.run_grasp(grasp_type, max_time, alpha=alpha)
            
    except Exception as e:
        print(f"Error in {config['id']}: {e}")
        return float('inf'), time.perf_counter() - start_time, False

    elapsed = time.perf_counter() - start_time
    return cost, elapsed, True

def run_opl_solver(config):
    """
    Runs the external OPL binary via subprocess.
    """
    model_file = config['model_file']
    data_file = config['data_file']
    cmd = ["oplrun", model_file, data_file]
    
    start_time = time.perf_counter()
    
    try:
        # Capture output to parse result
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=config.get('max_time', 300))
        elapsed = time.perf_counter() - start_time
        
        # --- PARSING OPL OUTPUT ---
        # Adjust this Regex based on your actual OPL output
        # Example assumes output: "OBJECTIVE: 1250"
        match = re.search(r"OBJECTIVE:\s*(\d+)", result.stdout)
        if match:
            cost = int(match.group(1))
            return cost, elapsed, True
        else:
            # Fallback: Log output if parse fails
            with open(f"logs/{config['id']}_error.log", "w") as f:
                f.write(result.stdout)
                f.write(result.stderr)
            return float('inf'), elapsed, False

    except subprocess.TimeoutExpired:
        return float('inf'), config.get('max_time', 300), False
    except Exception as e:
        print(f"OPL Error {config['id']}: {e}")
        return float('inf'), 0, False

def execute_experiment_batch(config, iterations=3):
    """
    Runs a single experiment configuration N times and aggregates stats.
    """
    costs = []
    times = []
    success_count = 0

    print(f"Starting Job: {config['id']} ({config['type']})")

    for i in range(iterations):
        if config['type'] == 'python':
            c, t, success = run_python_solver(config)
        elif config['type'] == 'opl':
            c, t, success = run_opl_solver(config)
        else:
            print(f"Unknown type: {config['type']}")
            return None

        if success:
            costs.append(c)
            times.append(t)
            success_count += 1
    
    if not costs:
        return TestResult(config['id'], -1, -1, -1, -1, -1, -1, 0.0)

    return TestResult(
        test_id=config['id'],
        avg_cost=statistics.mean(costs),
        min_cost=min(costs),
        max_cost=max(costs),
        avg_time=statistics.mean(times),
        min_time=min(times),
        max_time=max(times),
        success_rate=(success_count/iterations)*100
    )

def main():
    if len(sys.argv) < 2:
        print("Usage: python batch.py <config_file.json> [max_workers]")
        print("Example: python batch.py experiments.json 4")
        sys.exit(1)

    config_file = sys.argv[1]
    
    if len(sys.argv) >= 3:
        max_workers = int(sys.argv[2])
    else:
        # Default behavior: Use all available CPUs 
        max_workers = os.cpu_count()

    print(f"--- Running with {max_workers} concurrent process(es) ---")
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Load configuration
    with open(config_file, 'r') as f:
        experiments = json.load(f)

    results = []
    
    # Run in parallel
    # Use max_workers based on your CPU cores
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_exp = {executor.submit(execute_experiment_batch, exp): exp for exp in experiments}
        
        for future in as_completed(future_to_exp):
            res = future.result()
            if res:
                results.append(res)
                print(f"Finished: {res.test_id} | Avg Cost: {res.avg_cost:.2f} | Avg Time: {res.avg_time:.4f}s")

    # Write Output to CSV
    output_file = "batch_results.csv"
    file_exists = os.path.isfile(output_file) and os.path.getsize(output_file) > 0

    with open(output_file, 'a', newline='') as csvfile:
        fieldnames = ['TestID', 'AvgCost', 'MinCost', 'MaxCost', 'AvgTime', 'MinTime', 'MaxTime', 'SuccessRate']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for r in results:
            writer.writerow({
                'TestID': r.test_id,
                'AvgCost': f"{r.avg_cost:.2f}",
                'MinCost': r.min_cost,
                'MaxCost': r.max_cost,
                'AvgTime': f"{r.avg_time:.4f}",
                'MinTime': f"{r.min_time:.4f}",
                'MaxTime': f"{r.max_time:.4f}",
                'SuccessRate': f"{r.success_rate:.0f}%"
            })
    
    print(f"\nBatch processing complete. Results saved to {output_file}")

if __name__ == "__main__":
    main()