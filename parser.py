import re
import pprint

def parse_dat_file(filename: str) -> dict:
    """
    Parses the custom .dat file format from a string filename into a Python dictionary.
    
    It handles:
    1. Simple key-value pairs (e.g., K = 2;)
    2. Single-line arrays (e.g., P = [ 20 21 ];)
    3. Multi-line matrices (e.g., M = [ ... ];)
    """

    with open(filename, 'r') as f:
        content = f.read()
    
    data = {}
    
    # 1. Find and parse the 2D matrix 'M' (or any named matrix) first.
    # We look for the pattern key = [ ... ]; where the ... can span multiple lines.
    # re.DOTALL makes '.' match newline characters.
    # This regex finds the *first* matrix block. If you have multiple,
    # we'd need a loop (e.g., with re.finditer).
    
    # Regex breakdown:
    # (\w+)               - Capture group 1: The key (e.g., "M")
    # \s*=\s* - Equals sign, surrounded by optional whitespace
    # \[\n                - A literal bracket followed by a newline (start of matrix block)
    # (.*?)               - Capture group 2: The matrix content (non-greedy)
    # \n\];               - A newline, a closing bracket, and a semicolon (end of matrix block)
    matrix_match = re.search(r"(\w+)\s*=\s*\[\n(.*?)\n\];", content, re.DOTALL)
    
    if matrix_match:
        matrix_key = matrix_match.group(1)
        matrix_content = matrix_match.group(2)
        
        matrix = []
        # Split the content by lines
        lines = matrix_content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove the surrounding brackets for each row
            row_content = line.strip('[]')
            
            # Split by one or more spaces and convert to int
            try:
                row = [int(x) for x in re.split(r'\s+', row_content.strip())]
                matrix.append(row)
            except ValueError as e:
                print(f"Warning: Skipping malformed matrix row: {line} ({e})")
                
        data[matrix_key] = matrix
        
        # Remove the parsed matrix block from the original content
        # This is crucial so the simple parser doesn't get confused
        content = content[:matrix_match.start()] + content[matrix_match.end():]

    # 2. Parse the rest of the simple key-value and 1D-array pairs.
    
    # Remove all remaining newlines to make parsing easier
    content = content.replace('\n', ' ')
    
    # Split the remaining content by the statement terminator ';'
    assignments = content.split(';')
    
    for assignment in assignments:
        assignment = assignment.strip()
        if not assignment:
            continue
            
        # Split into key and value
        try:
            key, value = assignment.split('=', 1)
        except ValueError:
            print(f"Warning: Skipping malformed line: {assignment}")
            continue
            
        key = key.strip()
        value = value.strip()
        
        if not key or not value:
            continue
            
        if value.startswith('['):
            # This is a 1D array
            # Remove surrounding brackets
            array_content = value.strip('[]')
            # Split by spaces and convert to int
            try:
                data[key] = [int(x) for x in array_content.split()]
            except ValueError as e:
                 print(f"Warning: Skipping malformed array for key {key}: {value} ({e})")
        elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
            # This is a simple integer (handles negative numbers too)
            data[key] = int(value)
        else:
            # Could be a string or other type, but not in the example
             print(f"Warning: Skipping unknown value type for key {key}: {value}")
            
    return data

if __name__ == "__main__":    
    filename = 'project/project.1.dat'

    print("--- Parsing .dat content ---")
    parsed_data = parse_dat_file(filename)
    print("--- Parse complete ---")
    
    print("\nParsed data:")
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(parsed_data)