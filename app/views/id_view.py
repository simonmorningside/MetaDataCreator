import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

class IDView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="white")
        self.app = app

        ttk.Label(self, text="Tools / ID Generator", font=("Arial", 16, "bold")).pack(pady=20)

        ttk.Label(self, text="Select CSV:").pack(pady=5)
        self.csv_dropdown = ttk.Combobox(self, textvariable=app.csv_choice, state="readonly")
        self.csv_dropdown.pack(pady=5)

        ttk.Button(self, text="Generate New IDs", command=self.app.id_controller.generate_ids).pack(pady=5)
        ttk.Button(self, text="View Identifier Pools", command=self.app.id_controller.view_pools).pack(pady=5)

        ttk.Button(self, text="Back to Menu", command=lambda: app.show_frame("MainMenu")).pack(pady=20)
