# test_ai_controller.py
import argparse
from pathlib import Path
import pandas as pd
from PIL import Image
from transformers import pipeline
from app.utils.paths import (
    DATA_DIR,
    DATA_TEST_DIR,
    PHOTOS_RENAMED_DIR,
    PHOTOS_TEST_RENAMED_DIR,
)
import json


class AIController:
    def __init__(self, test_mode: bool = False):
        """Initialize the AI controller and load the ViT-GPT2 image captioning model."""
        self.test_mode = test_mode

        # --- Directories based on mode ---
        if test_mode:
            self.data_dir = DATA_TEST_DIR
            self.photo_dir = PHOTOS_TEST_RENAMED_DIR
            self.ai_pool_file = DATA_TEST_DIR / "ai_pool_test.json"
        else:
            self.data_dir = DATA_DIR
            self.photo_dir = PHOTOS_RENAMED_DIR
            self.ai_pool_file = DATA_DIR / "ai_pool.json"

        # --- Load ViT-GPT2 captioning model ---
        model_name = "nlpconnect/vit-gpt2-image-captioning"
        print(f"Loading model: {model_name} ...")
        self.captioner = pipeline("image-to-text", model=model_name)
        print("Model loaded successfully.\n")

        # --- Load AI pool IDs ---
        if not self.ai_pool_file.exists():
            raise FileNotFoundError(f"AI pool file not found: {self.ai_pool_file}")
        with open(self.ai_pool_file, 'r') as f:
            self.ai_pool_ids = json.load(f)
        print(f"Loaded {len(self.ai_pool_ids)} IDs from AI pool.")

    def generate_caption(self, image_path: Path) -> str:
        """Generate a caption for a single image using the ViT-GPT2 model."""
        image = Image.open(image_path).convert("RGB")
        results = self.captioner(image)
        caption = results[0]['generated_text'].strip()
        return caption

    def remove_captioned_id(self, image_id: str):
        """Remove a captioned ID from the AI pool and update the JSON file."""
        if image_id in self.ai_pool_ids:
            self.ai_pool_ids.remove(image_id)
            with open(self.ai_pool_file, 'w') as f:
                json.dump(self.ai_pool_ids, f, indent=2)
            print(f"🗑️  Removed {image_id} from AI pool ({len(self.ai_pool_ids)} remaining).")

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

                # ✅ Remove ID from pool after successful captioning
                self.remove_captioned_id(image_id)

            df.to_csv(csv_path, index=False)
            print(f"Updated CSV saved: {csv_path}")

        print("\n✅ Captioning complete.")
        print(f"Remaining IDs in pool: {len(self.ai_pool_ids)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIController for generating captions using AI pool.")
    parser.add_argument("--test", action="store_true", help="Use test directories and CSVs")
    args = parser.parse_args()

    controller = AIController(test_mode=args.test)
    controller.caption_all_images()
