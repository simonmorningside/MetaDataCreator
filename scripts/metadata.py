#!/usr/bin/env python3
import sys
from pathlib import Path
import pandas as pd


# Resolve project root
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))


from utils.paths import DATA_DIR
from utils.csv_loader import load_csvs_from_dir
from utils.variable_namer import assign_variables

#load csvs
datasets = load_csvs_from_dir(DATA_DIR)
if not datasets:
    print(f"No CSV files found in {DATA_DIR}")
    exit(0)


#assign variable names
assigned_variables = assign_variables(datasets)

locals().update(assigned_variables)

#prints a summary of all the items
print("\n--- CSV Summary ---")
for var_name, df in assigned_variables.items():
    cols = list(df.columns)
    print(f"{var_name}: {len(df)} rows, {len(cols)} columns")
    print(f"  Columns: {cols[:5]}{'...' if len(cols) > 5 else ''}")