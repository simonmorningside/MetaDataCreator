#!/usr/bin/env python3
import sys
from pathlib import Path
import shutil
import pandas as pd
import argparse

# --- Resolve project root ---
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from utils.paths import DATA_DIR
from utils.csv_loader import load_csvs_from_dir
from utils.variable_namer import assign_variables
from utils.identifiers import IdentifierPool

#read command line
parser = argparse.ArgumentParser(description="Rename photos using available IDs.")
parser.add_argument("--test", action="store_true", help="Use test folders and CSVs.")
args = parser.parse_args()

#setup based on test or not
if args.test:
    DATA_DIR_USED = ROOT / "data" / "test"
    ORIGINAL_DIR = ROOT / "photos" / "test_original"
    RENAMED_DIR = ROOT / "photos" / "test_renamed"
else:
    DATA_DIR_USED = DATA_DIR
    ORIGINAL_DIR = ROOT / "photos" / "original"
    RENAMED_DIR = ROOT / "photos" / "renamed"

RENAMED_DIR.mkdir(parents=True, exist_ok=True)

#load csvs and assign variables
datasets = load_csvs_from_dir(DATA_DIR_USED)
if not datasets:
    print(f"No CSV files found in {DATA_DIR_USED}")
    exit(0)

assigned_variables = assign_variables(datasets)
locals().update(assigned_variables)

#load id pool
id_pool = IdentifierPool(assigned_variables)
print("\nAvailable pools:", list(id_pool.pool.keys()))

#prompt for csv pool choice
while True:
    pool_choice = input("Choose CSV pool to use for renaming (e.g., 'ctk', 'fnd'): ").strip()
    if pool_choice in id_pool.pool:
        break
    print("Invalid choice, try again.")

df = assigned_variables[pool_choice]

#prompt for temp coverage
temporal_map = {
    "1": "1920-1929",
    "2": "1930-1939",
    "3": "1940-1949",
    "4": "1950-1959",
    "5": "1960-1969",
    "6": "1970-1979"
}

set_temporal = input("Do you want to set Temporal Coverage for this batch? (y/n): ").strip().lower() == "y"
if set_temporal:
    while True:
        print("Select Temporal Coverage:")
        for k, v in temporal_map.items():
            print(f"{k}: {v}")
        choice = input("Enter number (1-6): ").strip()
        if choice in temporal_map:
            temporal_value = temporal_map[choice]
            break
        print("Invalid selection. Try again.")

#rename photos
photo_files = sorted(ORIGINAL_DIR.glob("*.*"))
if not photo_files:
    print(f"No photos found in {ORIGINAL_DIR}")
    exit(0)

from utils.photo_variant_handler import group_and_rename_variants

df, total_renamed = group_and_rename_variants(
    photo_files=photo_files,
    id_pool=id_pool,
    pool_choice=pool_choice,
    df=df,
    renamed_dir=RENAMED_DIR,
    set_temporal=set_temporal,
    temporal_value=temporal_value if set_temporal else None
)


#save updated csv
csv_file_path = DATA_DIR_USED / f"{pool_choice}.csv"
df.to_csv(csv_file_path, index=False)
print(f"\nUpdated CSV saved: {csv_file_path}")
print(f"Renamed {len(photo_files)} photos into {RENAMED_DIR}")
