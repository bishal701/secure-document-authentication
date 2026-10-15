# Secure Document Authentication System
### Research Prototype: Hybrid QR + DWT-SVD Watermarking + Blind Copy Detection + Web-PKI + Edge AI
**Course:** Digital Watermarking and Steganography (BCSE323L) — Fall Semester 2026-2027  
**Author:** Bishal Paul (Registration Number: 23BCI0224)  

---

## 🌟 Overview

This project implements the complete research prototype specified in the **Secure Document Authentication Implementation Roadmap (Levels 0 through 10, Phases 1 through 17)**. It provides a multi-layer defense against physical photocopies, digital splicing/tampering, and institutional domain impersonation.

```
       [ ORIGINAL DOCUMENT ]
                 |
  +--------------+--------------+
  |                             |
  v                             v
[Ed25519 Signed QR Code]    [DWT-SVD Watermark]
(CBOR + ZLIB compressed)    (Embedded in Luminance)
  |                             |
  +--------------+--------------+
                 |
                 v
     [ AUTHENTICATED CREDENTIAL ]
                 |
  [ Physical Print / Scan / Attack ]
                 |
                 v
   [ 8-STAGE UNIFIED VERIFICATION ]
   1. QR Code Readability & CBOR Decode
   2. Web-PKI Institutional Enrollment Check
   3. Ed25519 Cryptographic Signature Check
   4. SHA-256 Canonical Digest Match
   5. DWT-SVD Watermark NC & BER Analysis
   6. Component A: Blind Copy Detection (GLCM & DCT)
   7. Component B: Typosquatting / Homoglyph Check
   8. Component C: Secondary Edge AI Triage
                 |
                 v
  VERIFIED / VERIFIED-WITH-WARNING / SUSPICIOUS / INVALID
```

---

## 🚀 Quick Start & Running the Demo

To launch the complete application (FastAPI backend + interactive Web UI):

```bash
python run_demo.py
```

Your default browser will automatically open to:
```
http://127.0.0.1:8000/
```

---

## 🧪 Running Automated Unit Tests

To run the complete 8-test verification suite:

```bash
python -m unittest tests/test_pipeline.py
```

Expected output:
```
Ran 8 tests in ~1.3s
OK
```

---

## 🔬 Extended Research Project: QR Watermarking, Physical Pipeline & Edge AI

This repository extends the baseline document authentication system into a rigorous, reproducible experimental research platform resolving three foundational research gaps:

| Research Gap | Focus & Technical Implementation | Validation Location |
| :--- | :--- | :--- |
| **Gap 3: LSB vs. Transform QR Watermarking** | Structural pattern masking isolating finder patterns; fair comparison of Spatial LSB vs. Transform DWT–DCT under 10 identical digital attacks | `backend/qr_watermark/`, `results/gap3/` |
| **Gap 4: Real Print–Scan–Reprint Validation** | Reproducible physical data-collection pipeline with 300 DPI A4 sheets, fiducial crosshairs, step-wedges, manifest integrity, and perspective evaluators | `data/physical/`, `scripts/export_print_sheets.py` |
| **Gap 10: Stealth–Accuracy Pareto Trade-off** | 4,000-sample leakage-safe synthetic dataset grouped by unique payload ID; PyTorch edge CNN (`QRArtifactCNN`) vs. RF baseline; multi-strength Pareto frontier | `backend/ml_classifier/`, `results/gap10/` |

---

## ⚡ Reproduction Commands

To reproduce the entire scientific benchmark from scratch:

```bash
# 1. Install verified dependencies
pip install -r requirements.txt

# 2. Run the complete automated test suite (31 tests)
python -m pytest tests/

# 3. Generate the 4,000-sample leakage-safe synthetic dataset
python scripts/generate_synthetic_benchmark_dataset.py

# 4. Run Gap 3 digital attack comparative benchmark (LSB vs DWT-DCT)
python scripts/run_gap3_benchmark.py

# 5. Train edge CNN and evaluate against Random Forest baseline
python backend/ml_classifier/train.py

# 6. Run Gap 10 strength trade-off and Pareto frontier analysis
python scripts/run_gap10_benchmark.py

# 7. Generate all 10 publication-quality 300 DPI figures
python scripts/generate_publication_figures.py

# 8. Compile the research paper (Editable DOCX and Matching PDF)
python scripts/generate_research_manuscript.py

# 9. Physical Pipeline (When hardware is available):
python scripts/export_print_sheets.py
python scripts/validate_physical_manifest.py
python scripts/evaluate_physical_captures.py
```

---

## 📁 Extended Project Directory Structure

```
secure-document-authentication/
|-- backend/
|   |-- app.py                     # FastAPI REST server & routing
|   |-- config.py                  # System thresholds & paths
|   |-- crypto/                    # Ed25519 signing & canonicalization
|   |-- qr/                        # CBOR/ZLIB encoding & OpenCV QR detector
|   |-- qr_watermark/              # Gap 3: LSB, DWT-DCT, masking, and benchmark metrics
|   |-- ml_classifier/             # Gap 10: PyTorch QRArtifactCNN and RF baseline
|   |-- watermark/                 # Baseline 2D DWT + SVD canvas watermarker
|   |-- components/
|   |   |-- component_a/           # Blind copy detection (GLCM & DCT frequency)
|   |   |-- component_b/           # Semantic Web-PKI & Levenshtein domain validator
|   |   `-- component_c/           # Secondary Edge AI classifier
|   |-- generator/                 # High-resolution rendering (multi-template/script)
|   |-- engine/                    # Unified 8-stage verification pipeline
|   `-- attack_simulator/          # Distortion engine & QR attack taxonomy
|-- data/
|   |-- physical/                  # Gap 4: Printable sheets, raw/processed captures, manifest.csv
|   `-- synthetic/                 # Gap 10: 4,000 images, leakage-safe manifest.csv
|-- docs/
|   |-- implementation_audit.md    # Pre-implementation baseline audit
|   |-- experiment_protocol.md     # Standardized experimental protocol & metrics
|   |-- physical_capture_protocol.md # Physical print-scan-reprint procedure
|   `-- reproducibility_report.md  # Comprehensive reproducibility report
|-- models/
|   |-- qr_cnn_best.pth            # Trained PyTorch edge CNN weights (366 KB)
|   `-- rf_baseline.joblib         # Trained Random Forest baseline model
|-- paper/
|   |-- Stealth_Aware_QR_Watermarking_Research_Manuscript.docx # Editable 17-section DOCX
|   `-- Stealth_Aware_QR_Watermarking_Research_Manuscript.pdf  # Publication-grade PDF (1.5 MB)
|-- results/
|   |-- backup_20261015/           # Dated archive of baseline results
|   |-- gap3/                      # LSB vs DWT-DCT comparative results & summary
|   |-- gap4/                      # Physical evaluation summary & results
|   |-- gap10/                     # Stealth-accuracy trade-off, history & predictions
|   `-- final/                     # Figures 1 to 10 & final reproducibility report
|-- scripts/
|   |-- generate_synthetic_benchmark_dataset.py
|   |-- run_gap3_benchmark.py
|   |-- run_gap10_benchmark.py
|   |-- export_print_sheets.py
|   |-- validate_physical_manifest.py
|   |-- evaluate_physical_captures.py
|   |-- generate_publication_figures.py
|   `-- generate_research_manuscript.py
|-- tests/
|   |-- test_pipeline.py           # 8 original unit tests
|   |-- test_all_scenarios.py      # 16 original scenario tests
|   `-- test_watermark_benchmark.py# 7 newly added benchmark tests
|-- requirements.txt               # Pinned dependencies
|-- run_demo.py                    # Interactive launcher
`-- README.md
```
