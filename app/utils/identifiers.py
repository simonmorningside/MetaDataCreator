# utils/identifiers.py
import json
from pathlib import Path
import pandas as pd
from utils.paths import DOCS_BASE

# Base data folder inside Documents
DOCUMENTS_DATA_DIR = DOCS_BASE / "data"
DOCUMENTS_TEST_DIR = DOCUMENTS_DATA_DIR / "test"

# Default pool files
DEFAULT_POOL_FILE = DOCUMENTS_DATA_DIR / "available_ids.json"
TEST_POOL_FILE = DOCUMENTS_TEST_DIR / "available_ids_test.json"


class IdentifierPool:
    def __init__(
        self,
        csv_datasets: dict[str, pd.DataFrame],
        id_col: str = "ID",
        title_col: str = "Title",
        rebuild: bool = False,
        test_mode: bool = False,
    ):
        """
        csv_datasets: dictionary of {variable_name: DataFrame} from assigned CSVs
        id_col: column name containing unique IDs
        title_col: column name to check if used/assigned
        rebuild: if True, rebuilds the pool from CSVs even if JSON exists
        test_mode: if True, uses a separate test pool file
        """
        self.id_col = id_col
        self.title_col = title_col
        self.csv_keys = list(csv_datasets.keys())
        self.pool_file = TEST_POOL_FILE if test_mode else DEFAULT_POOL_FILE

        # Ensure the folder exists
        self.pool_file.parent.mkdir(parents=True, exist_ok=True)

        # Rebuild or load
        if not rebuild and self.pool_file.exists():
            with self.pool_file.open("r", encoding="utf-8") as f:
                self.pool = json.load(f)
        else:
            self.pool = self._build_pool(csv_datasets)
            self._save()

    def _build_pool(self, datasets: dict[str, pd.DataFrame]) -> dict[str, list[str]]:
        pool = {}
        for name, df in datasets.items():
            # Determine which identifier column exists
            id_column_candidates = [self.id_col, "dcextended:identifier"]
            id_col_in_df = next((col for col in id_column_candidates if col in df.columns), None)

            if id_col_in_df:
                # Keep only rows where ID is not empty
                df_valid = df[df[id_col_in_df].notna()]

                # Columns to check for emptiness (exclude ID and file[mediasource])
                ignore_cols = {id_col_in_df, "file[mediasource]"}
                other_cols = [col for col in df_valid.columns if col not in ignore_cols]

                # Keep rows where all other columns are empty
                mask_empty = df_valid[other_cols].isna().all(axis=1)
                available_ids = df_valid.loc[mask_empty, id_col_in_df].astype(str).tolist()

                pool[name] = available_ids
            else:
                pool[name] = []

        return pool

    def get_available_ids(self, csv_name: str) -> list[str]:
        return self.pool.get(csv_name, [])

    def pop_identifier(self, csv_name: str) -> str | None:
        ids = self.pool.get(csv_name)
        if ids:
            identifier = ids.pop(0)
            self._save()
            return identifier
        return None

    def add_identifier(self, csv_name: str, identifier: str):
        if csv_name not in self.pool:
            self.pool[csv_name] = []
        self.pool[csv_name].append(identifier)
        self._save()

    def _save(self):
        self.pool_file.parent.mkdir(parents=True, exist_ok=True)
        with self.pool_file.open("w", encoding="utf-8") as f:
            json.dump(self.pool, f, indent=2)

    def summary(self):
        for csv_name, ids in self.pool.items():
            print(f"{csv_name}: {len(ids)} available IDs")

    def items(self):
        return self.pool.items()


def display_identifier_pools() -> str:
    """Return a formatted string showing the full contents of both normal and test identifier pools."""
    pools = []
    for label, pool_file in [("Main Pool", DEFAULT_POOL_FILE), ("Test Pool", TEST_POOL_FILE)]:
        if pool_file.exists():
            try:
                with pool_file.open("r", encoding="utf-8") as f:
                    pool_data = json.load(f)
                summary_lines = [f"=== {label} ({pool_file.name}) ==="]
                for name, ids in pool_data.items():
                    summary_lines.append(f"\n{name}: {len(ids)} IDs available")
                    if ids:
                        # Show all IDs, separated by commas (limit line length)
                        id_list = ", ".join(ids)
                        summary_lines.append(f"  IDs: {id_list}")
                    else:
                        summary_lines.append("  (No IDs available)")
                pools.append("\n".join(summary_lines))
            except Exception as e:
                pools.append(f"{label}: Failed to load ({e})")
        else:
            pools.append(f"{label}: No pool file found.")
    return "\n\n".join(pools)
