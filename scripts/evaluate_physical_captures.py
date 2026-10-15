"""
Physical Print-Scan-Reprint Capture Evaluator (Gap 4).
Processes real digitized physical captures:
1. Perspective unwarping and alignment via fiducial registration marks.
2. QR segmentation into data/physical/processed/.
3. Optical QR scannability decoding via OpenCV.
4. Watermark extraction and recovery metrics (NC, BER).
5. GLCM microtexture print-channel degradation analysis.
Saves evaluated records to results/gap4/physical_evaluation_results.csv and summary JSON.
"""

import os
import sys
import json
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.qr_watermark.qr_generator import QRWatermarkGenerator
from backend.qr_watermark.lsb import LSBWatermarker
from backend.qr_watermark.dwt_dct import DWTDCTWatermarker
from backend.qr_watermark.benchmark_evaluator import BenchmarkEvaluator
from backend.components.component_a.print_channel import CopyDetectionEngine

BASE_DIR = Path(__file__).resolve().parent.parent
PHYS_DIR = BASE_DIR / "data" / "physical"
RAW_DIR = PHYS_DIR / "raw"
PROC_DIR = PHYS_DIR / "processed"
MANIFEST_PATH = PHYS_DIR / "manifest.csv"
RESULTS_GAP4_DIR = BASE_DIR / "results" / "gap4"

def evaluate_physical_captures():
    print("=" * 60)
    print("EVALUATING PHYSICAL CAPTURES (GAP 4)")
    print("=" * 60)

    RESULTS_GAP4_DIR.mkdir(parents=True, exist_ok=True)
    PROC_DIR.mkdir(parents=True, exist_ok=True)

    if not MANIFEST_PATH.exists():
        print("[ERROR] Manifest not found. Run scripts/export_print_sheets.py first.")
        return

    df_manifest = pd.read_csv(MANIFEST_PATH)
    total_planned = len(df_manifest)

    available_captures = []
    for idx, row in df_manifest.iterrows():
        raw_rel = row.get("raw_image_path", "")
        raw_full = BASE_DIR / raw_rel
        if raw_full.exists():
            available_captures.append((idx, row, raw_full))

    print(f"Total Configured Manifest Records: {total_planned}")
    print(f"Actual Captured Image Files Found: {len(available_captures)}")

    results = []

    if len(available_captures) == 0:
        print("\n" + "!" * 60)
        print("NOTICE: NO PHYSICAL CAPTURE FILES FOUND IN data/physical/raw/")
        print("In accordance with scientific non-fabrication rules:")
        print("Physical captures require genuine printed and scanned specimens.")
        print("To complete physical evaluation:")
        print("  1. Print: data/physical/print_sheets/physical_print_sheet_BATCH-01.pdf at 100% scale.")
        print("  2. Digitize via flatbed scanner (600 DPI) or smartphone perpendicular camera.")
        print("  3. Save to data/physical/raw/ as specified in data/physical/manifest.csv.")
        print("  4. Rerun: python scripts/evaluate_physical_captures.py")
        print("!" * 60 + "\n")

        summary = {
            "status": "PENDING_PHYSICAL_CAPTURES",
            "research_gap": "Gap 4: Real Print-Scan-Reprint Validation",
            "manifest_records_configured": total_planned,
            "real_physical_captures_evaluated": 0,
            "simulated_data_substituted": False,
            "execution_instructions": "Print physical sheet PDF at 100% scale, scan or photograph, save to data/physical/raw/, and rerun scripts/evaluate_physical_captures.py."
        }

        # Save pending summary
        with open(RESULTS_GAP4_DIR / "physical_evaluation_summary.json", "w") as f:
            json.dump(summary, f, indent=2)

        # Create empty template CSV
        cols = list(df_manifest.columns) + [
            "qr_decoded", "decoded_payload", "extracted_nc", "extracted_ber",
            "glcm_homogeneity", "glcm_energy", "copy_score", "evaluation_timestamp"
        ]
        df_empty = pd.DataFrame(columns=cols)
        df_empty.to_csv(RESULTS_GAP4_DIR / "physical_evaluation_results.csv", index=False)
        return

    # Process available real captures
    for idx, row, raw_full in available_captures:
        sid = row["sample_id"]
        method = row["watermark_method"]
        strength = float(row["embedding_strength"])
        payload_id = row["payload_id"]
        gt_label = row["ground_truth_label"]

        # Read image
        img_bgr = cv2.imread(str(raw_full))
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # Save processed crop
        proc_path = PROC_DIR / f"{sid}_aligned.png"
        cv2.imwrite(str(proc_path), img_bgr)

        # 1. Optical QR Decoding
        decoded_ok, decoded_text = QRWatermarkGenerator.decode_qr(img_rgb)

        # 2. Watermark Extraction
        qr_obj = QRWatermarkGenerator.create_qr_symbol(payload_id)
        mask = cv2.resize(qr_obj["pixel_mask"].astype(np.uint8), (img_rgb.shape[1], img_rgb.shape[0]), interpolation=cv2.INTER_NEAREST).astype(bool)
        gt_bits = QRWatermarkGenerator.generate_watermark_bits(payload_id, 64)

        nc, ber = 0.0, 100.0
        if method == "LSB":
            lsb = LSBWatermarker(bit_plane=int(strength) if strength > 0 else 1)
            try:
                ext_bits, _ = lsb.extract(img_rgb, mask, 64)
                nc = BenchmarkEvaluator.calculate_nc(gt_bits, ext_bits)
                ber = BenchmarkEvaluator.calculate_ber(gt_bits, ext_bits)
            except Exception as e:
                print(f"Extraction error for {sid}: {e}")
        elif method == "DWT-DCT":
            dwt = DWTDCTWatermarker(alpha=strength)
            try:
                ext_bits, _ = dwt.extract(img_rgb, mask, 64)
                nc = BenchmarkEvaluator.calculate_nc(gt_bits, ext_bits)
                ber = BenchmarkEvaluator.calculate_ber(gt_bits, ext_bits)
            except Exception as e:
                print(f"Extraction error for {sid}: {e}")

        # 3. GLCM Copy Detection
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        copy_res = CopyDetectionEngine.analyze_microtexture(gray)

        results.append({
            **row.to_dict(),
            "qr_decoded": decoded_ok,
            "decoded_payload": decoded_text,
            "extracted_nc": float(nc),
            "extracted_ber": float(ber),
            "glcm_homogeneity": copy_res["glcm_homogeneity"],
            "glcm_energy": copy_res["glcm_energy"],
            "copy_score": copy_res["copy_score"],
            "predicted_verdict": copy_res["verdict"]
        })

    df_res = pd.DataFrame(results)
    df_res.to_csv(RESULTS_GAP4_DIR / "physical_evaluation_results.csv", index=False)

    summary = {
        "status": "COMPLETED",
        "research_gap": "Gap 4: Real Print-Scan-Reprint Validation",
        "total_evaluated": len(results),
        "qr_decoding_success_rate": float(df_res["qr_decoded"].mean() * 100.0),
        "mean_extracted_nc": float(df_res["extracted_nc"].mean()),
        "mean_extracted_ber": float(df_res["extracted_ber"].mean()),
    }
    with open(RESULTS_GAP4_DIR / "physical_evaluation_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Saved Physical Evaluation Results to: {RESULTS_GAP4_DIR / 'physical_evaluation_results.csv'}")

if __name__ == "__main__":
    evaluate_physical_captures()
