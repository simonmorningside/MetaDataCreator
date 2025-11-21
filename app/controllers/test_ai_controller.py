# test_ai_controller.py
import argparse
from pathlib import Path
import pandas as pd
from PIL import Image
import torch
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from utils.paths import (
    DATA_DIR,
    DATA_TEST_DIR,
    PHOTOS_RENAMED_DIR,
    PHOTOS_TEST_RENAMED_DIR,
)
import json


class AIController:
    def __init__(self, test_mode: bool = False):
        """Initialize the AI controller using vit-gpt2-image-captioning."""
        self.test_mode = test_mode

        # Directories
        if test_mode:
            self.data_dir = DATA_TEST_DIR
            self.photo_dir = PHOTOS_TEST_RENAMED_DIR
            self.ai_pool_file = DATA_TEST_DIR / "ai_pool_test.json"
        else:
            self.data_dir = DATA_DIR
            self.photo_dir = PHOTOS_RENAMED_DIR
            self.ai_pool_file = DATA_DIR / "ai_pool.json"

        # -------------------------
        # Load model + processor + tokenizer
        # -------------------------
        model_name = "nlpconnect/vit-gpt2-image-captioning"
        print(f"Loading model: {model_name} ...")

        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
        self.feature_extractor = ViTImageProcessor.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        print("Model loaded successfully.\n")

        # Load AI pool
        if not self.ai_pool_file.exists():
            raise FileNotFoundError(f"AI pool file not found: {self.ai_pool_file}")

        with open(self.ai_pool_file, "r") as f:
            self.ai_pool_ids = json.load(f)

        print(f"Loaded {len(self.ai_pool_ids)} IDs from AI pool.")

    # ------------------------------------------------
    # Generate caption
    # ------------------------------------------------
    def generate_caption(self, image_path: Path) -> str:
        """Generate a caption for a single image."""
        image = Image.open(image_path).convert("RGB")
        pixel_values = self.feature_extractor(images=image, return_tensors="pt").pixel_values.to(self.device)

        # Generate caption
        with torch.no_grad():
            output_ids = self.model.generate(
                pixel_values,
                max_length=64,
                num_beams=4,
                early_stopping=True
            )

        caption = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return caption

    # ------------------------------------------------
    def remove_captioned_id(self, image_id: str):
        """Remove a captioned ID from the AI pool and update JSON."""
        if image_id in self.ai_pool_ids:
            self.ai_pool_ids.remove(image_id)
            with open(self.ai_pool_file, "w") as f:
                json.dump(self.ai_pool_ids, f, indent=2)
            print(f"🗑️ Removed {image_id} from AI pool ({len(self.ai_pool_ids)} remaining).")

    # ------------------------------------------------
    def caption_all_images(self):
        """Loop over CSVs and generate captions for IDs in the AI pool."""
        csv_files = list(self.data_dir.glob("*.csv"))
        if not csv_files:
            print(f"No CSV files found in {self.data_dir}")
            return

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

            # Filter rows in AI pool
            df_pool = df[df["ID"].astype(str).isin(self.ai_pool_ids)]

            for idx, row in df_pool.iterrows():
                image_id = str(row["ID"])

                # Find corresponding image file
                matches = list(self.photo_dir.glob(f"{image_id}.*"))
                if not matches:
                    print(f"Skipping {image_id}: image not found")
                    continue

                image_path = matches[0]
                caption = self.generate_caption(image_path)
                print(f"{image_path.name}: {caption}")

                df.at[idx, "Description"] = caption
                self.remove_captioned_id(image_id)

            df.to_csv(csv_path, index=False)
            print(f"Updated CSV saved: {csv_path}")

        print("\n✅ Captioning complete.")
        print(f"Remaining IDs in pool: {len(self.ai_pool_ids)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIController using vit-gpt2-image-captioning")
    parser.add_argument("--test", action="store_true", help="Use test directories and CSVs")
    args = parser.parse_args()

    controller = AIController(test_mode=args.test)
    controller.caption_all_images()
