"""
Export High-Resolution Print-Ready Calibration Sheets for Physical Testing (Gap 4).
Generates 300 DPI A4 sheets with fiducial registration crosshairs, grayscale step-wedge,
metric ruler, and a structured grid of LSB and DWT-DCT watermarked QR codes.
Outputs both PNG and PDF files to data/physical/print_sheets/ and updates manifest.csv.
"""

import os
import sys
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.qr_watermark.qr_generator import QRWatermarkGenerator
from backend.qr_watermark.lsb import LSBWatermarker
from backend.qr_watermark.dwt_dct import DWTDCTWatermarker

BASE_DIR = Path(__file__).resolve().parent.parent
PHYS_DIR = BASE_DIR / "data" / "physical"
RAW_DIR = PHYS_DIR / "raw"
PROC_DIR = PHYS_DIR / "processed"
SHEETS_DIR = PHYS_DIR / "print_sheets"
MANIFEST_PATH = PHYS_DIR / "manifest.csv"

# A4 at 300 DPI: 2480 x 3508 pixels
A4_WIDTH = 2480
A4_HEIGHT = 3508

def draw_crosshair(draw: ImageDraw.ImageDraw, x: int, y: int, size: int = 40, thickness: int = 4):
    """Draws a high-precision registration crosshair with outer ring."""
    draw.ellipse([x - size, y - size, x + size, y + size], outline="black", width=thickness)
    draw.line([x - size - 15, y, x + size + 15, y], fill="black", width=thickness)
    draw.line([x, y - size - 15, x, y + size + 15], fill="black", width=thickness)

def generate_print_sheet(batch_id: str = "BATCH-01") -> Path:
    """Generates a complete 300 DPI printable calibration sheet."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROC_DIR.mkdir(parents=True, exist_ok=True)
    SHEETS_DIR.mkdir(parents=True, exist_ok=True)

    sheet = Image.new("RGB", (A4_WIDTH, A4_HEIGHT), color="white")
    draw = ImageDraw.Draw(sheet)

    # 1. Header Information
    draw.rectangle([100, 80, A4_WIDTH - 100, 200], fill="#f8fafc", outline="#0f172a", width=3)
    # Text headers
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_sub = ImageFont.truetype("arial.ttf", 22)
        font_small = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = font_title
        font_small = font_title

    draw.text((130, 95), "PHYSICAL PRINT-SCAN-REPRINT BENCHMARK SHEET (GAP 4)", fill="#0f172a", font=font_title)
    draw.text((130, 145), f"Batch ID: {batch_id}  |  Resolution: 300 DPI (A4: 2480x3508)  |  Target Size: 50x50mm/QR", fill="#334155", font=font_sub)
    draw.text((130, 172), "Instructions: Print at 100% scale (no scaling). Scan at 600 DPI or photograph perpendicularly.", fill="#475569", font=font_small)

    # 2. Fiducial Registration Crosshairs at 4 corners
    margin_x, margin_y = 120, 100
    corners = [
        (margin_x, margin_y + 130),
        (A4_WIDTH - margin_x, margin_y + 130),
        (margin_x, A4_HEIGHT - margin_y),
        (A4_WIDTH - margin_x, A4_HEIGHT - margin_y)
    ]
    for cx, cy in corners:
        draw_crosshair(draw, cx, cy, size=35, thickness=4)

    # 3. Photometric Step-Wedge (8 grayscale patches from 0% to 100% black)
    wedge_x, wedge_y = 150, 240
    wedge_w, wedge_h = 260, 40
    densities = [255, 220, 185, 150, 115, 80, 45, 0]
    draw.text((wedge_x, wedge_y - 25), "Photometric Density Wedge (0% - 100%):", fill="#1e293b", font=font_small)
    for i, d in enumerate(densities):
        draw.rectangle(
            [wedge_x + i * wedge_w, wedge_y, wedge_x + (i + 1) * wedge_w, wedge_y + wedge_h],
            fill=(d, d, d), outline="black", width=1
        )

    # 4. Metric scale bar (50 mm at 300 DPI = ~590 px)
    scale_x, scale_y = 150, 310
    scale_px_50mm = 590
    draw.line([scale_x, scale_y, scale_x + scale_px_50mm, scale_y], fill="black", width=5)
    for tick in range(0, 51, 10):
        tx = scale_x + int(tick * scale_px_50mm / 50.0)
        draw.line([tx, scale_y - 12, tx, scale_y + 12], fill="black", width=3)
        draw.text((tx - 10, scale_y + 15), f"{tick}mm", fill="black", font=font_small)

    # 5. Generate 6 Watermarked QR Samples (3 rows x 2 columns)
    # LSB (Strengths 1, 2) vs DWT-DCT (Alphas 15, 25, 35) + 1 Clean Baseline
    configurations = [
        {"sample_id": f"{batch_id}-QR-01", "method": "CLEAN", "param": 0, "name": "Unwatermarked Host QR"},
        {"sample_id": f"{batch_id}-QR-02", "method": "LSB", "param": 1, "name": "LSB (1-Bit Plane)"},
        {"sample_id": f"{batch_id}-QR-03", "method": "LSB", "param": 2, "name": "LSB (2-Bit Planes)"},
        {"sample_id": f"{batch_id}-QR-04", "method": "DWT-DCT", "param": 15.0, "name": "DWT-DCT (Alpha=15.0)"},
        {"sample_id": f"{batch_id}-QR-05", "method": "DWT-DCT", "param": 25.0, "name": "DWT-DCT (Alpha=25.0)"},
        {"sample_id": f"{batch_id}-QR-06", "method": "DWT-DCT", "param": 35.0, "name": "DWT-DCT (Alpha=35.0)"},
    ]

    grid_start_x = 220
    grid_start_y = 440
    cell_w = 980
    cell_h = 960
    qr_target_size = 590 # ~50mm at 300 DPI

    manifest_rows = []

    for idx, cfg in enumerate(configurations):
        row = idx // 2
        col = idx % 2
        top_left_x = grid_start_x + col * cell_w
        top_left_y = grid_start_y + row * cell_h

        # Generate base QR
        payload_uuid = f"PHYS-DOC-{batch_id}-{idx+1:02d}"
        qr_obj = QRWatermarkGenerator.create_qr_symbol(payload_uuid, box_size=14, border=4)
        base_img = qr_obj["image_rgb"]
        mask = qr_obj["pixel_mask"]
        watermark_bits = QRWatermarkGenerator.generate_watermark_bits(payload_uuid, 64)

        # Apply watermarking
        if cfg["method"] == "LSB":
            wm_engine = LSBWatermarker(bit_plane=int(cfg["param"]))
            wm_img, meta = wm_engine.embed(base_img, watermark_bits, mask)
        elif cfg["method"] == "DWT-DCT":
            wm_engine = DWTDCTWatermarker(alpha=float(cfg["param"]))
            wm_img, meta = wm_engine.embed(base_img, watermark_bits, mask)
        else:
            wm_img = base_img.copy()

        # Resize to physical target size
        qr_resized = cv2.resize(wm_img, (qr_target_size, qr_target_size), interpolation=cv2.INTER_NEAREST)
        pil_qr = Image.fromarray(qr_resized)

        # Paste onto sheet
        sheet.paste(pil_qr, (top_left_x, top_left_y))

        # Draw cell outline & labeling
        draw.rectangle([top_left_x - 10, top_left_y - 10, top_left_x + qr_target_size + 10, top_left_y + qr_target_size + 10], outline="#cbd5e1", width=2)
        draw.text((top_left_x, top_left_y + qr_target_size + 20), f"Sample: {cfg['sample_id']}  |  {cfg['name']}", fill="#0f172a", font=font_sub)
        draw.text((top_left_x, top_left_y + qr_target_size + 55), f"Payload: {payload_uuid}  |  Size: 50x50 mm", fill="#64748b", font=font_small)

        # Record manifest rows (Template rows for G1 and G2)
        manifest_rows.append({
            "sample_id": f"{cfg['sample_id']}-G1",
            "batch_id": batch_id,
            "grid_index": idx + 1,
            "payload_id": payload_uuid,
            "watermark_method": cfg["method"],
            "embedding_strength": cfg["param"],
            "capture_stage": "G1_PRINT_SCAN",
            "printer_model": "PENDING_RECORDING",
            "paper_type": "PENDING_RECORDING",
            "capture_device": "PENDING_RECORDING",
            "lighting_lux": 500,
            "tilt_angle_deg": 0.0,
            "raw_image_path": f"data/physical/raw/G1_{batch_id}_{cfg['sample_id']}.png",
            "ground_truth_label": "GENUINE",
            "verification_status": "PENDING_PHYSICAL_CAPTURE"
        })
        manifest_rows.append({
            "sample_id": f"{cfg['sample_id']}-G2",
            "batch_id": batch_id,
            "grid_index": idx + 1,
            "payload_id": payload_uuid,
            "watermark_method": cfg["method"],
            "embedding_strength": cfg["param"],
            "capture_stage": "G2_REPRINT_SCAN",
            "printer_model": "PENDING_RECORDING",
            "paper_type": "PENDING_RECORDING",
            "capture_device": "PENDING_RECORDING",
            "lighting_lux": 500,
            "tilt_angle_deg": 0.0,
            "raw_image_path": f"data/physical/raw/G2_reprint_{batch_id}_{cfg['sample_id']}.png",
            "ground_truth_label": "REPRINT_MANIPULATED",
            "verification_status": "PENDING_PHYSICAL_CAPTURE"
        })

    # Save output sheet
    png_path = SHEETS_DIR / f"physical_print_sheet_{batch_id}.png"
    pdf_path = SHEETS_DIR / f"physical_print_sheet_{batch_id}.pdf"
    sheet.save(png_path, dpi=(300, 300))
    sheet.save(pdf_path, "PDF", resolution=300.0)

    # Save or update manifest
    df_new = pd.DataFrame(manifest_rows)
    if MANIFEST_PATH.exists():
        df_old = pd.read_csv(MANIFEST_PATH)
        df_combined = pd.concat([df_old, df_new]).drop_duplicates(subset=["sample_id"])
        df_combined.to_csv(MANIFEST_PATH, index=False)
    else:
        df_new.to_csv(MANIFEST_PATH, index=False)

    print(f"Exported Print Sheet PNG: {png_path}")
    print(f"Exported Print Sheet PDF: {pdf_path}")
    print(f"Updated Physical Manifest: {MANIFEST_PATH}")
    return pdf_path

if __name__ == "__main__":
    generate_print_sheet("BATCH-01")
