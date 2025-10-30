import tkinter as tk
from tkinter import ttk

from app.controllers.metadata_controller import MetadataController
from app.controllers.photo_controller import PhotoController
from app.controllers.id_controller import IDController

from app.views.metadata_view import MetadataView
from app.views.photo_view import PhotoView
from app.views.id_view import IDView
from app.views.about_view import AboutView
from app.utils.paths import ensure_all_dirs


class PhotoDataApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Metadata Creator")
        self.geometry("600x500")
        self.resizable(False, False)
        ensure_all_dirs()

        # --- App State ---
        self.test_mode = tk.BooleanVar(value=False)
        self.csv_choice = tk.StringVar()
        self.csvs = {}

        # --- Controllers ---
        self.metadata_controller = MetadataController(self)
        self.photo_controller = PhotoController(self)
        self.id_controller = IDController(self)

        # --- Frame Container ---
        self.container = tk.Frame(self, bg="#f4f4f4")
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (MainMenu, MetadataView, PhotoView, IDView, AboutView):
            page_name = F.__name__
            frame = F(parent=self.container, app=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        """Switch visible frame."""
        frame = self.frames[page_name]
        frame.tkraise()

    def update_csv_dropdown(self, csv_dict):
        """Update dropdown when new metadata loaded."""
        self.csvs = csv_dict
        id_view = self.frames["IDView"]
        id_view.csv_dropdown["values"] = list(csv_dict.keys())
        if csv_dict:
            self.csv_choice.set(list(csv_dict.keys())[0])


# ---------------------------------------------------------------------
# 🎨 MAIN MENU FRAME
# ---------------------------------------------------------------------
class MainMenu(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f4f4f4")
        self.app = app

        # --- Title ---
        title = tk.Label(
            self,
            text="Metadata Creator",
            font=("Helvetica", 22, "bold"),
            bg="#f4f4f4",
            fg="#333",
        )
        title.pack(pady=40)

        # --- Grid for 2x2 buttons ---
        button_frame = tk.Frame(self, bg="#f4f4f4")
        button_frame.pack(expand=True)

        style = {
            "width": 15,
            "height": 5,
            "font": ("Helvetica", 12, "bold"),
            "bg": "#0078D7",
            "fg": "white",
            "activebackground": "#005A9E",
            "relief": "raised",
            "bd": 3,
        }

        tk.Button(
            button_frame, text="Metadata", command=lambda: app.show_frame("MetadataView"), **style
        ).grid(row=0, column=0, padx=20, pady=20)
        tk.Button(
            button_frame, text="Photos", command=lambda: app.show_frame("PhotoView"), **style
        ).grid(row=0, column=1, padx=20, pady=20)
        tk.Button(
            button_frame, text="Tools", command=lambda: app.show_frame("IDView"), **style
        ).grid(row=1, column=0, padx=20, pady=20)
        tk.Button(
            button_frame, text="About Me", command=lambda: app.show_frame("AboutView"), **style
        ).grid(row=1, column=1, padx=20, pady=20)
