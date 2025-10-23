from collections import defaultdict
import re
import shutil
import pandas as pd
from pathlib import Path

def group_and_rename_variants(photo_files, id_pool, pool_choice, df, renamed_dir, set_temporal=False, temporal_value=None):
    """
    Groups photos by base name and renames them using shared base identifiers.
    Variants like _A, _a, _B, _b are treated case-insensitively but normalized to uppercase suffix.
    Updates CSV by duplicating rows for suffix variants immediately below the base row.
    """
    # --- Ensure renamed_dir exists in Documents ---
    renamed_dir.mkdir(parents=True, exist_ok=True)

    pattern = re.compile(r"^(.*?)(?:_([a-zA-Z]))?$")
    photo_groups = defaultdict(list)

    # Group photos by base name
    for photo_path in photo_files:
        stem = photo_path.stem
        match = pattern.match(stem)
        if not match:
            continue
        base, suffix = match.groups()
        suffix = suffix.upper() if suffix else ''  # Normalize suffix to uppercase
        photo_groups[base].append((suffix, photo_path))

    total_renamed = 0

    for base in sorted(photo_groups.keys()):
        group = sorted(photo_groups[base], key=lambda x: (x[0] != '', x[0]))

        base_identifier = id_pool.pop_identifier(pool_choice)
        if not base_identifier:
            print(f"No more available IDs in pool '{pool_choice}'. Stopping.")
            break

        # Find index of base row in df
        base_row_idx = df.index[df["ID"] == base_identifier]
        if base_row_idx.empty:
            print(f"Base ID '{base_identifier}' not found in CSV, skipping group {base}")
            continue
        base_row_idx = base_row_idx[0]

        # Rename base photo
        suffix, photo_path = group[0]
        ext = photo_path.suffix
        new_filename = f"{base_identifier}{ext}"
        new_path = renamed_dir / new_filename
        shutil.move(str(photo_path), str(new_path))
        print(f"{photo_path.name} → {new_filename}")

        if "Title" in df.columns:
            df.at[base_row_idx, "Title"] = photo_path.name
        if set_temporal and "Temporal Coverage" in df.columns:
            df.at[base_row_idx, "Temporal Coverage"] = temporal_value

        total_renamed += 1

        # Handle variant photos
        insert_pos = base_row_idx + 1
        for suffix, photo_path in group[1:]:
            ext = photo_path.suffix
            full_identifier = f"{base_identifier}_{suffix}"
            new_filename = f"{full_identifier}{ext}"
            new_path = renamed_dir / new_filename
            shutil.move(str(photo_path), str(new_path))
            print(f"{photo_path.name} → {new_filename}")

            # Duplicate base row and update
            base_row = df.loc[base_row_idx].copy()
            base_row["ID"] = full_identifier
            if "Title" in df.columns:
                base_row["Title"] = photo_path.name
            if set_temporal and "Temporal Coverage" in df.columns:
                base_row["Temporal Coverage"] = temporal_value

            top = df.iloc[:insert_pos]
            bottom = df.iloc[insert_pos:]
            df = pd.concat([top, base_row.to_frame().T, bottom]).reset_index(drop=True)
            insert_pos += 1
            total_renamed += 1

    return df, total_renamed
