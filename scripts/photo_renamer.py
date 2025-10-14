from pathlib import Path
from utils.paths import DATA_DIR
from utils.csv_loader import load_csvs_from_dir
from utils.variable_namer import assign_variables
from utils.identifiers import IdentifierPool
from utils.photo_variant_handler import group_and_rename_variants


def run_photo_renamer(root: Path, test_mode: bool = False):
    """Rename photo files using IDs from CSVs."""
    # Paths
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

    # Load data
    datasets = load_csvs_from_dir(data_dir)
    if not datasets:
        print(f"No CSV files found in {data_dir}")
        return

    assigned_variables = assign_variables(datasets)
    id_pool = IdentifierPool(assigned_variables)
    id_pool.pool_file = pool_file
    id_pool._save()

    # Choose pool
    print("\nAvailable pools:", list(id_pool.pool.keys()))
    while True:
        pool_choice = input("Choose CSV pool to use for renaming (e.g., 'ctk', 'fnd'): ").strip()
        if pool_choice in id_pool.pool:
            break
        print("Invalid choice, try again.")

    df = assigned_variables[pool_choice]

    # Optional temporal coverage
    temporal_map = {
        "1": "1920-1929", "2": "1930-1939", "3": "1940-1949",
        "4": "1950-1959", "5": "1960-1969", "6": "1970-1979"
    }

    set_temporal = input("Do you want to set Temporal Coverage for this batch? (y/n): ").strip().lower() == "y"
    temporal_value = None
    if set_temporal:
        while True:
            for k, v in temporal_map.items():
                print(f"{k}: {v}")
            choice = input("Enter number (1-6): ").strip()
            if choice in temporal_map:
                temporal_value = temporal_map[choice]
                break
            print("Invalid selection. Try again.")

    # Rename photos
    photo_files = sorted(original_dir.glob("*.*"))
    if not photo_files:
        print(f"No photos found in {original_dir}")
        return

    df, total_renamed = group_and_rename_variants(
        photo_files=photo_files,
        id_pool=id_pool,
        pool_choice=pool_choice,
        df=df,
        renamed_dir=renamed_dir,
        set_temporal=set_temporal,
        temporal_value=temporal_value
    )

    csv_file_path = data_dir / f"{pool_choice}.csv"
    df.to_csv(csv_file_path, index=False)
    print(f"\nUpdated CSV saved: {csv_file_path}")
    print(f"Renamed {len(photo_files)} photos into {renamed_dir}")
