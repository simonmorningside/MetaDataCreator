# utils/csv_loader.py
from pathlib import Path
import pandas as pd

def load_csvs_from_dir(data_dir: Path) -> dict[str, pd.DataFrame]:
    """Load all CSV files in a directory into a dict keyed by filename stem, storing the path in df.attrs."""
    csv_files = sorted(data_dir.glob("*.csv"))
    datasets = {}
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            df.attrs["file_path"] = str(csv_file)  # attach full path
            datasets[csv_file.stem] = df
            print(f"Loaded {csv_file.name} ({len(df)} rows, {len(df.columns)} columns)")
            print(f"Path to CSV: {csv_file}")  # <-- added print
        except Exception as e:
            print(f"Failed to read {csv_file.name}: {e}")
    return datasets

def validate_variable_name(name: str) -> bool:
    """Check if a string is a valid Python identifier."""
    return name.isidentifier()