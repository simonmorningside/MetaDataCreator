# test_ai_controller.py
import argparse
from pathlib import Path
import pandas as pd
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
from app.utils.paths import (
    DATA_DIR,
    DATA_TEST_DIR,
    PHOTOS_RENAMED_DIR,
    PHOTOS_TEST_RENAMED_DIR,
)
import json

class AIController:
    def __init__(self, test_mode: bool = False):
        """Initialize the AI controller and load the captioning model."""
        self.test_mode = test_mode

        if test_mode:
            self.data_dir = DATA_TEST_DIR
            self.photo_dir = PHOTOS_TEST_RENAMED_DIR
            self.ai_pool_file = DATA_TEST_DIR / "ai_pool_test.json"
        else:
            self.data_dir = DATA_DIR
            self.photo_dir = PHOTOS_RENAMED_DIR
            self.ai_pool_file = DATA_DIR / "ai_pool.json"

        print("Loading BLIP image captioning model...")
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        print("Model loaded.\n")

        # --- Load AI pool IDs ---
        if not self.ai_pool_file.exists():
            raise FileNotFoundError(f"AI pool file not found: {self.ai_pool_file}")
        with open(self.ai_pool_file, 'r') as f:
            self.ai_pool_ids = json.load(f)
        print(f"Loaded {len(self.ai_pool_ids)} IDs from AI pool.")

    def generate_caption(self, image_path: Path) -> str:
        """Generate a caption for a single image."""
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt")
        out = self.model.generate(**inputs)
        caption = self.processor.decode(out[0], skip_special_tokens=True)
        return caption

    def caption_all_images(self):
        """Loop over CSV files and generate descriptions only for IDs in the AI pool."""
        csv_files = list(self.data_dir.glob("*.csv"))
        if not csv_files:
            print(f"No CSV files found in {self.data_dir}")
            return

        # --- Debug: list files in photo directory ---
        all_photos = list(self.photo_dir.glob("*.*"))
        if all_photos:
            print(f"Found {len(all_photos)} files in {self.photo_dir}:")
            for f in all_photos:
                print(f" - {f.name}")
        else:
            print(f"No image files found in {self.photo_dir}")

        for csv_path in csv_files:
            print(f"\nProcessing CSV: {csv_path.name}")
            df = pd.read_csv(csv_path)

            if 'ID' not in df.columns:
                print(f"CSV {csv_path} missing 'ID' column, skipping.")
                continue
            if 'Description' not in df.columns:
                df['Description'] = ""  # create column if missing

            # Only process rows where ID is in the AI pool
            df_pool = df[df['ID'].astype(str).isin(self.ai_pool_ids)]
            for idx, row in df_pool.iterrows():
                image_id = str(row['ID'])

                # Find the actual file in the renamed folder
                matches = list(self.photo_dir.glob(f"{image_id}.*"))
                if not matches:
                    print(f"Skipping: {image_id} not found in {self.photo_dir}")
                    continue

                image_path = matches[0]
                caption = self.generate_caption(image_path)
                print(f"{image_path.name}: {caption}")
                df.at[idx, 'Description'] = caption

            df.to_csv(csv_path, index=False)
            print(f"Updated CSV saved: {csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIController for generating captions using AI pool.")
    parser.add_argument("--test", action="store_true", help="Use test directories and CSVs")
    args = parser.parse_args()

    controller = AIController(test_mode=args.test)
    controller.caption_all_images()
