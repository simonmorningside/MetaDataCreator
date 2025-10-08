from pathlib import Path
import json
from .csv_loader import validate_variable_name

MAP_FILE = Path(__file__).resolve().parent.parent / "data" / "variable_map.json"

def load_variable_map() -> dict:
    if MAP_FILE.exists():
        try:
            with open(MAP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_variable_map(variable_map: dict):
    MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MAP_FILE, "w", encoding="utf-8") as f:
        json.dump(variable_map, f, indent=2)

def assign_variables(datasets: dict[str, any]) -> dict[str, any]:
    """Assign variable names for CSV datasets. Only prompt for new ones."""
    variable_map = load_variable_map()
    assigned = {}

    for original_name, df in datasets.items():
        if original_name in variable_map:
            assigned[variable_map[original_name]] = df
            continue

        # Prompt user for new CSV
        while True:
            var_name = input(f"Enter variable name for '{original_name}': ").strip()
            if not validate_variable_name(var_name):
                print("Invalid variable name. Try again.")
                continue
            if var_name in assigned or var_name in variable_map.values():
                print("Variable name already used. Pick another.")
                continue
            break
        assigned[var_name] = df
        variable_map[original_name] = var_name

    save_variable_map(variable_map)
    return assigned
