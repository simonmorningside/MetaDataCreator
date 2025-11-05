import tkinter as tk
from tkinter import ttk, messagebox

class MetadataView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="white")
        self.app = app

        ttk.Label(self, text="Metadata Tools", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Button(self, text="Inspect Metadata", command=self.app.metadata_controller.inspect_metadata).pack(pady=5)
        ttk.Button(self, text="Back to Menu", command=lambda: app.show_frame("MainMenu")).pack(pady=20)
