#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))


from utils.paths import DATA_DIR
from utils.csv_loader import load_csvs_from_dir, validate_variable_name

# --- Load all CSVs ---
datasets = load_csvs_from_dir(DATA_DIR)

if not datasets:
    exit(0)

# --- Prompt user to assign variable names ---
assigned = {}
print("\n--- Assign variable names ---")
for original_name, df in datasets.items():
    while True:
        var_name = input(f"Enter variable name for '{original_name}': ").strip()
        if not validate_variable_name(var_name):
            print("Invalid variable name. Must be a valid Python identifier.")
            continue
        if var_name in assigned:
            print("Variable name already used. Pick another.")
            continue
        break
    assigned[var_name] = df

# Optional: assign to local namespace
locals().update(assigned)

# --- Print summary ---
print("\n--- Summary ---")
for var_name, df in assigned.items():
    cols = list(df.columns)
    print(f"{var_name}: {len(df)} rows, {len(cols)} columns")
    print(f"  Columns: {cols[:5]}{'...' if len(cols) > 5 else ''}")

# Example usage after assignment
# print(ctk.head())  # if user assigned 'ctk' to CTK.csv