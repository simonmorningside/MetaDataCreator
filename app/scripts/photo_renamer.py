from pathlib import Path
from tkinter import messagebox, simpledialog
from app.utils.paths import (
    DATA_DIR,
    DATA_TEST_DIR,
    PHOTOS_ORIGINAL_DIR,
    PHOTOS_RENAMED_DIR,
    PHOTOS_TEST_ORIGINAL_DIR,
    PHOTOS_TEST_RENAMED_DIR,
)
from app.utils.csv_loader import load_csvs_from_dir
from app.utils.variable_namer import assign_variables
from app.utils.identifiers import IdentifierPool
from app.utils.photo_variant_handler import group_and_rename_variants
import json
import pandas as pd


def run_photo_renamer(test_mode: bool = False, gui_mode: bool = False):
    """
    Rename photo files using IDs from CSVs (CLI or GUI) and save a pool for AI captioning.
    Properly respects test_mode for all paths and pool usage.
    """

    # --- Paths ---
    if test_mode:
        data_dir = DATA_TEST_DIR
        original_dir = PHOTOS_TEST_ORIGINAL_DIR
        renamed_dir = PHOTOS_TEST_RENAMED_DIR
        pool_file = DATA_TEST_DIR / "available_ids_test.json"
        ai_pool_file = DATA_TEST_DIR / "ai_pool_test.json"
    else:
        data_dir = DATA_DIR
        original_dir = PHOTOS_ORIGINAL_DIR
        renamed_dir = PHOTOS_RENAMED_DIR
        pool_file = DATA_DIR / "available_ids.json"
        ai_pool_file = DATA_DIR / "ai_pool.json"

    renamed_dir.mkdir(parents=True, exist_ok=True)

    # --- Load CSV data ---
    datasets = load_csvs_from_dir(data_dir)
    if not datasets:
        msg = f"No CSV files found in {data_dir}"
        print(msg)
        if gui_mode:
            messagebox.showwarning("No Data Found", msg)
        return

    # --- Assign variables from CSVs ---
    assigned_variables = assign_variables(datasets)

    # --- Initialize ID pool (reads existing pool internally) ---
    id_pool = IdentifierPool(assigned_variables, test_mode=test_mode)
    id_pool.pool_file = pool_file  # points to the correct pool for this mode

    # --- Choose pool ---
    available_pools = list(id_pool.pool.keys())
    if not available_pools:
        msg = "No available ID pools found."
        print(msg)
        if gui_mode:
            messagebox.showerror("No Pools", msg)
        return

    print("\nAvailable pools:", available_pools)

    if gui_mode:
        pool_choice = simpledialog.askstring(
            "Choose Pool",
            f"Available pools:\n{', '.join(available_pools)}\n\nEnter pool name:",
        )
        if not pool_choice or pool_choice not in available_pools:
            messagebox.showerror("Invalid Choice", "That pool does not exist.")
            return
    else:
        while True:
            pool_choice = input("Choose CSV pool to use for renaming (e.g., 'ctk', 'fnd'): ").strip()
            if pool_choice in id_pool.pool:
                break
            print("Invalid choice, try again.")

    df = assigned_variables[pool_choice]

    # --- Optional Temporal Coverage ---
    temporal_map = {
        "1": "1920-1929",
        "2": "1930-1939",
        "3": "1940-1949",
        "4": "1950-1959",
        "5": "1960-1969",
        "6": "1970-1979",
    }

    if gui_mode:
        set_temporal = messagebox.askyesno("Set Temporal Coverage", "Do you want to set Temporal Coverage for this batch?")
    else:
        set_temporal = input("Do you want to set Temporal Coverage for this batch? (y/n): ").strip().lower() == "y"

    temporal_value = None
    if set_temporal:
        if gui_mode:
            options = "\n".join([f"{k}: {v}" for k, v in temporal_map.items()])
            while True:
                choice = simpledialog.askstring("Select Temporal Coverage", f"{options}\n\nEnter number (1–6):")
                if not choice:
                    return
                if choice in temporal_map:
                    temporal_value = temporal_map[choice]
                    break
                messagebox.showerror("Invalid Selection", "Please enter a number between 1 and 6.")
        else:
            while True:
                for k, v in temporal_map.items():
                    print(f"{k}: {v}")
                choice = input("Enter number (1-6): ").strip()
                if choice in temporal_map:
                    temporal_value = temporal_map[choice]
                    break
                print("Invalid selection. Try again.")

    # --- Rename photos ---
    photo_files = sorted(original_dir.glob("*.*"))
    if not photo_files:
        msg = f"No photos found in {original_dir}"
        print(msg)
        if gui_mode:
            messagebox.showwarning("No Photos Found", msg)
        return

    df, total_renamed = group_and_rename_variants(
        photo_files=photo_files,
        id_pool=id_pool,
        pool_choice=pool_choice,
        df=df,
        renamed_dir=renamed_dir,
        set_temporal=set_temporal,
        temporal_value=temporal_value,
    )

    # --- Save CSV ---
    csv_file_path = data_dir / f"{pool_choice}.csv"
    df.to_csv(csv_file_path, index=False)

    # --- Save AI Pool (only IDs that exist in renamed folder) ---
    ai_ids = [str(f) for f in df['ID'] if pd.notna(f) and list(renamed_dir.glob(f"{f}.*"))]
    with open(ai_pool_file, 'w') as f:
        json.dump(ai_ids, f, indent=2)

    print(f"AI pool saved: {ai_pool_file} ({len(ai_ids)} items)")

    summary_msg = (
        f"Updated CSV saved:\n{csv_file_path}\n"
        f"\nRenamed {len(photo_files)} photos into:\n{renamed_dir}\n"
        f"AI pool saved: {ai_pool_file}"
    )
    print(summary_msg)
    if gui_mode:
        messagebox.showinfo("Rename Complete", summary_msg)
