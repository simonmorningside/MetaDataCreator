# utils/identifiers.py
import json
from pathlib import Path
import pandas as pd

POOL_FILE = Path(__file__).resolve().parent.parent / "data" / "available_ids.json"

class IdentifierPool:
    def __init__(self, csv_datasets: dict[str, pd.DataFrame],
                 id_col: str = "ID",
                 title_col: str = "Title",
                 rebuild: bool = False):
        """
        csv_datasets: dictionary of {variable_name: DataFrame} from assigned CSVs
        id_col: column name containing unique IDs
        title_col: column name to check if used/assigned
        rebuild: if True, rebuilds the pool from CSVs even if JSON exists
        """
        self.id_col = id_col
        self.title_col = title_col
        self.csv_keys = list(csv_datasets.keys())

        # Force rebuild or load existing pool
        if not rebuild and POOL_FILE.exists():
            with POOL_FILE.open("r", encoding="utf-8") as f:
                self.pool = json.load(f)
        else:
            # Build pool from CSVs
            self.pool = self._build_pool(csv_datasets)
            self._save()

    def _build_pool(self, datasets: dict[str, pd.DataFrame]) -> dict[str, list[str]]:
        """
        Creates a dictionary: {csv_name: [available IDs]}
        Only includes rows where title_col is empty/missing.
        """
        pool = {}
        for name, df in datasets.items():
            if self.id_col in df.columns and self.title_col in df.columns:
                available_ids = df[df[self.title_col].isna()][self.id_col].astype(str).tolist()
                pool[name] = available_ids
            else:
                pool[name] = []
        return pool

    def get_available_ids(self, csv_name: str) -> list[str]:
        """Return the current list of available IDs for a specific CSV."""
        return self.pool.get(csv_name, [])

    def pop_identifier(self, csv_name: str) -> str | None:
        """Pop the first available ID from the pool and save. Returns None if empty."""
        ids = self.pool.get(csv_name)
        if ids:
            identifier = ids.pop(0)
            self._save()
            return identifier
        return None

    def add_identifier(self, csv_name: str, identifier: str):
        """Add an ID back into the pool (e.g., if an image is deleted)."""
        if csv_name not in self.pool:
            self.pool[csv_name] = []
        self.pool[csv_name].append(identifier)
        self._save()

    def _save(self):
        """Save current pool to JSON."""
        POOL_FILE.parent.mkdir(parents=True, exist_ok=True)
        with POOL_FILE.open("w", encoding="utf-8") as f:
            json.dump(self.pool, f, indent=2)

    def summary(self):
        """Print a quick summary of available IDs."""
        for csv_name, ids in self.pool.items():
            print(f"{csv_name}: {len(ids)} available IDs")

    def items(self):
        """Return iterable of (csv_name, list_of_available_ids)."""
        return self.pool.items()
