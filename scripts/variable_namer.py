#!/usr/bin/env python3

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))


from utils.paths import DATA_DIR
from utils.csv_loader import load_csvs_from_dir, validate_variable_name
import json

# Load all CSVs
datasets = load_csvs_from_dir(DATA_DIR)
if not datasets:
    exit(0)

# Prompt user for variable names
variable_map = {}
print("\n--- Assign variable names ---")
for original_name in datasets.keys():
    while True:
        var_name = input(f"Enter variable name for '{original_name}': ").strip()
        if not validate_variable_name(var_name):
            print("Invalid variable name. Try again.")
            continue
        if var_name in variable_map.values():
            print("Variable already used. Pick another.")
            continue
        break
    variable_map[original_name] = var_name

# Save mapping for later scripts
out_file = Path(__file__).resolve().parent.parent / "data" / "variable_map.json"
with open(out_file, "w") as f:
    json.dump(variable_map, f, indent=2)
print(f"\nVariable mapping saved to {out_file}")