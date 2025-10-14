#!/usr/bin/env python3
import argparse
from pathlib import Path
from scripts.metadata import run_load_and_inspect
from scripts.photo_renamer import run_photo_renamer


def main():
    parser = argparse.ArgumentParser(description="Photo Data Management App")
    parser.add_argument("action", choices=["inspect", "rename"], help="Action to perform")
    parser.add_argument("--test", action="store_true", help="Use test mode with test data and folders.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent

    if args.action == "inspect":
        run_load_and_inspect(root, test_mode=args.test)
    elif args.action == "rename":
        run_photo_renamer(root, test_mode=args.test)


if __name__ == "__main__":
    main()
