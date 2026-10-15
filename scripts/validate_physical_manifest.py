"""
Physical Manifest Validator Tool (Gap 4).
Verifies schema compliance, file existence, label consistency, and data integrity
for all entries in data/physical/manifest.csv.
"""

import sys
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = BASE_DIR / "data" / "physical" / "manifest.csv"

REQUIRED_COLUMNS = [
    "sample_id",
    "batch_id",
    "payload_id",
    "watermark_method",
    "embedding_strength",
    "capture_stage",
    "printer_model",
    "paper_type",
    "capture_device",
    "raw_image_path",
    "ground_truth_label",
    "verification_status"
]

VALID_STAGES = ["G1_PRINT_SCAN", "G2_REPRINT_SCAN"]
VALID_LABELS = ["GENUINE", "MANIPULATED", "REPRINT_MANIPULATED"]
VALID_METHODS = ["CLEAN", "LSB", "DWT-DCT"]

def validate_manifest() -> bool:
    print("=" * 60)
    print("PHYSICAL CAPTURE MANIFEST VALIDATION (GAP 4)")
    print("=" * 60)

    if not MANIFEST_PATH.exists():
        print(f"[FAIL] Manifest file does not exist: {MANIFEST_PATH}")
        print("Run 'python scripts/export_print_sheets.py' to generate initial print sheets and manifest.")
        return False

    try:
        df = pd.read_csv(MANIFEST_PATH)
    except Exception as e:
        print(f"[FAIL] Could not parse CSV manifest: {e}")
        return False

    errors = []
    warnings = []

    # 1. Schema check
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns in CSV: {missing_cols}")

    # 2. Duplicate sample_id check
    if "sample_id" in df.columns:
        dups = df[df.duplicated(subset=["sample_id"], keep=False)]
        if not dups.empty:
            errors.append(f"Found duplicate sample_ids: {dups['sample_id'].unique().tolist()}")

    # 3. Value validations
    raw_images_found = 0
    raw_images_pending = 0

    for idx, row in df.iterrows():
        sid = row.get("sample_id", f"Row_{idx}")

        # Method check
        method = row.get("watermark_method")
        if method not in VALID_METHODS:
            errors.append(f"[{sid}] Invalid watermark_method '{method}'. Must be in {VALID_METHODS}")

        # Stage check
        stage = row.get("capture_stage")
        if stage not in VALID_STAGES:
            errors.append(f"[{sid}] Invalid capture_stage '{stage}'. Must be in {VALID_STAGES}")

        # Label check
        label = row.get("ground_truth_label")
        if label not in VALID_LABELS:
            errors.append(f"[{sid}] Invalid ground_truth_label '{label}'. Must be in {VALID_LABELS}")

        # File check
        raw_rel = row.get("raw_image_path", "")
        raw_path = BASE_DIR / raw_rel
        status = row.get("verification_status")

        if raw_path.exists():
            raw_images_found += 1
            if status == "PENDING_PHYSICAL_CAPTURE":
                warnings.append(f"[{sid}] Raw file exists at '{raw_rel}', but status is still marked PENDING.")
        else:
            raw_images_pending += 1
            if status == "EVALUATED":
                errors.append(f"[{sid}] Marked EVALUATED, but file does not exist: {raw_path}")

    # Report results
    print(f"Total Manifest Records: {len(df)}")
    print(f"Physical Captures Digitized & Available: {raw_images_found}")
    print(f"Physical Captures Awaiting Real Hardware: {raw_images_pending}")

    if warnings:
        print(f"\n[WARNINGS] ({len(warnings)} found):")
        for w in warnings[:5]:
            print(f"  - {w}")

    if errors:
        print(f"\n[ERRORS] ({len(errors)} found):")
        for err in errors[:10]:
            print(f"  - {err}")
        print("\nManifest validation FAILED.")
        return False
    else:
        print("\nManifest schema and consistency validation PASSED.")
        if raw_images_pending > 0:
            print(f"Notice: {raw_images_pending} physical captures are pending real user scanning.")
        return True

if __name__ == "__main__":
    success = validate_manifest()
    sys.exit(0 if success else 1)
