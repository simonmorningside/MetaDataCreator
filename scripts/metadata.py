from pathlib import Path
from utils.paths import DATA_DIR
from utils.csv_loader import load_csvs_from_dir
from utils.variable_namer import assign_variables
from utils.identifiers import IdentifierPool


def run_load_and_inspect(root: Path, test_mode: bool = False):
    """Load CSVs, inspect them, and optionally rebuild identifier pool."""
    data_dir = root / "data" / "test" if test_mode else DATA_DIR
    print(f"Using data folder: {data_dir}")

    # Load CSVs
    datasets = load_csvs_from_dir(data_dir)
    if not datasets:
        print(f"No CSV files found in {data_dir}")
        return None, None

    assigned_variables = assign_variables(datasets)

    # CSV summary
    print("\n--- CSV Summary ---")
    for var_name, df in assigned_variables.items():
        cols = list(df.columns)
        print(f"{var_name}: {len(df)} rows, {len(cols)} columns")
        print(f"  Columns: {cols[:5]}{'...' if len(cols) > 5 else ''}")

    # Optional column info
    '''
    for var_name, df in assigned_variables.items():
        cols_to_show = [c for c in ["ID", "Title", "Temporal Coverage"] if c in df.columns]
        if cols_to_show:
            print(f"\n{var_name}: info for columns {cols_to_show}")
            print(df[cols_to_show].info())
        else:
            print(f"{var_name}: no 'ID', 'Title', or 'Temporal Coverage' columns found.")
    '''

    rebuild_flag = input("Rebuild identifier pool from CSVs? (y/n): ").strip().lower() == "y"
    id_pool = IdentifierPool(assigned_variables, rebuild=rebuild_flag, test_mode=test_mode)

    # Print available IDs
    print("\n--- Available ID Pools ---")
    for csv_name, ids in id_pool.pool.items():
        print(f"{csv_name}: {len(ids)} available IDs")
        print(f"  {ids[:10]}{'...' if len(ids) > 10 else ''}")

    return assigned_variables, id_pool
