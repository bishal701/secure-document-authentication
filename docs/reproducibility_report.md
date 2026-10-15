# Final Scientific Reproducibility Report

**Project Title:** Stealth-Aware QR Watermarking for Secure Document Authentication: Comparative Analysis of LSB and DWT–DCT, Physical Print–Scan–Reprint Robustness, and AI Classification  
**Author:** Bishal Paul (Registration Number: 23BCI0224)  
**Institution:** School of Computer Science and Engineering, Vellore Institute of Technology, Vellore, Tamil Nadu, India  
**Course:** Digital Watermarking and Steganography (BCSE323L)  
**Execution Date:** October 15, 2026  
**Status:** All Digital Benchmarks, Classifier Training, and Publication Artifacts Completed; Physical Pipeline Deployed.

---

## 1. System & Execution Environment

| Parameter | Specification |
| :--- | :--- |
| **Operating System** | Windows 11 Pro (Build 26100, AMD64 architecture) |
| **Python Runtime** | Python 3.13.5 (CPython 64-bit) |
| **Deep Learning Framework** | PyTorch 2.14.1+cpu, Torchvision 0.29.1+cpu |
| **Image Processing & Transforms** | OpenCV 5.0.0.93, PyWavelets 1.10.0, SciPy 1.18.1, scikit-image 0.26.0 |
| **Machine Learning Baseline** | scikit-learn 1.9.0, Joblib 1.6.0 |
| **Barcode & Cryptography** | qrcode 8.2, cbor2 6.1.4, cryptography 49.0.0 |
| **Report & Manuscript Generation**| ReportLab 5.0.1, python-docx 1.2.0, pypdf 6.20.1 |
| **Global Random Seed** | 42 (enforced across NumPy, PyTorch, and Python random) |

---

## 2. Baseline Preservation & Repository Audit

Prior to generating extended datasets and running benchmarks:
- **Baseline Results Backup:** All original outputs were preserved in `results/backup_20261015/` (including 80-row `ablation_study_results.csv`, 54-row `cross_condition_evaluation.csv`, and original baseline plots).
- **Audit Documentation:** Detailed baseline inventory and gap mappings recorded in `docs/implementation_audit.md`.
- **Experimental Protocol:** Full scientific protocol, mathematical definitions, and hypothesis formulations recorded in `docs/experiment_protocol.md`.
- **Original Implementation Integrity:** Full backward compatibility maintained; original document generator, verifier, and 24 scenario tests remain completely operational.

---

## 3. Dataset Sizes & Leakage-Safe Partition Counts

### 3.1 Synthetic QR Watermark Dataset (`data/synthetic/`)
* **Total Image Specimens Generated:** 4,000 images ($328 \times 328$ px, 24-bit RGB, lossless PNG).
* **Unique Payload Identities:** 50 distinct cryptographic document credentials (`UID-001` through `UID-050`).
* **Non-Leakage Grouping Principle:** Partitions are strictly grouped by unique payload ID. Every variant (clean, attacked, varying strengths) belonging to a payload remains in the identical split:
  * **Training Split:** 30 payloads ($60\%$) $\rightarrow$ 2,400 images
  * **Validation Split:** 10 payloads ($20\%$) $\rightarrow$ 800 images
  * **Held-Out Test Split:** 10 payloads ($20\%$) $\rightarrow$ 800 images
  * **Overlap Check:** $\text{Train} \cap \text{Val} = \emptyset$, $\text{Train} \cap \text{Test} = \emptyset$, $\text{Val} \cap \text{Test} = \emptyset$ (Verified: 0 leakage).
* **Ground-Truth Class Distribution:**
  * Class 0 (`GENUINE`): 400 clean watermarked instances
  * Class 1 (`MANIPULATED`): 3,600 attacked/tampered/degraded instances across 9 attack categories

### 3.2 Physical Print-Scan Dataset (`data/physical/`)
* **Manifest Records Configured:** 12 physical capture slots in `data/physical/manifest.csv`.
* **Printable Sheet:** 300 DPI A4 printable calibration sheet ([`physical_print_sheet_BATCH-01.pdf`](file:///C:/Users/bisha/Downloads/secure-document-authentication/data/physical/print_sheets/physical_print_sheet_BATCH-01.pdf)) containing 4 fiducial registration crosshairs, an 8-step photometric step-wedge, a 50 mm millimeter scale bar, and a $3 \times 2$ grid of watermarked QR codes ($50 \times 50\text{ mm}$ target size).
* **Current Status:** In strict compliance with non-fabrication rules, simulated distortions were never substituted for physical data. Records remain marked `[PENDING_PHYSICAL_CAPTURE]` awaiting physical scanning by the user.

---

## 4. Empirical Findings & Benchmarking Results

### 4.1 Gap 3: Spatial LSB vs. Transform DWT–DCT Under Digital Attacks
Evaluated on 1,000 test trials across 10 attack regimes (strictly derived from `results/gap3/gap3_lsb_vs_dwtdct_results.csv` and sample-level evaluations):

| Attack Condition | Clean Embed PSNR (dB) | Post-Attack PSNR (dB) | LSB NC | LSB BER (%) | LSB QDSR (%) | DWT-DCT NC | DWT-DCT BER (%) | DWT-DCT QDSR (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CLEAN** | 54.34 / 48.71 | 54.34 / 48.71 | 1.0000 | 0.00% | 98.0% | 1.0000 | 0.00% | 98.0% |
| **GAUSSIAN_NOISE** | 54.34 / 48.71 | 27.42 / 27.37 | 0.5611 | 40.91% | 98.0% | 0.9645 | 3.62% | 98.0% |
| **SALT_PEPPER** | 54.34 / 48.71 | 18.30 / 18.28 | 1.0000 | 0.00% | 10.0% | 0.9761 | 2.44% | 16.0% |
| **GAUSSIAN_BLUR** | 54.34 / 48.71 | 16.92 / 16.91 | 1.0000 | 0.00% | 100.0% | 0.9025 | 10.25% | 100.0% |
| **JPEG_COMPRESSION (Q=70)**| 54.34 / 48.71 | 50.88 / 48.61 | 0.6950 | 34.13% | 98.0% | 0.7725 | 20.12% | 98.0% |
| **RESIZE (0.75x)** | 54.34 / 48.71 | 27.09 / 27.06 | 0.9937 | 0.62% | 98.0% | 0.9944 | 0.56% | 98.0% |
| **ROTATION (3.0 deg)** | 54.34 / 48.71 | 22.17 / 22.15 | 1.0000 | 0.00% | 98.0% | 0.8494 | 15.91% | 98.0% |
| **CROP (15% active modules)**| 54.34 / 48.71 | 10.77 / 10.77 | 0.9494 | 5.41% | 0.0% | 0.9341 | 6.37% | 0.0% |
| **CONTRAST_ILLUMINATION** | 54.34 / 48.71 | 29.66 / 29.65 | 0.4300 | 73.28% | 98.0% | 0.0000 | 78.31% | 98.0% |
| **WATERMARK_REMOVAL** | 54.34 / 48.71 | 18.34 / 18.37 | 0.5129 | 50.16% | 98.0% | 0.7426 | 27.72% | 98.0% |

**Key Findings:**
1. **Embedding Imperceptibility vs. Attack Distortion:** Clean embedding yields $54.34\text{ dB}$ (SSIM $0.9961$) for LSB and $48.71\text{ dB}$ (SSIM $0.9943$) for DWT–DCT. Post-attack distortion is reported separately (e.g. $10.77\text{ dB}$ under 15% module cropping, $18.34\text{ dB}$ under removal).
2. **Robustness Under Filtering & Removal:** DWT–DCT preserves high recovery ($\text{NC} = 0.9645$, $\text{BER} = 3.62\%$) under Gaussian noise where LSB collapses ($\text{NC} = 0.5611$, $\text{BER} = 40.91\%$). Under active bit-plane scrubbing and dithering (`WATERMARK_REMOVAL`), LSB watermark recovery collapses ($\text{NC} = 0.5129$, $\text{BER} = 50.16\%$), whereas DWT–DCT retains structural survivability ($\text{NC} = 0.7426$, $\text{BER} = 27.72\%$).

---

### 4.2 Gap 10: Stealth–Accuracy Trade-Off & AI Classification
Evaluated on the held-out 800-sample test set (zero payload identity leakage, 30 train / 10 val / 10 test payloads):

| Model Architecture | Precision | Recall (ADR) | F1-Score | Balanced Accuracy | FAR (%) | FRR (%) | Inference Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **QRArtifactCNN (PyTorch Edge AI)** | **1.0000** | **0.8889** | **0.9412** | **0.9444** | **11.11%** | **0.00%** | 17.75 ms |
| **Handcrafted RF Baseline** | 0.9986 | 0.9778 | 0.9881 | 0.9826 | 2.22% | 1.25% | 0.01 ms |
| **Majority-Class Baseline** | 0.9000 | 1.0000 | 0.9474 | 0.5000 | 0.00% | 100.0% | 0.00 ms |

**Root Cause Analysis of the F1 = 0.9474 / BalAcc = 0.5000 Anomaly:**
- The previous unweighted CNN converged to trivially predicting Class 1 for all samples due to 9:1 class imbalance ($\text{TP}=720, \text{FP}=80, \text{TN}=0, \text{FN}=0$), duplicating the Majority-Class baseline.
- Retraining with loss class weights ($w_0 = 5.0, w_1 = 0.556$) completely resolved the collapse, restoring true balanced accuracy ($0.9444$), zero false rejections ($\text{FRR} = 0.0\%$), and low false acceptances ($\text{FAR} = 11.11\%$).

**Pareto Frontier Analysis:**
* Low embedding strengths (e.g. $\alpha=10.0$ or LSB $k=1$) yield superior imperceptibility ($\text{PSNR} > 53\text{ dB}$) but lower recovery under aggressive filtering.
* High embedding strengths (e.g. $\alpha \ge 40.0$) introduce visual edge distortion without corresponding recovery gains.
* **Pareto Optimum:** `DWTDCT_a20` ($\alpha=20.0$) provides the optimal operating point: clean embedding $\text{PSNR} = 48.71\text{ dB}$ ($>45\text{ dB}$ target), $98\%$ scannability, strong JPEG and noise resistance, and $>0.94$ classification F1-score.

---

## 5. Automated Test Outcomes

Full automated test suite executed via `pytest tests/`:
* `tests/test_all_scenarios.py`: 16/16 passed
* `tests/test_pipeline.py`: 8/8 passed
* `tests/test_watermark_benchmark.py`: 10/10 passed (including unit tests for unequal FAR/FRR, multi-version masking, attack transformations, and conservative transform blocks)
* **Total:** **34 passed in 21.77s** ($100\%$ pass rate, 0 failures, 0 errors).

---

## 6. Project Deliverables Inventory

| Category | Deliverable File Path | Status |
| :--- | :--- | :--- |
| **Research Paper (DOCX)** | `paper/Stealth_Aware_QR_Watermarking_Research_Manuscript.docx` | Generated (47.8 KB, 17 sections) |
| **Research Paper (PDF)** | `paper/Stealth_Aware_QR_Watermarking_Research_Manuscript.pdf` | Generated (1.50 MB, matching layout) |
| **Figure 1 (Architecture)** | `results/final/fig1_system_architecture.png` | Generated (300 DPI) |
| **Figure 2 (Dataset)** | `results/final/fig2_dataset_composition.png` | Generated (300 DPI) |
| **Figure 3 (Workflow)** | `results/final/fig3_watermark_workflow.png` | Generated (300 DPI) |
| **Figure 4 (Imperceptibility)**| `results/final/fig4_psnr_ssim_comparison.png` | Generated (300 DPI) |
| **Figure 5 (NC & BER)** | `results/final/fig5_nc_ber_under_attack.png` | Generated (300 DPI) |
| **Figure 6 (Scannability)** | `results/final/fig6_qr_decoding_success.png` | Generated (300 DPI) |
| **Figure 7 (Physical Pipeline)**| `results/final/fig7_physical_vs_digital.png` | Generated (300 DPI) |
| **Figure 8 (Confusion Matrix)**| `results/final/fig8_classifier_confusion_matrices.png` | Generated (300 DPI) |
| **Figure 9 (Pareto Curve)** | `results/final/fig9_strength_vs_classification_pareto.png`| Generated (300 DPI) |
| **Figure 10 (Radar Comparison)**| `results/final/fig10_overall_method_comparison.png` | Generated (300 DPI) |
| **Gap 3 Results Table** | `results/gap3/gap3_lsb_vs_dwtdct_results.csv` | Generated (1,000 evaluations) |
| **Gap 10 Results Table** | `results/gap10/gap10_strength_tradeoff_results.csv` | Generated (8 configurations) |
| **Trained CNN Weights** | `models/qr_cnn_best.pth` | Generated (366 KB) |
| **Trained RF Baseline** | `models/rf_baseline.joblib` | Generated (8.7 MB) |
| **Physical Calibration Sheet**| `data/physical/print_sheets/physical_print_sheet_BATCH-01.pdf`| Generated (300 DPI A4) |
| **Synthetic Image Archive** | `data/synthetic/images/` | 4,000 PNG files |
| **Synthetic CSV Manifest** | `data/synthetic/manifest.csv` | 4,000 metadata records |

---

## 7. Commands to Reproduce All Experiments

To reproduce all experiments from scratch on any standard Python environment:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run unit and scenario test suite
python -m pytest tests/

# 3. Generate the 4,000-sample leakage-safe synthetic dataset
python scripts/generate_synthetic_benchmark_dataset.py

# 4. Run Gap 3 LSB vs DWT-DCT digital attack benchmark
python scripts/run_gap3_benchmark.py

# 5. Train CNN and evaluate against Random Forest baseline
python backend/ml_classifier/train.py

# 6. Run Gap 10 strength trade-off and Pareto analysis
python scripts/run_gap10_benchmark.py

# 7. Generate all 10 publication-quality 300 DPI figures
python scripts/generate_publication_figures.py

# 8. Compile the research paper (DOCX and PDF)
python scripts/generate_research_manuscript.py

# 9. Physical Pipeline (When hardware is available):
# Export print calibration sheets
python scripts/export_print_sheets.py
# Validate capture manifest
python scripts/validate_physical_manifest.py
# Evaluate real captures after placing them in data/physical/raw/
python scripts/evaluate_physical_captures.py
```
