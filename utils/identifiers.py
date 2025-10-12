# utils/identifiers.py
import json
from pathlib import Path
import pandas as pd

# Default pool files
DEFAULT_POOL_FILE = Path(__file__).resolve().parent.parent / "data" / "available_ids.json"
TEST_POOL_FILE = Path(__file__).resolve().parent.parent / "data" / "available_ids_test.json"


class IdentifierPool:
    def __init__(self,
                 csv_datasets: dict[str, pd.DataFrame],
                 id_col: str = "ID",
                 title_col: str = "Title",
                 rebuild: bool = False,
                 test_mode: bool = False):
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
            if self.id_col in df.columns and self.title_col in df.columns:
                available_ids = df[df[self.title_col].isna()][self.id_col].astype(str).tolist()
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
