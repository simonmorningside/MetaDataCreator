# metadata_view.py

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import pandas as pd
from controllers.test_ai_controller import AIController


class MetadataView(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="white")
        self.app = app
        self.csv_data = None
        self.current_row = 0
        self.csv_path = None
        self.photo_dir = None
        self.tk_image = None
        self.recent_captioned_ids = set()   # ⭐ Newly captioned items

        # Title
        ttk.Label(self, text="Metadata Tools", font=("Arial", 16, "bold")).pack(pady=20)

        # Existing metadata inspection button
        ttk.Button(
            self,
            text="Inspect Metadata",
            command=self.app.metadata_controller.inspect_metadata
        ).pack(pady=5)

        # AI caption generation
        ttk.Button(
            self,
            text="Generate Captions (AI)",
            command=self.run_ai_captioner
        ).pack(pady=5)

        # CSV review frame
        self.review_frame = ttk.Frame(self)
        self.review_frame.pack(pady=10, fill="both", expand=True)

        # Dropdown for IDs
        self.id_label = ttk.Label(self.review_frame, text="Select ID:")
        self.id_combobox = ttk.Combobox(self.review_frame, state="readonly")
        self.id_combobox.bind("<<ComboboxSelected>>", self.on_id_selected)

        # NEW — This appears above the image when the item was just captioned
        self.new_tag = ttk.Label(
            self.review_frame,
            text="★ NEW CAPTION",
            foreground="red",
            font=("Arial", 12, "bold")
        )
        self.new_tag.pack_forget()

        # Image + description section
        self.image_label = ttk.Label(self.review_frame)
        self.desc_label = ttk.Label(self.review_frame, text="Description:")
        self.desc_entry = ttk.Entry(self.review_frame, width=80)

        # Navigation
        self.nav_frame = tk.Frame(self.review_frame, bg="white")
        self.prev_button = ttk.Button(self.nav_frame, text="Previous", command=self.prev_row)
        self.next_button = ttk.Button(self.nav_frame, text="Next", command=self.next_row)

        self.prev_button.pack(side="left", padx=5)
        self.next_button.pack(side="right", padx=5)

        # Back button
        ttk.Button(
            self,
            text="Back to Menu",
            command=lambda: app.show_frame("MainMenu")
        ).pack(pady=20)

        # Style for flashing NEW highlight
        style = ttk.Style()
        style.configure("Highlight.TFrame", background="#fff6a6")  # pale yellow

    # -------------------------------------------------------------------
    # AI Captioning
    # -------------------------------------------------------------------
    def run_ai_captioner(self):
        try:
            self.app.status_label.config(text="Generating AI captions...")
            self.app.update()

            test_mode = getattr(self.app, "test_mode", tk.BooleanVar(value=False)).get()
            controller = AIController(test_mode=test_mode)

            # ⭐ Get list of newly captioned IDs
            captioned_ids = controller.caption_all_images()
            self.recent_captioned_ids = set(map(str, captioned_ids))

            # Load CSV + photos
            self.load_csv_for_review(controller.data_dir, controller.photo_dir)

            messagebox.showinfo(
                "Success",
                "AI caption generation complete!\nNew captions are highlighted."
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate captions:\n{e}")
        finally:
            self.app.status_label.config(text="Ready")

    # -------------------------------------------------------------------
    # Load CSV + UI Setup
    # -------------------------------------------------------------------
    def load_csv_for_review(self, csv_dir, photo_dir):
        csv_files = list(csv_dir.glob("*.csv"))
        if not csv_files:
            messagebox.showwarning("No CSVs", f"No CSV files found in {csv_dir}")
            return

        self.csv_path = csv_files[0]
        self.csv_data = pd.read_csv(self.csv_path)

        if "ID" not in self.csv_data.columns or "Description" not in self.csv_data.columns:
            messagebox.showerror("Invalid CSV", "CSV must contain ID and Description")
            return

        self.photo_dir = photo_dir

        # Fill dropdown with NEW markers
        dropdown_values = [
            f"{str(row['ID'])} ★ NEW" if str(row["ID"]) in self.recent_captioned_ids else str(row["ID"])
            for _, row in self.csv_data.iterrows()
        ]

        self.id_combobox["values"] = dropdown_values
        self.id_label.pack()
        self.id_combobox.pack(pady=5)

        # Show row 0
        self.current_row = 0
        self.show_row(0)

        # Show main UI pieces
        self.image_label.pack(pady=10)
        self.desc_label.pack()
        self.desc_entry.pack()
        self.nav_frame.pack(pady=5)

    # -------------------------------------------------------------------
    # Display a single row
    # -------------------------------------------------------------------
    def show_row(self, row_idx):
        if row_idx < 0 or row_idx >= len(self.csv_data):
            return

        # Save previous before switching
        self.save_current_row()

        self.current_row = row_idx
        row = self.csv_data.iloc[row_idx]

        img_id = str(row["ID"])
        description = row["Description"]

        # Select in dropdown
        dropdown_value = (
            f"{img_id} ★ NEW" if img_id in self.recent_captioned_ids else img_id
        )
        self.id_combobox.set(dropdown_value)

        # Load the image
        image_files = list(self.photo_dir.glob(f"{img_id}.*"))
        if image_files:
            image = Image.open(image_files[0])
            image.thumbnail((400, 400))
            self.tk_image = ImageTk.PhotoImage(image)
        else:
            self.tk_image = self.generate_placeholder_image((400, 400))

        self.image_label.configure(image=self.tk_image)
        self.image_label.image = self.tk_image

        # Load description text
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, description)

        # NEW Highlight if captioned this run
        self.apply_new_highlight(img_id)

    # -------------------------------------------------------------------
    # Highlighting Newly Captioned Rows
    # -------------------------------------------------------------------
    def apply_new_highlight(self, image_id):
        if image_id in self.recent_captioned_ids:
            self.new_tag.pack(pady=3)
            self.flash_background()
        else:
            self.new_tag.pack_forget()
            self.review_frame.configure(style="")  # reset

    def flash_background(self):
        self.review_frame.configure(style="Highlight.TFrame")
        self.after(1500, lambda: self.review_frame.configure(style=""))

    # -------------------------------------------------------------------
    # Placeholder Image
    # -------------------------------------------------------------------
    def generate_placeholder_image(self, size):
        img = Image.new("RGB", size, color=(200, 200, 200))
        draw = ImageDraw.Draw(img)
        text = "No Image"
        font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (size[0] - text_width) / 2
        y = (size[1] - text_height) / 2

        draw.text((x, y), text, fill=(100, 100, 100), font=font)
        return ImageTk.PhotoImage(img)

    # -------------------------------------------------------------------
    # Dropdown selection
    # -------------------------------------------------------------------
    def on_id_selected(self, event):
        selected = self.id_combobox.get().replace(" ★ NEW", "")
        index = self.csv_data.index[self.csv_data["ID"].astype(str) == selected][0]
        self.show_row(index)

    # -------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------
    def save_current_row(self):
        if self.csv_data is not None and self.csv_path is not None:
            self.csv_data.at[self.current_row, "Description"] = self.desc_entry.get()
            self.csv_data.to_csv(self.csv_path, index=False)

    def next_row(self):
        if self.current_row < len(self.csv_data) - 1:
            self.show_row(self.current_row + 1)

    def prev_row(self):
        if self.current_row > 0:
            self.show_row(self.current_row - 1)
