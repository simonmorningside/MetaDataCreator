# utils/variable_namer.py
from pathlib import Path
import json
from tkinter import simpledialog, messagebox
from .csv_loader import validate_variable_name
from .paths import DATA_DIR

# --- Variable map path ---
MAP_FILE = DATA_DIR / "variable_map.json"
DATA_DIR.mkdir(parents=True, exist_ok=True)

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

def assign_variables(datasets: dict[str, any], gui_mode: bool = False) -> dict[str, any]:
    """Assign variable names for CSV datasets. Only prompt for new ones."""
    variable_map = load_variable_map()
    assigned = {}

    for original_name, df in datasets.items():
        if original_name in variable_map:
            assigned[variable_map[original_name]] = df
            continue

        var_name = None
        while True:
            if gui_mode:
                var_name = simpledialog.askstring("Variable Name", f"Enter variable name for '{original_name}':")
                if var_name is None:
                    messagebox.showerror("Cancelled", "Variable assignment cancelled.")
                    return {}
            else:
                var_name = input(f"Enter variable name for '{original_name}': ").strip()

            if not validate_variable_name(var_name):
                msg = "Invalid variable name. Try again."
                if gui_mode:
                    messagebox.showerror("Invalid Name", msg)
                else:
                    print(msg)
                continue
            if var_name in assigned or var_name in variable_map.values():
                msg = "Variable name already used. Pick another."
                if gui_mode:
                    messagebox.showerror("Duplicate Name", msg)
                else:
                    print(msg)
                continue
            break

        assigned[var_name] = df
        variable_map[original_name] = var_name

    save_variable_map(variable_map)
    return assigned
