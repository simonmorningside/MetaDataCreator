#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from scripts.metadata import run_load_and_inspect
from scripts.photo_renamer import run_photo_renamer
from utils.identifiers import display_identifier_pools
from utils.id_generator import generate_new_ids_for_csv
from utils.paths import ensure_all_dirs, DATA_DIR, DATA_TEST_DIR


class PhotoDataApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Photo Data Management App")
        self.geometry("520x460")
        self.test_mode = tk.BooleanVar(value=False)

        ensure_all_dirs()

        # --- ALERT BANNER ---
        self.alert_frame = tk.Frame(self, bg="red", height=40)
        self.alert_label = tk.Label(
            self.alert_frame,
            text="⚠️ TEST MODE ACTIVE ⚠️",
            fg="white",
            bg="red",
            font=("Arial", 12, "bold")
        )
        self.alert_label.pack(fill="both", expand=True)
        self.alert_frame.pack(fill="x")
        self.alert_frame.pack_forget()

        # --- MAIN UI ---
        ttk.Label(self, text="Select Action:").pack(pady=10)
        ttk.Button(self, text="Inspect Metadata", command=self.inspect_action).pack(pady=5)
        ttk.Button(self, text="Rename Photos", command=self.rename_action).pack(pady=5)

        ttk.Label(self, text="Select CSV for ID Generation:").pack(pady=5)
        self.csv_choice = tk.StringVar()
        self.csv_dropdown = ttk.Combobox(self, textvariable=self.csv_choice, state="readonly")
        self.csv_dropdown.pack(pady=5)

        ttk.Button(self, text="Generate New IDs", command=self.generate_ids).pack(pady=5)
        ttk.Button(self, text="View Identifier Pools", command=self.view_pools).pack(pady=5)

        ttk.Checkbutton(
            self,
            text="Test Mode",
            variable=self.test_mode,
            command=self.toggle_test_mode
        ).pack(pady=15)

        self.status_label = ttk.Label(self, text="Ready", foreground="gray")
        self.status_label.pack(side="bottom", pady=10)

        self.csvs = {}

    def toggle_test_mode(self):
        if self.test_mode.get():
            self.alert_frame.pack(fill="x", before=self.children["!label"])
            self.bell()
        else:
            self.alert_frame.pack_forget()
        self.status_label.config(text="Test Mode Enabled" if self.test_mode.get() else "Ready")

    def inspect_action(self):
        try:
            self.status_label.config(text="Running metadata inspection...")
            self.update()
            self.csvs, _ = run_load_and_inspect(
                test_mode=self.test_mode.get(),
                gui_mode=True
            )
            self.csv_dropdown["values"] = list(self.csvs.keys())
            if self.csvs:
                self.csv_choice.set(list(self.csvs.keys())[0])
            messagebox.showinfo("Success", "Metadata inspection complete!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to inspect: {e}")
        finally:
            self.status_label.config(text="Ready")

    def rename_action(self):
        try:
            self.status_label.config(text="Running photo renamer...")
            self.update()
            run_photo_renamer(test_mode=self.test_mode.get(), gui_mode=True)
            messagebox.showinfo("Success", "Photo renaming complete!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename: {e}")
        finally:
            self.status_label.config(text="Ready")

    def generate_ids(self):
        selected_csv = self.csv_choice.get()
        if not selected_csv:
            messagebox.showwarning("No CSV selected", "Please select a CSV from the dropdown.")
            return

        num_new = simpledialog.askinteger(
            "Number of new IDs",
            "How many new IDs would you like to generate?",
            minvalue=1,
            maxvalue=10000
        )
        if not num_new:
            return

        try:
            generate_new_ids_for_csv(selected_csv, num_new=num_new, test_mode=self.test_mode.get())
            messagebox.showinfo("Success", f"Generated {num_new} new IDs for '{selected_csv}.csv'.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate IDs: {e}")

    def view_pools(self):
        try:
            text = display_identifier_pools()
            messagebox.showinfo("Identifier Pools", text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display pools: {e}")


if __name__ == "__main__":
    app = PhotoDataApp()
    app.mainloop()
