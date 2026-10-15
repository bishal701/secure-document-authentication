# Implementation Audit and Repository Baseline Report

**Project Title:** Stealth-Aware QR Watermarking for Secure Document Authentication: Comparative Analysis of LSB and DWT–DCT, Physical Print–Scan–Reprint Robustness, and AI Classification  
**Date of Audit:** October 15, 2026  
**Auditor / Researcher:** Bishal Paul (23BCI0224), VIT Vellore  
**Target Directory:** `secure-document-authentication`  

---

## 1. Executive Summary

This audit assesses the state of the Secure Document Authentication repository prior to implementing the extended research program covering **Gap 3 (LSB vs. DWT–DCT QR Watermarking)**, **Gap 4 (Real Print–Scan–Reprint Validation Pipeline)**, and **Gap 10 (Watermark Imperceptibility vs. AI Classification Trade-off)**.

The existing baseline implements a multi-tier document authentication framework combining:
1. Asymmetric digital signatures (Ed25519) with CBOR serialization and ZLIB Level-9 compression embedded in a visual 2D QR barcode.
2. Full-canvas Discrete Wavelet Transform and Singular Value Decomposition (DWT-SVD) invisible watermarking on the luminance ($Y$) channel.
3. Blind copy detection (Component A) using Gray-Level Co-occurrence Matrix (GLCM) microtexture features and 2D-DCT high-frequency energy ratio ($R_{\text{HF}}$).
4. Semantic Web-PKI Trust Registry (Component B) with Levenshtein domain typosquatting protection.
5. Edge AI triage classifier (Component C) using a 48-dimensional handcrafted spatial gradient feature vector.

---

## 2. Baseline Inventory & Audit Findings

### 2.1 File & Module Structure

| Path / Module | Purpose | Status | Audit Notes |
| :--- | :--- | :--- | :--- |
| `backend/crypto/` | Ed25519 signing, key generation, and canonicalization | Operational | Uses pure standard Python `cryptography` library. |
| `backend/qr/` | QR code generation, CBOR+ZLIB payload coding, OpenCV detection | Operational | Encodes document metadata into `SDA1` compact binary format. |
| `backend/watermark/dwt_svd.py` | 1-level 2D Haar DWT + SVD watermarker | Operational | Embeds across full document image luminance; requires singular value aux data for extraction. |
| `backend/watermark/metrics.py` | PSNR, SSIM, NC, BER calculations | Operational | Correctly implements skimage SSIM and normalized correlation. |
| `backend/components/component_a/` | GLCM & DCT blind copy detection | Operational | Calibrated threshold model on microtexture. |
| `backend/components/component_b/` | Trust registry & domain validator | Operational | Fast SQLite lookup and Levenshtein distance check. |
| `backend/components/component_c/` | Edge AI classifier | Operational | Handcrafted 48-dim spatial centroid classifier saved as joblib. |
| `backend/generator/` | Multi-script document builder | Operational | Supports Latin and Devanagari across 3 templates. |
| `backend/attack_simulator/` | Synthetic digital & print-scan distortion simulator | Operational | Simulates JPEG, MTF blur, halftoning, tampering. |
| `backend/experiments/runner.py` | Ablation & cross-condition test runner | Operational | Outputs baseline CSVs in `results/`. |
| `tests/test_pipeline.py` | 8-test unit test suite | Operational | 8/8 passed. |
| `tests/test_all_scenarios.py` | 16-test scenario verification suite | Operational | 16/16 passed. Total test suite: 24/24 passed (41.55s). |

### 2.2 Baseline Results & Artifacts

All baseline results have been backed up to `results/backup_20261015/`:
- `ablation_study_results.csv`: 80 rows covering 10 sample runs across 5 schemes (A: QR Only, B: QR + Watermark, C: QR + Watermark + Comp A, D: QR + Watermark + A + B, E: Full System) under 4 attack regimes (`NONE`, `PRINT_SCAN`, `JPEG`, `TAMPER`).
- `cross_condition_evaluation.csv`: 54 rows evaluating multi-script (Latin, Devanagari), multi-template (Certificate, ID Card, Transcript), multi-printer (Brother Laser, HP LaserJet, Epson Inkjet), and multi-paper conditions (Bond, Glossy, Parchment).
- `ablation_comparison_chart.png` and `component_a_roc_curve.png`: Baseline evaluation plots.

---

## 3. Identification of Research Gaps to Implement

While the original system establishes strong multi-tier foundations, three crucial research gaps require immediate implementation:

### Gap 3: LSB vs. Transform-Domain (DWT–DCT) Watermarking Inside the QR Symbol
- **Deficiency in Baseline:** The original watermark was embedded across the entire document canvas luminance. It did not watermark inside the QR symbol itself.
- **Requirement:** Implement a dedicated QR-symbol watermarking module (`backend/qr_watermark/`) featuring:
  - Spatial LSB watermarking (1-bit / 2-bit planes).
  - Transform-domain DWT–DCT watermarking with block-based DCT on the LL/HL subbands.
  - Critical QR structural pattern masking (protecting finder patterns, timing bars, and quiet zones to prevent fatal decoder degradation).
  - Fair comparison under identical digital attacks: Gaussian noise, salt-and-pepper, Gaussian blur, JPEG compression, resizing, rotation, cropping, and contrast/brightness distortion.

### Gap 4: Real Physical Print–Scan–Reprint Pipeline
- **Deficiency in Baseline:** The previous print-scan evaluation was entirely software-simulated using halftoning and point-spread blur models. No real physical print-and-scan dataset or capture pipeline existed.
- **Requirement:** Build a real physical print–scan–reprint capture pipeline:
  - Generate standardized printable calibration sheets (`scripts/export_print_sheets.py`) with fiducial registration corners and sample IDs.
  - Establish a strict physical capture protocol (`docs/physical_capture_protocol.md`) for 1st-generation (print-scan) and 2nd-generation (reprint-scan).
  - Provide manifest validation (`scripts/validate_physical_manifest.py`) and capture evaluation (`scripts/evaluate_physical_captures.py`) tools that execute perspective correction, QR alignment, watermark extraction, and scannability evaluation.
  - Strictly enforce non-fabrication: Never simulate real captures or label synthetic degradation as physical data. Real captures remain marked as pending until physical samples are scanned.

### Gap 10: Watermark Imperceptibility vs. AI Classification Trade-off
- **Deficiency in Baseline:** The baseline classifier (`Component C`) used a fixed 48-dimensional handcrafted centroid model and did not investigate how watermark embedding strength affects classification or whether neural classifiers can discriminate between watermarked, authentic, tampered, and reprinted QR artefacts.
- **Requirement:**
  - Build and train a lightweight Convolutional Neural Network (CNN) in PyTorch alongside a non-neural Machine Learning baseline (Random Forest / SVM).
  - Enforce strict payload-leakage-safe dataset splitting (all variants of a unique QR payload ID remain strictly within one split: train, val, or test).
  - Sweep multiple embedding strengths ($\alpha$) for both LSB and DWT–DCT.
  - Measure PSNR, SSIM, watermark recovery (NC, BER), QR decoding success, classifier precision, recall, F1, balanced accuracy, FAR, and FRR.
  - Conduct a Pareto trade-off analysis identifying optimal stealth-performance operating points.

---

## 4. Preservation & Non-Regression Guarantee

1. Existing endpoints (`backend/app.py`), verifier engine (`backend/engine/verifier.py`), document generators (`backend/generator/`), and test suites (`tests/`) remain fully operational and unaltered in behavior.
2. New functionality is isolated into modular packages:
   - `backend/qr_watermark/`
   - `backend/attack_simulator/qr_attacks.py`
   - `backend/ml_classifier/`
   - `scripts/`
   - `results/gap3/`, `results/gap4/`, `results/gap10/`, `results/final/`
3. All baseline outputs are archived in `results/backup_20261015/`.
