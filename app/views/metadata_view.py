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
        self.image_label = None
        self.csv_path = None
        self.photo_dir = None
        self.tk_image = None

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

        # Image and description
        self.image_label = ttk.Label(self.review_frame)
        self.desc_label = ttk.Label(self.review_frame, text="Description:")
        self.desc_entry = ttk.Entry(self.review_frame, width=80)

        # Navigation buttons
        self.prev_button = ttk.Button(self.review_frame, text="Previous", command=self.prev_row)
        self.next_button = ttk.Button(self.review_frame, text="Next", command=self.next_row)

        # Back button
        ttk.Button(
            self,
            text="Back to Menu",
            command=lambda: app.show_frame("MainMenu")
        ).pack(pady=20)

    # -----------------------------
    # AI Captioning
    # -----------------------------
    def run_ai_captioner(self):
        try:
            self.app.status_label.config(text="Generating AI captions...")
            self.app.update()

            test_mode = getattr(self.app, "test_mode", tk.BooleanVar(value=False)).get()
            controller = AIController(test_mode=test_mode)
            controller.caption_all_images()

            # After AI finishes, load CSV for review
            self.load_csv_for_review(controller.data_dir, controller.photo_dir)
            messagebox.showinfo("Success", "AI caption generation complete!")

        except FileNotFoundError as e:
            messagebox.showerror("File Not Found", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate captions:\n{e}")
        finally:
            self.app.status_label.config(text="Ready")

    # -----------------------------
    # Load CSV for review
    # -----------------------------
    def load_csv_for_review(self, csv_dir, photo_dir):
        csv_files = list(csv_dir.glob("*.csv"))
        if not csv_files:
            messagebox.showwarning("No CSVs", f"No CSV files found in {csv_dir}")
            return

        self.csv_path = csv_files[0]
        self.csv_data = pd.read_csv(self.csv_path)
        if "ID" not in self.csv_data.columns or "Description" not in self.csv_data.columns:
            messagebox.showerror("Invalid CSV", "CSV must contain ID and Description columns")
            return

        self.photo_dir = photo_dir

        # Fill the dropdown with all IDs
        self.id_combobox["values"] = list(self.csv_data["ID"].astype(str))
        self.id_label.pack()
        self.id_combobox.pack(pady=5)

        # Show first row
        self.current_row = 0
        self.show_row(self.current_row)

        # Pack image and description fields
        self.image_label.pack(pady=10)
        self.desc_label.pack()
        self.desc_entry.pack()
        self.prev_button.pack(side="left", padx=5, pady=5)
        self.next_button.pack(side="right", padx=5, pady=5)

    # -----------------------------
    # Show single row
    # -----------------------------
    def show_row(self, row_idx):
        if self.csv_data is None or row_idx < 0 or row_idx >= len(self.csv_data):
            return

        self.save_current_row()
        self.current_row = row_idx
        row = self.csv_data.iloc[row_idx]
        image_id = str(row["ID"])
        description = row["Description"]

        # Update dropdown selection
        self.id_combobox.current(row_idx)

        # Load image
        image_list = list(self.photo_dir.glob(f"{image_id}.*"))
        if image_list:
            image = Image.open(image_list[0])
            image.thumbnail((400, 400))
            self.tk_image = ImageTk.PhotoImage(image)
        else:
            self.tk_image = self.generate_placeholder_image((400, 400))

        self.image_label.configure(image=self.tk_image)
        self.image_label.image = self.tk_image

        # Update description
        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, description)

    # -----------------------------
    # Placeholder Image
    # -----------------------------
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

    # -----------------------------
    # ID dropdown selection
    # -----------------------------
    def on_id_selected(self, event):
        selected_id = self.id_combobox.get()
        row_idx = self.csv_data.index[self.csv_data["ID"].astype(str) == selected_id][0]
        self.show_row(row_idx)

    # -----------------------------
    # Navigation
    # -----------------------------
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
