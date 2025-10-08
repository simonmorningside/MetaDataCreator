# utils/paths.py
from pathlib import Path

# Resolve the project root (two levels up from this file)
ROOT = Path(__file__).resolve().parent.parent

# Common directories
DATA_DIR = ROOT / "data"
OUTPUTS_DIR = ROOT / "outputs"
SCRIPTS_DIR = ROOT / "scripts"

def get_data_path(filename: str) -> Path:
    """Return a full path to a file inside /data."""
    return DATA_DIR / filename

def ensure_dir(path: Path):
    """Create directory if it doesn’t exist."""
    path.mkdir(parents=True, exist_ok=True)