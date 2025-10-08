#!/usr/bin/env python3
import sys
from pathlib import Path
import pandas as pd

#set root
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from utils.paths import DATA_DIR
from utils.csv_loader import load_csvs_from_dir
from utils.variable_namer import assign_variables
from utils.identifiers import IdentifierPool

#check for test flag
TEST_FLAG = False
if len(sys.argv) > 1 and sys.argv[1].lower() in ("--test", "test"):
    TEST_FLAG = True

#set data folder
data_dir = ROOT / "data" / "test" if TEST_FLAG else DATA_DIR
print(f"Using data folder: {data_dir}")

#load CSVs
datasets = load_csvs_from_dir(data_dir)
if not datasets:
    print(f"No CSV files found in {data_dir}")
    exit(0)

#assign variable names
assigned_variables = assign_variables(datasets)
locals().update(assigned_variables)

#ask if pool needs rebuilt
rebuild_input = input("Rebuild identifier pool from CSVs? (y/n): ").strip().lower()
rebuild_flag = rebuild_input == "y"

#optional csv summary
print("\n--- CSV Summary ---")
for var_name, df in assigned_variables.items():
    cols = list(df.columns)
    print(f"{var_name}: {len(df)} rows, {len(cols)} columns")
    print(f"  Columns: {cols[:5]}{'...' if len(cols) > 5 else ''}")

#optional column info
for var_name, df in assigned_variables.items():
    cols_to_show = [col for col in ["ID", "Title", "Temporal Coverage"] if col in df.columns]
    if not cols_to_show:
        print(f"{var_name}: no 'ID', 'Title', or 'Temporal Coverage' columns found.")
        continue
    print(f"\n{var_name}: info for columns {cols_to_show}")
    print(df[cols_to_show].info())

#set a pool based on test flag
from utils.identifiers import IdentifierPool
from utils.identifiers import POOL_FILE

#use a test pool for test
if TEST_FLAG:
    test_pool_file = POOL_FILE.parent / "available_ids_test.json"
else:
    test_pool_file = POOL_FILE

#create id pool
id_pool = IdentifierPool(assigned_variables, rebuild=rebuild_flag)
# Override the default pool file if test flag is set
if TEST_FLAG:
    id_pool.POOL_FILE = test_pool_file
    # Save immediately if rebuilding
    if rebuild_flag:
        id_pool._save()

#print available ids
print("\n--- Available ID Pools ---")
for csv_name, ids in id_pool.pool.items():
    print(f"{csv_name}: {len(ids)} available IDs")
    print(f"  {ids[:10]}{'...' if len(ids) > 10 else ''}")
