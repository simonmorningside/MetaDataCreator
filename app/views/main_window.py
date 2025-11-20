import tkinter as tk
from tkinter import ttk

from controllers.metadata_controller import MetadataController
from controllers.photo_controller import PhotoController
from controllers.id_controller import IDController

from views.metadata_view import MetadataView
from views.photo_view import PhotoView
from views.id_view import IDView
from views.about_view import AboutView
from utils.paths import ensure_all_dirs


class PhotoDataApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Metadata Creator")
        self.geometry("440x480")

        # 🔥 Make window resizable
        self.resizable(True, True)

        ensure_all_dirs()

        # --- App State ---
        self.test_mode = tk.BooleanVar(value=False)
        self.csv_choice = tk.StringVar()
        self.csvs = {}

        # --- Controllers ---
        self.metadata_controller = MetadataController(self)
        self.photo_controller = PhotoController(self)
        self.id_controller = IDController(self)

        # --- Root grid (main + status bar) ---
        self.grid_rowconfigure(0, weight=1)  # main
        self.grid_rowconfigure(1, weight=0)  # status bar
        self.grid_columnconfigure(0, weight=1)

        # --- Container for pages ---
        self.container = tk.Frame(self, bg="#f4f4f4")
        self.container.grid(row=0, column=0, sticky="nsew")

        # 🔥 Make container responsive
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # --- Page frames ---
        self.frames = {}
        for F in (MainMenu, MetadataView, PhotoView, IDView, AboutView):
            frame = F(parent=self.container, app=self)

            # 🔥 Every child frame fills container
            frame.grid(row=0, column=0, sticky="nsew")

            # Store
            self.frames[F.__name__] = frame

        # --- Status Bar ---
        status_frame = tk.Frame(self, height=60, bg="#4CAF50")
        status_frame.grid(row=1, column=0, sticky="ew")
        status_frame.grid_propagate(False)

        self.status_label = tk.Label(
            status_frame,
            text="Status: Ready",
            anchor="w",
            bg="#4CAF50",
            fg="white",
            font=("Helvetica", 16, "bold"),
            padx=10,
        )
        self.status_label.pack(fill="both", expand=True)

        # Update status when test mode changes
        self.test_mode.trace_add("write", lambda *args: self.update_status())

        # Start on Main Menu
        self.show_frame("MainMenu")

    def show_frame(self, page_name):
        self.frames[page_name].tkraise()

    def update_csv_dropdown(self, csv_dict):
        """Update dropdown when new metadata loaded."""
        self.csvs = csv_dict
        id_view = self.frames["IDView"]
        id_view.csv_dropdown["values"] = list(csv_dict.keys())
        if csv_dict:
            self.csv_choice.set(list(csv_dict.keys())[0])

    def update_status(self):
        """Update status bar to reflect test mode."""
        if self.test_mode.get():
            self.status_label.config(
                text="Status: TEST MODE ACTIVE",
                bg="#FF9800",
                fg="white"
            )
            self.status_label.master.config(bg="#FF9800")
        else:
            self.status_label.config(
                text="Status: Ready",
                bg="#4CAF50",
                fg="white"
            )
            self.status_label.master.config(bg="#4CAF50")


# ---------------------------------------------------------------------
# 🎨 MAIN MENU FRAME — Now 100% Responsive
# ---------------------------------------------------------------------
class MainMenu(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f4f4f4")
        self.app = app

        # --- Make MainMenu frame responsive ---
        self.grid_rowconfigure(0, weight=1)   # top spacer
        self.grid_rowconfigure(1, weight=0)   # title
        self.grid_rowconfigure(2, weight=1)   # button area (expands)
        self.grid_rowconfigure(3, weight=0)   # test toggle
        self.grid_rowconfigure(4, weight=1)   # bottom spacer
        self.grid_columnconfigure(0, weight=1)

        # --- Title ---
        title = tk.Label(
            self,
            text="Metadata Creator",
            font=("Helvetica", 24, "bold"),
            bg="#f4f4f4",
            fg="#333",
        )
        title.grid(row=1, column=0, pady=(20, 20))

        # --- Buttons Container ---
        button_frame = tk.Frame(self, bg="#f4f4f4")
        button_frame.grid(row=2, column=0, sticky="nsew")

        # 🔥 Make button frame responsive
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_rowconfigure(1, weight=1)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

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

        # 🔥 Responsive buttons (fill grid cells)
        tk.Button(button_frame, text="Metadata",
                  command=lambda: app.show_frame("MetadataView"),
                  **style).grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        tk.Button(button_frame, text="Photos",
                  command=lambda: app.show_frame("PhotoView"),
                  **style).grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        tk.Button(button_frame, text="Tools",
                  command=lambda: app.show_frame("IDView"),
                  **style).grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

        tk.Button(button_frame, text="About Me",
                  command=lambda: app.show_frame("AboutView"),
                  **style).grid(row=1, column=1, padx=20, pady=20, sticky="nsew")

        # --- Test Mode Toggle ---
        test_frame = tk.Frame(self, bg="#f4f4f4")
        test_frame.grid(row=3, column=0, pady=(20, 40))

        test_toggle = tk.Checkbutton(
            test_frame,
            text="Enable Test Mode",
            variable=self.app.test_mode,
            bg="#f4f4f4",
            font=("Helvetica", 12, "bold"),
            onvalue=True,
            offvalue=False,
        )
        test_toggle.pack()
