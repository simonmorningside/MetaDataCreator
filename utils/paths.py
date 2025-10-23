# utils/paths.py
import os
from pathlib import Path

# Base directory in Documents
DOCS_BASE = Path(os.path.expanduser("~/Documents")) / "DigiHumanitiesAssist"

# Subdirectories
DATA_DIR = DOCS_BASE / "data"
DATA_TEST_DIR = DATA_DIR / "test"

PHOTOS_DIR = DOCS_BASE / "photos"
PHOTOS_ORIGINAL_DIR = PHOTOS_DIR / "original"
PHOTOS_RENAMED_DIR = PHOTOS_DIR / "renamed"
PHOTOS_TEST_ORIGINAL_DIR = PHOTOS_DIR / "test_original"
PHOTOS_TEST_RENAMED_DIR = PHOTOS_DIR / "test_renamed"


def ensure_all_dirs():
    """Create all required directories if missing."""
    folders = [
        DATA_DIR,
        DATA_TEST_DIR,
        PHOTOS_DIR,
        PHOTOS_ORIGINAL_DIR,
        PHOTOS_RENAMED_DIR,
        PHOTOS_TEST_ORIGINAL_DIR,
        PHOTOS_TEST_RENAMED_DIR,
    ]
    for folder in folders:
        folder.mkdir(parents=True, exist_ok=True)


def get_data_path(filename: str, test_mode=False) -> Path:
    """Return path inside data or data/test based on mode."""
    return (DATA_TEST_DIR if test_mode else DATA_DIR) / filename


def get_photo_path(filename: str, test_mode=False, renamed=False) -> Path:
    """Return correct photo path depending on test + renamed flags."""
    if test_mode:
        return (PHOTOS_TEST_RENAMED_DIR if renamed else PHOTOS_TEST_ORIGINAL_DIR) / filename
    return (PHOTOS_RENAMED_DIR if renamed else PHOTOS_ORIGINAL_DIR) / filename
