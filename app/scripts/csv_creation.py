#!/usr/bin/env python3
import csv
from tkinter import Tk, simpledialog, messagebox
from app.utils.paths import DATA_DIR, DATA_TEST_DIR, ensure_all_dirs

# --- Ensure folders exist ---
ensure_all_dirs()

# --- Setup Tkinter root ---
root = Tk()
root.withdraw()  # hide main window

# --- Ask user for CSV filename ---
csv_name = simpledialog.askstring("CSV Creator", "Enter the name of the new CSV file (without extension):")
if not csv_name:
    messagebox.showerror("Cancelled", "CSV creation cancelled.")
    exit()

# --- Ask for number of additional columns ---
while True:
    try:
        num_cols = simpledialog.askinteger("CSV Creator", "How many additional columns besides ID and Title?")
        if num_cols is None:
            raise KeyboardInterrupt
        if num_cols < 0:
            raise ValueError
        break
    except ValueError:
        messagebox.showwarning("Invalid Input", "Please enter a valid non-negative integer.")
    except KeyboardInterrupt:
        messagebox.showinfo("Cancelled", "CSV creation cancelled.")
        exit()

# --- Ask for additional column names ---
additional_columns = []
for i in range(num_cols):
    while True:
        col_name = simpledialog.askstring("CSV Creator", f"Enter name for column {i+1}:")
        if col_name and col_name.strip():
            additional_columns.append(col_name.strip())
            break
        messagebox.showwarning("Invalid Input", "Column name cannot be empty.")

# --- Ask for 3–5 letter prefix for unique IDs ---
while True:
    prefix = simpledialog.askstring("CSV Creator", "Enter 3–5 letter prefix for unique IDs:")
    if prefix and 3 <= len(prefix.strip()) <= 5 and prefix.isalpha():
        prefix = prefix.upper()
        break
    messagebox.showwarning("Invalid Input", "Prefix must be 3 to 5 letters only.")

# --- CSV fieldnames ---
fieldnames = ["ID", "Title"] + additional_columns
num_rows = 2000

# --- Function to create CSV ---
def create_csv(path):
    with open(path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for i in range(num_rows):
            unique_id = f"{prefix}{i:05d}"
            row = {"ID": unique_id, "Title": ""}
            for col in additional_columns:
                row[col] = ""
            writer.writerow(row)
    print(f"CSV created at {path}")

# --- Create CSV in both data folders ---
create_csv(DATA_DIR / f"{csv_name}.csv")
create_csv(DATA_TEST_DIR / f"{csv_name}.csv")

messagebox.showinfo("CSV Created", f"CSV created successfully in:\n{DATA_DIR}\nand\n{DATA_TEST_DIR}")
