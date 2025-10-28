#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from scripts.metadata import run_load_and_inspect
from scripts.photo_renamer import run_photo_renamer
from utils.paths import ensure_all_dirs
from utils.identifiers import display_identifier_pools


class PhotoDataApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Photo Data Management App")
        self.geometry("400x360")
        self.root_path = Path(__file__).resolve().parent
        self.test_mode = tk.BooleanVar(value=False)

        ensure_all_dirs()

        # --- ALERT BANNER ---
        self.alert_frame = tk.Frame(self, bg="red", height=40)
        self.alert_label = tk.Label(
            self.alert_frame,
            text="⚠️ TEST MODE ACTIVE ⚠️",
            fg="white",
            bg="red",
            font=("Arial", 12, "bold"),
        )
        self.alert_label.pack(fill="both", expand=True)
        self.alert_frame.pack(fill="x")
        self.alert_frame.pack_forget()  # start hidden

        # --- MAIN UI ---
        ttk.Label(self, text="Select Action:").pack(pady=10)
        ttk.Button(self, text="Inspect Metadata", command=self.inspect_action).pack(pady=5)
        ttk.Button(self, text="Rename Photos", command=self.rename_action).pack(pady=5)
        ttk.Button(self, text="View Identifier Pools", command=self.view_identifiers_action).pack(pady=5)

        ttk.Checkbutton(
            self,
            text="Test Mode",
            variable=self.test_mode,
            command=self.toggle_test_mode,
        ).pack(pady=15)

        self.status_label = ttk.Label(self, text="Ready", foreground="gray")
        self.status_label.pack(side="bottom", pady=10)

    def toggle_test_mode(self):
        """Show or hide the red alert banner."""
        if self.test_mode.get():
            self.alert_frame.pack(fill="x", before=self.children["!label"])  # show banner at top
            self.bell()  # make a sound for emphasis
        else:
            self.alert_frame.pack_forget()
        self.status_label.config(text="Test Mode Enabled" if self.test_mode.get() else "Ready")

    def inspect_action(self):
        try:
            self.status_label.config(text="Running metadata inspection...")
            self.update()
            run_load_and_inspect(test_mode=self.test_mode.get(), gui_mode=True)
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

    def view_identifiers_action(self):
        """Show the current identifier pools (main/test)."""
        try:
            pool_summary = display_identifier_pools()
            messagebox.showinfo("Identifier Pools", pool_summary)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display identifier pools: {e}")


if __name__ == "__main__":
    app = PhotoDataApp()
    app.mainloop()
