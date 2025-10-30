import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from app.utils.paths import ensure_all_dirs, DATA_DIR, DATA_TEST_DIR

from app.controllers.metadata_controller import MetadataController
from app.controllers.photo_controller import PhotoController
from app.controllers.id_controller import IDController


class PhotoDataApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Photo Data Management App")
        self.geometry("520x460")
        self.test_mode = tk.BooleanVar(value=False)

        ensure_all_dirs()

        # --- Alert Banner ---
        self.alert_frame = tk.Frame(self, bg="red", height=40)
        self.alert_label = tk.Label(
            self.alert_frame,
            text="⚠️ TEST MODE ACTIVE ⚠️",
            fg="white",
            bg="red",
            font=("Arial", 12, "bold")
        )
        self.alert_label.pack(fill="both", expand=True)
        self.alert_frame.pack_forget()

        # --- Controllers ---
        self.metadata_controller = MetadataController(self)
        self.photo_controller = PhotoController(self)
        self.id_controller = IDController(self)

        # --- Main Layout ---
        ttk.Label(self, text="Select Action:").pack(pady=10)
        ttk.Button(self, text="Inspect Metadata", command=self.metadata_controller.inspect_metadata).pack(pady=5)
        ttk.Button(self, text="Rename Photos", command=self.photo_controller.rename_photos).pack(pady=5)

        ttk.Label(self, text="Select CSV for ID Generation:").pack(pady=5)
        self.csv_choice = tk.StringVar()
        self.csv_dropdown = ttk.Combobox(self, textvariable=self.csv_choice, state="readonly")
        self.csv_dropdown.pack(pady=5)

        ttk.Button(self, text="Generate New IDs", command=self.id_controller.generate_ids).pack(pady=5)
        ttk.Button(self, text="View Identifier Pools", command=self.id_controller.view_pools).pack(pady=5)

        ttk.Checkbutton(
            self,
            text="Test Mode",
            variable=self.test_mode,
            command=self.toggle_test_mode
        ).pack(pady=15)

        self.status_label = ttk.Label(self, text="Ready", foreground="gray")
        self.status_label.pack(side="bottom", pady=10)

        # Internal state
        self.csvs = {}

    def toggle_test_mode(self):
        if self.test_mode.get():
            self.alert_frame.pack(fill="x", before=self.children["!label"])
            self.bell()
            self.status_label.config(text="Test Mode Enabled")
        else:
            self.alert_frame.pack_forget()
            self.status_label.config(text="Ready")

    def update_csv_dropdown(self, csv_dict):
        """Called by controller after metadata inspection."""
        self.csvs = csv_dict
        self.csv_dropdown["values"] = list(csv_dict.keys())
        if csv_dict:
            self.csv_choice.set(list(csv_dict.keys())[0])
