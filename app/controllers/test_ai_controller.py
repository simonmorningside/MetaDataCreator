# test_ai_controller.py
import argparse
from pathlib import Path
import pandas as pd
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from utils.paths import (
    DATA_DIR,
    DATA_TEST_DIR,
    PHOTOS_RENAMED_DIR,
    PHOTOS_TEST_RENAMED_DIR,
)
import json


class AIController:
    def __init__(self, test_mode: bool = False):
        """Initialize AI controller using BLIP-Large (Salesforce/blip-image-captioning-large)."""

        self.test_mode = test_mode

        # -------------------------
        # Directories
        # -------------------------
        if test_mode:
            self.data_dir = DATA_TEST_DIR
            self.photo_dir = PHOTOS_TEST_RENAMED_DIR
            self.ai_pool_file = DATA_TEST_DIR / "ai_pool_test.json"
        else:
            self.data_dir = DATA_DIR
            self.photo_dir = PHOTOS_RENAMED_DIR
            self.ai_pool_file = DATA_DIR / "ai_pool.json"

        # -------------------------
        # Load BLIP-Large
        # -------------------------
        model_name = "Salesforce/blip-image-captioning-large"
        print(f"Loading BLIP model: {model_name} ...")

        self.processor = BlipProcessor.from_pretrained(model_name)
        self.model = BlipForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float32   # safer for CPU-only usage
        )

        # Always CPU on Windows + AMD
        self.device = torch.device("cpu")
        self.model.to(self.device)

        print("BLIP model loaded successfully.\n")

        # -------------------------
        # Load AI pool
        # -------------------------
        if not self.ai_pool_file.exists():
            raise FileNotFoundError(f"AI pool file not found: {self.ai_pool_file}")

        with open(self.ai_pool_file, "r") as f:
            self.ai_pool_ids = json.load(f)

        print(f"Loaded {len(self.ai_pool_ids)} IDs from AI pool.")

    # ------------------------------------------------
    # Generate caption
    # ------------------------------------------------
    def generate_caption(self, image_path: Path) -> str:
        """Generate caption using BLIP-Large."""
        image = Image.open(image_path).convert("RGB")

        inputs = self.processor(images=image, return_tensors="pt").to(self.device)

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=60
            )

        caption = self.processor.decode(output[0], skip_special_tokens=True)
        return caption

    # ------------------------------------------------
    def remove_captioned_id(self, image_id: str):
        """Remove a captioned ID from the AI pool JSON."""
        if image_id in self.ai_pool_ids:
            self.ai_pool_ids.remove(image_id)
            with open(self.ai_pool_file, "w") as f:
                json.dump(self.ai_pool_ids, f, indent=2)
            print(f"🗑️ Removed {image_id} from AI pool ({len(self.ai_pool_ids)} remaining).")

    # ------------------------------------------------
    def caption_all_images(self):
        """
        Loop over CSVs and generate captions for IDs in the AI pool.
        RETURNS a list of IDs that were captioned.
        """
        captioned_ids = []

        csv_files = list(self.data_dir.glob("*.csv"))
        if not csv_files:
            print(f"No CSV files found in {self.data_dir}")
            return captioned_ids

        all_photos = list(self.photo_dir.glob("*.*"))
        if all_photos:
            print(f"Found {len(all_photos)} image files in {self.photo_dir}")
        else:
            print(f"No images found in photo directory: {self.photo_dir}")

        for csv_path in csv_files:
            print(f"\nProcessing CSV: {csv_path.name}")
            df = pd.read_csv(csv_path)

            if "ID" not in df.columns:
                print(f"CSV missing ID column: {csv_path}")
                continue

            if "Description" not in df.columns:
                df["Description"] = ""

            # Filter rows still needing captions
            df_pool = df[df["ID"].astype(str).isin(self.ai_pool_ids)]

            for idx, row in df_pool.iterrows():
                image_id = str(row["ID"])

                # Match image file
                matches = list(self.photo_dir.glob(f"{image_id}.*"))
                if not matches:
                    print(f"Skipping {image_id}: image not found")
                    continue

                image_path = matches[0]

                try:
                    caption = self.generate_caption(image_path)
                    df.at[idx, "Description"] = caption
                    captioned_ids.append(image_id)

                    print(f"Captioned {image_id}: {caption}")

                    self.remove_captioned_id(image_id)

                except Exception as e:
                    print(f"❌ Error captioning {image_id}: {e}")

            df.to_csv(csv_path, index=False)
            print(f"Updated CSV saved: {csv_path}")

        print("\n✅ Captioning complete.")
        print(f"Remaining IDs in pool: {len(self.ai_pool_ids)}")

        return captioned_ids


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIController using BLIP-Large captioning")
    parser.add_argument("--test", action="store_true", help="Use test directories and CSVs")
    args = parser.parse_args()

    controller = AIController(test_mode=args.test)
    controller.caption_all_images()
