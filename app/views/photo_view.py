import tkinter as tk
from tkinter import ttk

class PhotoView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="white")
        self.app = app

        ttk.Label(self, text="Photo Tools", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Button(self, text="Rename Photos", command=self.app.photo_controller.rename_photos).pack(pady=5)
        ttk.Button(self, text="Back to Menu", command=lambda: app.show_frame("MainMenu")).pack(pady=20)
