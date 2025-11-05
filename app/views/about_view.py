import tkinter as tk
from tkinter import ttk

class AboutView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="white")
        ttk.Label(self, text="About Me", font=("Arial", 16, "bold")).pack(pady=20)
        ttk.Label(self, text="This page is under construction.", foreground="gray").pack(pady=10)
        ttk.Button(self, text="Back to Menu", command=lambda: app.show_frame("MainMenu")).pack(pady=20)
