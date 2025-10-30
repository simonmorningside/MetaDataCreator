from pathlib import Path
from tkinter import messagebox, simpledialog
from app.utils.paths import DATA_DIR, DATA_TEST_DIR
from app.utils.csv_loader import load_csvs_from_dir
from app.utils.variable_namer import assign_variables
from app.utils.identifiers import IdentifierPool


def run_load_and_inspect(test_mode: bool = False, gui_mode: bool = False):
    """Load CSVs, inspect them, and optionally rebuild identifier pool."""

    # --- Paths ---
    data_dir = DATA_TEST_DIR if test_mode else DATA_DIR
    print(f"Using data folder: {data_dir}")

    # --- Load CSVs ---
    datasets = load_csvs_from_dir(data_dir)
    if not datasets:
        msg = f"No CSV files found in {data_dir}"
        print(msg)
        if gui_mode:
            messagebox.showwarning("No Data", msg)
        return None, None

    # --- Assign variable names (GUI popups if gui_mode) ---
    assigned_variables = assign_variables(datasets, gui_mode=gui_mode)

    # --- Build summary text ---
    summary_lines = ["--- CSV Summary ---"]
    for var_name, df in assigned_variables.items():
        cols = list(df.columns)
        summary_lines.append(f"{var_name}: {len(df)} rows, {len(cols)} columns")
        summary_lines.append(f"  Columns: {cols[:5]}{'...' if len(cols) > 5 else ''}")

    summary_text = "\n".join(summary_lines)
    print(summary_text)
    if gui_mode:
        messagebox.showinfo("CSV Summary", summary_text)

    # --- Rebuild pool prompt ---
    if gui_mode:
        rebuild_flag = messagebox.askyesno("Rebuild Pool", "Rebuild identifier pool from CSVs?")
    else:
        rebuild_flag = input("Rebuild identifier pool from CSVs? (y/n): ").strip().lower() == "y"

    # --- Initialize IdentifierPool ---
    id_pool = IdentifierPool(assigned_variables, rebuild=rebuild_flag, test_mode=test_mode)

    # --- Summarize ID pools ---
    pool_lines = ["--- Available ID Pools ---"]
    for csv_name, ids in id_pool.pool.items():
        pool_lines.append(f"{csv_name}: {len(ids)} available IDs")
        pool_lines.append(f"  {ids[:10]}{'...' if len(ids) > 10 else ''}")

    pool_text = "\n".join(pool_lines)
    print(pool_text)
    if gui_mode:
        messagebox.showinfo("Available ID Pools", pool_text)

    return assigned_variables, id_pool
