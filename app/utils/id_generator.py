import re
import pandas as pd
from pathlib import Path
from app.utils.paths import DATA_DIR, DATA_TEST_DIR

def generate_new_ids_for_csv(csv_name: str, num_new: int = 10, test_mode: bool = False) -> None:
    """
    Generate new IDs for a given CSV and append them as empty rows with IDs filled in.

    Args:
        csv_name (str): Name of the dataset (stem, no .csv extension)
        num_new (int): Number of new IDs to generate
        test_mode (bool): Whether to use test data directory
    """
    # Select correct data directory
    data_dir = DATA_TEST_DIR if test_mode else DATA_DIR
    csv_path = data_dir / f"{csv_name}.csv"

    if not csv_path.exists():
        print(f"CSV file not found: {csv_path}")
        return

    print(f"Generating new IDs for: {csv_path}")

    # Load the CSV
    df = pd.read_csv(csv_path)

    if "ID" not in df.columns:
        print(f"❌ 'ID' column not found in {csv_name}.csv")
        return

    # Extract prefix and max number using regex
    pattern = re.compile(r"^([A-Z]{3,5})(\d{5})$")
    valid_ids = df["ID"].dropna().astype(str)
    matches = [m for m in valid_ids.map(lambda x: pattern.match(x)) if m]

    if not matches:
        print(f"❌ No valid IDs found matching pattern (e.g. ABC00001) in {csv_name}.csv")
        return

    prefix = matches[0].group(1)
    max_num = max(int(m.group(2)) for m in matches)
    print(f"Current prefix: {prefix}, highest number: {max_num}")

    # Generate new IDs
    new_ids = [f"{prefix}{str(i).zfill(5)}" for i in range(max_num + 1, max_num + 1 + num_new)]

    # Create empty rows with only IDs
    new_rows = pd.DataFrame({col: [None] * num_new for col in df.columns})
    new_rows["ID"] = new_ids

    # Append and save
    df = pd.concat([df, new_rows], ignore_index=True)
    df.to_csv(csv_path, index=False)

    print(f"Added {num_new} new IDs to {csv_name}.csv")
    print(f"Last new ID: {new_ids[-1]}")
