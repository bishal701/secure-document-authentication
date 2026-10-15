"""
Synthetic Benchmark Dataset Generator (Gap 3, Gap 10).
Generates a reproducible dataset with strictly leakage-safe partitions grouped by unique payload ID.
Applies LSB and DWT-DCT watermarking across multiple strengths and full digital attack taxonomy.
Stores images in data/synthetic/images/ and full metadata in data/synthetic/manifest.csv.
"""

import os
import sys
import time
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
from backend.attack_simulator.qr_attacks import QRAttackEngine

DATA_DIR = BASE_DIR / "data" / "synthetic"
IMG_DIR = DATA_DIR / "images"
MANIFEST_PATH = DATA_DIR / "manifest.csv"
SUMMARY_PATH = DATA_DIR / "dataset_summary.json"

GLOBAL_SEED = 42

def build_dataset(num_payloads: int = 50) -> pd.DataFrame:
    print("=" * 60)
    print("GENERATING REPRODUCIBLE SYNTHETIC QR WATERMARK DATASET")
    print("=" * 60)

    np.random.seed(GLOBAL_SEED)
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Establish Leakage-Safe Splits by Unique Payload ID
    # 60% Train, 20% Val, 20% Test
    n_train = int(num_payloads * 0.6)
    n_val = int(num_payloads * 0.2)
    n_test = num_payloads - n_train - n_val

    splits = {}
    for i in range(num_payloads):
        pid = f"UID-{i+1:03d}"
        if i < n_train:
            splits[pid] = "train"
        elif i < n_train + n_val:
            splits[pid] = "val"
        else:
            splits[pid] = "test"

    print(f"Total Unique Payloads: {num_payloads} -> Train: {n_train}, Val: {n_val}, Test: {n_test}")

    # 2. Attack Definitions
    attack_configs = [
        ("CLEAN", {}),
        ("GAUSSIAN_NOISE", {"sigma": 15.0}),
        ("SALT_PEPPER", {"density": 0.03}),
        ("GAUSSIAN_BLUR", {"ksize": 5, "sigma": 1.2}),
        ("JPEG_COMPRESSION", {"quality": 70}),
        ("RESIZE", {"scale": 0.75}),
        ("ROTATION", {"angle": 3.0}),
        ("CROP", {"crop_ratio": 0.15}),
        ("CONTRAST_ILLUMINATION", {"alpha": 1.15, "beta": -15.0}),
        ("WATERMARK_REMOVAL", {})
    ]

    # 3. Watermarking Configurations:
    # Fair Gap 3 Core Comparison: LSB (plane 1) vs DWT-DCT (alpha 20.0)
    # Gap 10 Strength Sweep: LSB planes {1, 2, 3}, DWT-DCT alphas {10, 20, 30, 40, 50}
    watermark_configs = [
        {"method": "LSB", "strength": 1, "name": "LSB_k1"},
        {"method": "LSB", "strength": 2, "name": "LSB_k2"},
        {"method": "LSB", "strength": 3, "name": "LSB_k3"},
        {"method": "DWT-DCT", "strength": 10.0, "name": "DWTDCT_a10"},
        {"method": "DWT-DCT", "strength": 20.0, "name": "DWTDCT_a20"},
        {"method": "DWT-DCT", "strength": 30.0, "name": "DWTDCT_a30"},
        {"method": "DWT-DCT", "strength": 40.0, "name": "DWTDCT_a40"},
        {"method": "DWT-DCT", "strength": 50.0, "name": "DWTDCT_a50"},
    ]

    records = []
    sample_counter = 0
    t0 = time.time()

    for p_idx, (payload_id, split) in enumerate(splits.items()):
        # Generate base QR host
        qr_obj = QRWatermarkGenerator.create_qr_symbol(payload_id, box_size=8, border=4)
        host_img = qr_obj["image_rgb"]
        mask = qr_obj["pixel_mask"]
        gt_bits = QRWatermarkGenerator.generate_watermark_bits(payload_id, 64)

        # For each watermarking configuration
        for wm_cfg in watermark_configs:
            method = wm_cfg["method"]
            strength = wm_cfg["strength"]
            wm_tag = wm_cfg["name"]

            # Embed watermark
            t_emb_0 = time.perf_counter()
            if method == "LSB":
                engine = LSBWatermarker(bit_plane=int(strength))
                watermarked_img, meta_emb = engine.embed(host_img, gt_bits, mask)
            else:
                engine = DWTDCTWatermarker(alpha=float(strength))
                watermarked_img, meta_emb = engine.embed(host_img, gt_bits, mask)
            embed_latency_ms = (time.perf_counter() - t_emb_0) * 1000.0

            # 1. Embedding Imperceptibility (Host vs Clean Watermarked)
            embedding_psnr = BenchmarkEvaluator.calculate_psnr(host_img, watermarked_img)
            embedding_ssim = BenchmarkEvaluator.calculate_ssim(host_img, watermarked_img)

            # Apply attacks
            for atk_name, atk_params in attack_configs:
                sample_counter += 1
                sample_id = f"SMP-{sample_counter:05d}"

                # Apply distortion
                attacked_img, atk_meta = QRAttackEngine.apply_attack(watermarked_img, atk_name, atk_params)

                # Ground truth labeling:
                # Class 0: GENUINE (Clean watermarked with matching payload)
                # Class 1: MANIPULATED (Any attacked, tampered, or degraded variant)
                is_genuine = (atk_name == "CLEAN")
                gt_label = 0 if is_genuine else 1
                gt_class = "GENUINE" if is_genuine else "MANIPULATED"

                # Extract watermark
                t_ext_0 = time.perf_counter()
                try:
                    if method == "LSB":
                        ext_bits, _ = engine.extract(attacked_img, mask, 64)
                    else:
                        ext_bits, _ = engine.extract(attacked_img, mask, 64)
                    nc = BenchmarkEvaluator.calculate_nc(gt_bits, ext_bits)
                    ber = BenchmarkEvaluator.calculate_ber(gt_bits, ext_bits)
                except Exception:
                    nc, ber = 0.0, 100.0
                extract_latency_ms = (time.perf_counter() - t_ext_0) * 1000.0

                # Optical QR decoding
                decode_ok, decoded_text = QRWatermarkGenerator.decode_qr(attacked_img)

                # 2. Post-Attack Image Distortion (Host vs Attacked)
                post_psnr = BenchmarkEvaluator.calculate_psnr(host_img, attacked_img)
                post_ssim = BenchmarkEvaluator.calculate_ssim(host_img, attacked_img)

                # Save image file
                rel_img_path = f"data/synthetic/images/{sample_id}.png"
                full_img_path = BASE_DIR / rel_img_path
                cv2.imwrite(str(full_img_path), cv2.cvtColor(attacked_img, cv2.COLOR_RGB2BGR))

                records.append({
                    "sample_id": sample_id,
                    "payload_id": payload_id,
                    "split": split,
                    "watermark_method": method,
                    "embedding_strength": strength,
                    "watermark_config": wm_tag,
                    "attack_type": atk_name,
                    "attack_params": json.dumps(atk_params),
                    "ground_truth_label": gt_label,
                    "ground_truth_class": gt_class,
                    "embedding_psnr_db": round(float(embedding_psnr), 3),
                    "embedding_ssim": round(float(embedding_ssim), 4),
                    "post_attack_psnr_db": round(float(post_psnr), 3),
                    "post_attack_ssim": round(float(post_ssim), 4),
                    "psnr": round(float(post_psnr), 3),
                    "ssim": round(float(post_ssim), 4),
                    "extracted_nc": round(float(nc), 4),
                    "extracted_ber": round(float(ber), 3),
                    "qr_decoded": bool(decode_ok),
                    "decoded_payload": decoded_text,
                    "embed_latency_ms": round(embed_latency_ms, 2),
                    "extract_latency_ms": round(extract_latency_ms, 2),
                    "image_path": rel_img_path
                })

        if (p_idx + 1) % 10 == 0:
            elapsed = time.time() - t0
            print(f"Processed {p_idx + 1}/{num_payloads} payloads ({sample_counter} total samples) in {elapsed:.1f}s")

    df = pd.DataFrame(records)
    df.to_csv(MANIFEST_PATH, index=False)

    summary = {
        "total_samples": len(df),
        "unique_payloads": num_payloads,
        "splits": {
            "train": int(np.sum(df["split"] == "train")),
            "val": int(np.sum(df["split"] == "val")),
            "test": int(np.sum(df["split"] == "test")),
        },
        "class_distribution": {
            "GENUINE (0)": int(np.sum(df["ground_truth_label"] == 0)),
            "MANIPULATED (1)": int(np.sum(df["ground_truth_label"] == 1)),
        },
        "methods": df["watermark_method"].value_counts().to_dict(),
        "attacks": df["attack_type"].value_counts().to_dict(),
        "generation_time_sec": round(time.time() - t0, 2)
    }

    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Finished dataset generation: {len(df)} samples saved to {MANIFEST_PATH}")
    print(f"Summary saved to {SUMMARY_PATH}")
    return df

if __name__ == "__main__":
    build_dataset(num_payloads=50)
