from pathlib import Path
from tkinter import messagebox, simpledialog
from utils.paths import DATA_DIR
from utils.csv_loader import load_csvs_from_dir
from utils.variable_namer import assign_variables
from utils.identifiers import IdentifierPool
from utils.photo_variant_handler import group_and_rename_variants


def run_photo_renamer(root: Path, test_mode: bool = False, gui_mode: bool = False):
    """Rename photo files using IDs from CSVs (CLI or GUI)."""

    # --- Paths ---
    if test_mode:
        data_dir = root / "data" / "test"
        original_dir = root / "photos" / "test_original"
        renamed_dir = root / "photos" / "test_renamed"
        pool_file = root / "data" / "available_ids_test.json"
    else:
        data_dir = DATA_DIR
        original_dir = root / "photos" / "original"
        renamed_dir = root / "photos" / "renamed"
        pool_file = root / "data" / "available_ids.json"

    renamed_dir.mkdir(parents=True, exist_ok=True)

    # --- Load data ---
    datasets = load_csvs_from_dir(data_dir)
    if not datasets:
        msg = f"No CSV files found in {data_dir}"
        print(msg)
        if gui_mode:
            messagebox.showwarning("No Data Found", msg)
        return

    assigned_variables = assign_variables(datasets)
    id_pool = IdentifierPool(assigned_variables)
    id_pool.pool_file = pool_file
    id_pool._save()

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
        if not pool_choice:
            return
        if pool_choice not in available_pools:
            messagebox.showerror("Invalid Choice", "That pool does not exist.")
            return
    else:
        while True:
            pool_choice = input("Choose CSV pool to use for renaming (e.g., 'ctk', 'fnd'): ").strip()
            if pool_choice in id_pool.pool:
                break
            print("Invalid choice, try again.")

    df = assigned_variables[pool_choice]

    # --- Temporal coverage ---
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

    # --- Save results ---
    csv_file_path = data_dir / f"{pool_choice}.csv"
    df.to_csv(csv_file_path, index=False)

    summary_msg = f"Updated CSV saved:\n{csv_file_path}\n\nRenamed {len(photo_files)} photos into:\n{renamed_dir}"
    print(summary_msg)
    if gui_mode:
        messagebox.showinfo("Rename Complete", summary_msg)
