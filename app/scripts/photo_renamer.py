from pathlib import Path
from tkinter import messagebox, simpledialog, Toplevel, Label, Button, Frame, Button
from PIL import Image, ImageEnhance, ImageTk, ImageFilter
from utils.paths import (
    DATA_DIR,
    DATA_TEST_DIR,
    PHOTOS_ORIGINAL_DIR,
    PHOTOS_RENAMED_DIR,
    PHOTOS_TEST_ORIGINAL_DIR,
    PHOTOS_TEST_RENAMED_DIR,
)
from utils.csv_loader import load_csvs_from_dir
from utils.variable_namer import assign_variables
from utils.identifiers import IdentifierPool
from utils.photo_variant_handler import group_and_rename_variants
import json
import pandas as pd
import threading

# -----------------------------
# PHOTO RENAMER
# -----------------------------
def run_photo_renamer(test_mode: bool = False, gui_mode: bool = False):
    """
    Rename photo files using IDs from CSVs (CLI or GUI) and save a pool for AI captioning.
    Properly respects test_mode for all paths and pool usage.
    """
    # --- Paths ---
    if test_mode:
        data_dir = DATA_TEST_DIR
        original_dir = PHOTOS_TEST_ORIGINAL_DIR
        renamed_dir = PHOTOS_TEST_RENAMED_DIR
        pool_file = DATA_TEST_DIR / "available_ids_test.json"
        ai_pool_file = DATA_TEST_DIR / "ai_pool_test.json"
    else:
        data_dir = DATA_DIR
        original_dir = PHOTOS_ORIGINAL_DIR
        renamed_dir = PHOTOS_RENAMED_DIR
        pool_file = DATA_DIR / "available_ids.json"
        ai_pool_file = DATA_DIR / "ai_pool.json"

    renamed_dir.mkdir(parents=True, exist_ok=True)

    # --- Load CSV data ---
    datasets = load_csvs_from_dir(data_dir)
    if not datasets:
        msg = f"No CSV files found in {data_dir}"
        print(msg)
        if gui_mode:
            messagebox.showwarning("No Data Found", msg)
        return

    # --- Assign variables from CSVs ---
    assigned_variables = assign_variables(datasets)

    # --- Initialize ID pool ---
    id_pool = IdentifierPool(assigned_variables, test_mode=test_mode)
    id_pool.pool_file = pool_file

    # --- Choose pool ---
    available_pools = list(id_pool.pool.keys())
    if not available_pools:
        msg = "No available ID pools found."
        print(msg)
        if gui_mode:
            messagebox.showerror("No Pools", msg)
        return

    print("\nAvailable pools:", available_pools)

    if gui_mode:
        pool_choice = simpledialog.askstring(
            "Choose Pool",
            f"Available pools:\n{', '.join(available_pools)}\n\nEnter pool name:",
        )
        if not pool_choice or pool_choice not in available_pools:
            messagebox.showerror("Invalid Choice", "That pool does not exist.")
            return
    else:
        while True:
            pool_choice = input("Choose CSV pool to use for renaming (e.g., 'ctk', 'fnd'): ").strip()
            if pool_choice in id_pool.pool:
                break
            print("Invalid choice, try again.")

    df = assigned_variables[pool_choice]

    # --- Optional Temporal Coverage ---
    temporal_map = {
        "1": "1920-1929",
        "2": "1930-1939",
        "3": "1940-1949",
        "4": "1950-1959",
        "5": "1960-1969",
        "6": "1970-1979",
        "7": "1980-1989",
        "8": "1990-1999",
        "9": "2000-2009",
    }

    if gui_mode:
        set_temporal = messagebox.askyesno("Set Temporal Coverage", "Do you want to set Temporal Coverage for this batch?")
    else:
        set_temporal = input("Do you want to set Temporal Coverage for this batch? (y/n): ").strip().lower() == "y"

    temporal_value = None
    if set_temporal:
        if gui_mode:
            options = "\n".join([f"{k}: {v}" for k, v in temporal_map.items()])
            while True:
                choice = simpledialog.askstring("Select Temporal Coverage", f"{options}\n\nEnter number (1–6):")
                if not choice:
                    return
                if choice in temporal_map:
                    temporal_value = temporal_map[choice]
                    break
                messagebox.showerror("Invalid Selection", "Please enter a number between 1 and 6.")
        else:
            while True:
                for k, v in temporal_map.items():
                    print(f"{k}: {v}")
                choice = input("Enter number (1-6): ").strip()
                if choice in temporal_map:
                    temporal_value = temporal_map[choice]
                    break
                print("Invalid selection. Try again.")

    # --- Rename photos ---
    photo_files = sorted(original_dir.glob("*.*"))
    if not photo_files:
        msg = f"No photos found in {original_dir}"
        print(msg)
        if gui_mode:
            messagebox.showwarning("No Photos Found", msg)
        return

    df, total_renamed = group_and_rename_variants(
        photo_files=photo_files,
        id_pool=id_pool,
        pool_choice=pool_choice,
        df=df,
        renamed_dir=renamed_dir,
        set_temporal=set_temporal,
        temporal_value=temporal_value,
    )

    # --- Save CSV ---
    csv_file_path = data_dir / f"{pool_choice}.csv"
    df.to_csv(csv_file_path, index=False)

    # --- Save AI Pool ---
    ai_ids = [str(f) for f in df['ID'] if pd.notna(f) and list(renamed_dir.glob(f"{f}.*"))]
    with open(ai_pool_file, 'w') as f:
        json.dump(ai_ids, f, indent=2)

    print(f"AI pool saved: {ai_pool_file} ({len(ai_ids)} items)")

    summary_msg = (
        f"Updated CSV saved:\n{csv_file_path}\n"
        f"\nRenamed {len(photo_files)} photos into:\n{renamed_dir}\n"
        f"AI pool saved: {ai_pool_file}"
    )
    print(summary_msg)
    if gui_mode:
        messagebox.showinfo("Rename Complete", summary_msg)


# -----------------------------
# PHOTO CLEANING
# -----------------------------
def clean_photos(test_mode: bool = False, gui_mode: bool = False):
    """
    Apply cleaning operations to photos (brightness/contrast/denoise/rotation) in place.
    Shows old vs cleaned images for user choice with streamlined controls.
    """
    target_dir = PHOTOS_TEST_RENAMED_DIR if test_mode else PHOTOS_RENAMED_DIR
    photo_files = sorted(target_dir.glob("*.*"))

    if not photo_files:
        msg = f"No photos found in {target_dir}"
        print(msg)
        if gui_mode:
            messagebox.showwarning("No Photos Found", msg)
        return

    def get_median_filter_size(denoise_factor: float) -> int:
        """Map denoise factor (0-1) to odd integer size for MedianFilter (1–9)."""
        size = max(1, min(9, int(denoise_factor * 9) | 1))  # Ensure odd number
        return size

    for photo_path in photo_files:
        img = Image.open(photo_path).convert("RGB")

        # Default adjustment values
        brightness = 1.0
        contrast = 1.0
        denoise = 0.0
        rotation = 0
        preview_img = img.copy()  # nonlocal reference

        if gui_mode:
            window = Toplevel()
            window.title(f"Clean Photo: {photo_path.name}")
            window.configure(bg="white")

            # --- Labels for old vs preview ---
            Label(window, text="Original", font=("Arial", 12, "bold"), bg="white").grid(row=0, column=0)
            Label(window, text="Preview", font=("Arial", 12, "bold"), bg="white").grid(row=0, column=1)

            orig_imgtk = ImageTk.PhotoImage(img.resize((400, 400)))
            old_canvas = Label(window, image=orig_imgtk)
            old_canvas.image = orig_imgtk
            old_canvas.grid(row=1, column=0, padx=10, pady=10)

            clean_canvas = Label(window)
            clean_canvas.grid(row=1, column=1, padx=10, pady=10)

            # --- Update preview function ---
            def update_preview():
                nonlocal preview_img
                preview_img = img.copy()
                preview_img = ImageEnhance.Brightness(preview_img).enhance(brightness)
                preview_img = ImageEnhance.Contrast(preview_img).enhance(contrast)
                if denoise > 0:
                    size = get_median_filter_size(denoise)
                    preview_img = preview_img.filter(ImageFilter.MedianFilter(size=size))
                if rotation != 0:
                    preview_img = preview_img.rotate(rotation, expand=True)
                preview_imgtk = ImageTk.PhotoImage(preview_img.resize((400, 400)))
                clean_canvas.configure(image=preview_imgtk)
                clean_canvas.image = preview_imgtk

            # --- Helper to create up/down control for a parameter ---
            def create_control(name, value_getter, value_setter, row):
                frame = Frame(window, bg="white")
                frame.grid(row=row, column=0, columnspan=2, pady=2)
                Label(frame, text=f"{name}: ", font=("Arial", 10), bg="white").pack(side="left")
                value_label = Label(frame, text=f"{value_getter():.2f}" if name != "Denoise" else f"{value_getter():.1f}", width=5, bg="white")
                value_label.pack(side="left", padx=2)

                def up():
                    value_setter(1)
                    value_label.config(text=f"{value_getter():.2f}" if name != "Denoise" else f"{value_getter():.1f}")
                    update_preview()

                def down():
                    value_setter(-1)
                    value_label.config(text=f"{value_getter():.2f}" if name != "Denoise" else f"{value_getter():.1f}")
                    update_preview()

                Button(frame, text="▲", command=up, width=2).pack(side="left")
                Button(frame, text="▼", command=down, width=2).pack(side="left")

            # --- Define setters and getters ---
            create_control("Brightness",
                           lambda: brightness,
                           lambda d: nonlocal_set('brightness', d * 0.1),
                           row=2)
            create_control("Contrast",
                           lambda: contrast,
                           lambda d: nonlocal_set('contrast', d * 0.1),
                           row=3)
            create_control("Denoise",
                           lambda: denoise,
                           lambda d: nonlocal_set('denoise', d * 0.1),
                           row=4)
            create_control("Rotation",
                           lambda: rotation,
                           lambda d: nonlocal_set('rotation', d * 90),
                           row=5)

            # --- Buttons for keeping images ---
            Button(window, text="Keep Original", bg="lightgray", command=lambda: window.destroy()).grid(row=6, column=0, pady=10, sticky="ew")
            Button(window, text="Keep Cleaned", bg="lightgreen", command=lambda: save_and_close()).grid(row=6, column=1, pady=10, sticky="ew")

            # Helper functions for nonlocal variables
            def nonlocal_set(name, delta):
                nonlocal brightness, contrast, denoise, rotation
                if name == "brightness":
                    brightness = max(0.1, brightness + delta)
                elif name == "contrast":
                    contrast = max(0.1, contrast + delta)
                elif name == "denoise":
                    denoise = min(max(0.0, denoise + delta), 1.0)
                elif name == "rotation":
                    rotation = (rotation + delta) % 360

            def save_and_close():
                preview_img.save(photo_path)
                window.destroy()

            update_preview()
            window.wait_window()
        else:
            # Non-GUI automatic cleaning
            cleaned_img = ImageEnhance.Brightness(img).enhance(1.1)
            cleaned_img = ImageEnhance.Contrast(cleaned_img).enhance(1.1)
            cleaned_img = cleaned_img.filter(ImageFilter.MedianFilter(size=3))
            cleaned_img.thumbnail((800, 800))
            cleaned_img.save(photo_path)

    msg = f"Photo cleaning complete in place for {target_dir}"
    print(msg)
    if gui_mode:
        messagebox.showinfo("Cleaning Complete", msg)