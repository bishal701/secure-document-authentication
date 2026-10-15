"""
Gap 3 Benchmark Runner: Comparative Analysis of LSB vs DWT-DCT Watermarking.
Computes side-by-side performance under identical digital attacks:
PSNR, SSIM, NC, BER, WESR, QDSR, Attack Detection Rate, and execution latencies.
Saves results to results/gap3/gap3_lsb_vs_dwtdct_results.csv and gap3_summary.json.
"""

import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

RESULTS_GAP3_DIR = BASE_DIR / "results" / "gap3"
MANIFEST_PATH = BASE_DIR / "data" / "synthetic" / "manifest.csv"

def run_gap3_analysis():
    print("=" * 60)
    print("RUNNING GAP 3 BENCHMARK: LSB vs. DWT-DCT DIGITAL ATTACK COMPARISON")
    print("=" * 60)

    RESULTS_GAP3_DIR.mkdir(parents=True, exist_ok=True)

    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_PATH}")

    df = pd.read_csv(MANIFEST_PATH)

    # Filter for standard Gap 3 comparison configurations:
    # LSB (bit plane 1) vs DWT-DCT (alpha 20.0)
    df_comp = df[
        ((df["watermark_method"] == "LSB") & (df["embedding_strength"] == 1)) |
        ((df["watermark_method"] == "DWT-DCT") & (df["embedding_strength"] == 20.0))
    ].copy()

    print(f"Total eligible samples for Gap 3 comparison: {len(df_comp)}")

    attack_order = [
        "CLEAN",
        "GAUSSIAN_NOISE",
        "SALT_PEPPER",
        "GAUSSIAN_BLUR",
        "JPEG_COMPRESSION",
        "RESIZE",
        "ROTATION",
        "CROP",
        "CONTRAST_ILLUMINATION",
        "WATERMARK_REMOVAL"
    ]

    records = []
    summary_data = {"methods": ["LSB", "DWT-DCT"], "attacks": attack_order, "metrics": {}}

    for method in ["LSB", "DWT-DCT"]:
        df_method = df_comp[df_comp["watermark_method"] == method]
        summary_data["metrics"][method] = {}

        for atk in attack_order:
            df_atk = df_method[df_method["attack_type"] == atk]
            n_samples = len(df_atk)
            if n_samples == 0:
                continue

            mean_psnr = float(df_atk["psnr"].mean())
            std_psnr = float(df_atk["psnr"].std())
            mean_ssim = float(df_atk["ssim"].mean())
            std_ssim = float(df_atk["ssim"].std())
            mean_nc = float(df_atk["extracted_nc"].mean())
            std_nc = float(df_atk["extracted_nc"].std())
            mean_ber = float(df_atk["extracted_ber"].mean())
            std_ber = float(df_atk["extracted_ber"].std())

            # WESR: NC >= 0.75 and BER <= 20%
            wesr = float(np.mean((df_atk["extracted_nc"] >= 0.75) & (df_atk["extracted_ber"] <= 20.0)) * 100.0)
            # QDSR: Standard QR decoding success rate
            qdsr = float(df_atk["qr_decoded"].mean() * 100.0)

            # Attack Detection Rate: If attacked, did watermark degrade (NC < 0.75 or BER > 20%)?
            if atk == "CLEAN":
                adr = 0.0 # Genuine sample, not an attack
            else:
                adr = float(np.mean((df_atk["extracted_nc"] < 0.75) | (df_atk["extracted_ber"] > 20.0)) * 100.0)

            mean_emb_lat = float(df_atk["embed_latency_ms"].mean())
            mean_ext_lat = float(df_atk["extract_latency_ms"].mean())

            mean_emb_psnr = float(df_atk["embedding_psnr_db"].mean()) if "embedding_psnr_db" in df_atk.columns else mean_psnr
            mean_emb_ssim = float(df_atk["embedding_ssim"].mean()) if "embedding_ssim" in df_atk.columns else mean_ssim

            row = {
                "watermark_method": method,
                "attack_type": atk,
                "sample_count": n_samples,
                "embedding_psnr_db": round(mean_emb_psnr, 2),
                "embedding_ssim": round(mean_emb_ssim, 4),
                "post_attack_psnr_db": round(mean_psnr, 2),
                "post_attack_ssim": round(mean_ssim, 4),
                "mean_psnr_db": round(mean_psnr, 2),
                "std_psnr_db": round(std_psnr, 2),
                "mean_ssim": round(mean_ssim, 4),
                "std_ssim": round(std_ssim, 4),
                "mean_nc": round(mean_nc, 4),
                "std_nc": round(std_nc, 4),
                "mean_ber_percent": round(mean_ber, 2),
                "std_ber_percent": round(std_ber, 2),
                "wesr_percent": round(wesr, 1),
                "qdsr_scannability_percent": round(qdsr, 1),
                "attack_detection_rate_percent": round(adr, 1),
                "embed_latency_ms": round(mean_emb_lat, 2),
                "extract_latency_ms": round(mean_ext_lat, 2)
            }
            records.append(row)
            summary_data["metrics"][method][atk] = row

    df_out = pd.DataFrame(records)
    out_csv = RESULTS_GAP3_DIR / "gap3_lsb_vs_dwtdct_results.csv"
    df_out.to_csv(out_csv, index=False)

    out_json = RESULTS_GAP3_DIR / "gap3_summary.json"
    with open(out_json, "w") as f:
        json.dump(summary_data, f, indent=2)

    print(f"\nGap 3 evaluation finished. Saved results table to: {out_csv}")
    print(f"Summary JSON saved to: {out_json}")
    return df_out

if __name__ == "__main__":
    run_gap3_analysis()
