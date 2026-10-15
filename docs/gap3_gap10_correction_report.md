# Comprehensive Gap 3 and Gap 10 Targeted Correction Report

**Project Title:** Stealth-Aware QR Watermarking for Secure Document Authentication  
**Author:** Bishal Paul (Reg. No. 23BCI0224, VIT Vellore)  
**Date of Audit & Correction:** October 15, 2026  
**Scope:** Strict targeted correction of **Gap 3** (LSB vs. DWT–DCT QR watermarking) and **Gap 10** (Watermark stealth vs. AI classification). **Gap 4 (Physical Print–Scan–Reprint Pipeline) is strictly preserved without modification.**

---

## 1. Executive Summary

This report documents the targeted technical corrections, empirical recalculations, and regression tests conducted to address discrepancies, metric misdefinitions, attack no-ops, and training class imbalances identified in the digital watermarking and machine learning subsystems:

1. **Gap 3 Discrepancies & Attack No-Ops Resolved:**
   - Traced all metrics directly to sample-level evaluations, eliminating reporting discrepancies between CSV results and documentation.
   - Identified and resolved the **Cropping No-Op Anomaly** (previous 8% crop only affected the white quiet zone border) by establishing a realistic 15% active module crop.
   - Identified and resolved the **Watermark Removal Anomaly** (previous $3 \times 3$ median filter preserved identical module LSB bits) by introducing active bit-plane scrubbing and dithering.
   - Completely separated **Embedding Imperceptibility** ($54.34\text{ dB}$ for LSB, $48.71\text{ dB}$ for DWT–DCT) from **Post-Attack Image Distortion** (e.g. $10.77\text{ dB}$ under crop, $18.34\text{ dB}$ under removal).
   - Upgraded structural masking to ISO/IEC 18004 compliance (protecting finder patterns, timing bars, 15-bit format information, fixed dark modules, version information for $v \ge 7$, and alignment patterns across all QR versions).
   - Implemented a **conservative DWT–DCT block eligibility rule** requiring 100% spatial module containment inside the data region, completely preventing transform coefficient bleed into structural patterns.

2. **Gap 10 Metric Inversion & Class Imbalance Resolved:**
   - Corrected inverted **False Acceptance Rate (FAR)** and **False Rejection Rate (FRR)** definitions under the convention Class 1 = Attack, Class 0 = Genuine:
     $$\text{FAR} = \frac{\text{FN}}{\text{FN} + \text{TP}} \quad (\text{Attacks incorrectly accepted as genuine})$$
     $$\text{FRR} = \frac{\text{FP}}{\text{FP} + \text{TN}} \quad (\text{Genuine samples incorrectly rejected as attacks})$$
   - Added unit tests with a known confusion matrix where $\text{FAR} = 20.0\% \ne \text{FRR} = 5.0\%$, guaranteeing that inverted formulas cannot pass unnoticed.
   - Dissected the previously reported score ($\text{F1} = 0.9474$, $\text{Balanced Accuracy} = 0.5000$, $\text{FAR} = 100.0\%$): proved that the unweighted CNN had degenerated to trivially predicting Class 1 for all samples due to 9:1 class imbalance.
   - Retrained `QRArtifactCNN` with **loss class weighting** ($w_0 = 5.000$, $w_1 = 0.556$). Balanced accuracy on held-out test payloads jumped from **$0.5000 \rightarrow 0.9444$**, Precision = **$1.0000$**, Recall = **$0.8889$**, F1 = **$0.9412$**, $\text{FAR} = 11.1\%$, $\text{FRR} = 0.0\%$.
   - Added a transparent **Majority-Class Baseline** (F1 = 0.9474, BalAcc = 0.5000) and **Random Forest Baseline** (F1 = 0.9881, BalAcc = 0.9826) evaluated on the identical test identities.
   - Validated consistency of the DWT–DCT parameter $\alpha$ as raw differential DCT coefficient modulation step size.

3. **Gap 4 Complete Preservation:**
   - Files under `data/physical/` (`manifest.csv`, `physical_print_sheet_BATCH-01.pdf`), `scripts/export_print_sheets.py`, `scripts/validate_physical_manifest.py`, `scripts/evaluate_physical_captures.py`, and `docs/physical_capture_protocol.md` were preserved without modification.

---

## 2. Part A — Detailed Gap 3 Corrections

### A1. Cause of Discrepancies
- **Root Cause:** In the previous release, numbers in `docs/reproducibility_report.md` were manually aggregated from earlier exploratory scripts rather than programmatically generated from the final 4,000-sample CSV manifest.
- **Resolution:** All summary metrics in `results/gap3/gap3_lsb_vs_dwtdct_results.csv` and `results/gap3/gap3_summary.json` are now strictly computed from the sample-level data in `data/synthetic/manifest.csv`.

### A2. Audit and Correction of Attack Implementations
1. **Cropping Attack (`CROP`):**
   - *Previous Defect:* `crop_ratio = 0.08` (8% border crop). In a $300 \times 300$ QR code with 4-module border, the quiet zone spans $\approx 14\%$ of the image width. Cropping 8% of the border removed only pure white quiet zone pixels and padded them with white pixels (`[255, 255, 255]`), resulting in an exact no-op ($\text{PSNR} = 54.18\text{ dB}$, $\Delta = 0$).
   - *Correction:* Set `crop_ratio = 0.15` (15%). This penetrates past the quiet zone into the active QR data and finder modules, producing measurable distortion ($\text{PSNR} = 10.77\text{ dB}$, $\Delta_{max} = 255$, $\text{QDSR} = 0.0\%$, $\text{BER} = 5.41\%$).
2. **Watermark Removal Attack (`WATERMARK_REMOVAL`):**
   - *Previous Defect:* Applied $3 \times 3$ median blur. Because QR modules are uniform blocks of $8 \times 8$ pixels possessing identical LSB values, a $3 \times 3$ median filter within a module left the module's LSB bit completely unaltered. Majority voting across hundreds of redundant pixels produced $\text{NC} = 1.000$ and $\text{BER} = 0.00\%$.
   - *Correction:* Implemented active bit-plane scrubbing (clearing the lower 2 bit-planes and injecting random dithering noise) combined with spatial median filtering ($k=5$). This attacks both spatial LSB and transform correlations, resulting in $\text{NC} = 0.5129$, $\text{BER} = 50.16\%$ for LSB, while transform-domain DWT–DCT demonstrates expected structural resilience ($\text{NC} = 0.7426$, $\text{BER} = 27.72\%$).
3. **Attack Verification:**
   All 9 attack regimes were verified to produce non-zero pixel differences:
   | Attack Name | Parameters | Max Pixel Difference | Mean Absolute Error |
   | :--- | :--- | :---: | :---: |
   | `GAUSSIAN_NOISE` | $\sigma = 15.0$ | 72 | 6.23 |
   | `SALT_PEPPER` | $p = 0.03$ | 255 | 3.88 |
   | `GAUSSIAN_BLUR` | $k = 5, \sigma = 1.2$ | 140 | 18.04 |
   | `JPEG_COMPRESSION`| Quality = 70 | 1 | 0.25 |
   | `RESIZE` | Scale = 0.75 | 51 | 4.55 |
   | `ROTATION` | $\theta = 3.0^\circ$ (with deskew) | 111 | 7.51 |
   | `CROP` | Crop Ratio = 0.15 | 255 | 21.67 |
   | `CONTRAST_ILLUMINATION` | $\alpha = 1.15, \beta = -15.0$ | 15 | 4.88 |
   | `WATERMARK_REMOVAL` | Bit-plane scrub + median ($k=5$) | 255 | 1.23 |

### A3. Separation of Image-Quality Metrics
The manifest and summary tables now record four independent metric categories:
1. **Embedding Imperceptibility (Host vs. Clean Watermarked):** `embedding_psnr_db` and `embedding_ssim`.
2. **Post-Attack Image Distortion (Host vs. Attacked):** `post_attack_psnr_db` and `post_attack_ssim`.
3. **Watermark Recovery (Original vs. Extracted Bits):** `extracted_nc` and `extracted_ber`.
4. **QR Readability (Optical Scanning):** `qr_decoded` and `decoded_payload`.

### A4. Structural Masking & QR Version Support
- [`backend/qr_watermark/masking.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/backend/qr_watermark/masking.py) now dynamically derives `version = (num_modules - 17) // 4` and enforces full ISO/IEC 18004 protection:
  - 3 Finder patterns with 1-module separators ($8 \times 8$).
  - Timing patterns (Row 6, Column 6).
  - Format information modules (Row 8, Column 8 around finders, 15 bits).
  - Fixed dark module at coordinate $(num\_modules - 8, 8)$.
  - Version information blocks ($6 \times 3$ and $3 \times 6$) for versions $\ge 7$.
  - Dynamic alignment patterns mapped from standard specification tables.
- **Conservative Transform Block Eligibility:** In [`backend/qr_watermark/dwt_dct.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/backend/qr_watermark/dwt_dct.py), `_get_eligible_blocks` now checks that $100\%$ of the spatial pixels across the block's footprint (`pixel_mask[r0:r1, c0:c1]`) are in the eligible data region, preventing IDWT ringing into protected functional modules.

### Measured Gap 3 Results (Before vs. After)

| Condition | Old LSB NC | **Corrected LSB NC** | Old LSB BER | **Corrected LSB BER** | Old DWT NC | **Corrected DWT NC** | Old DWT BER | **Corrected DWT BER** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CLEAN** | 1.0000 | **1.0000** | 0.00% | **0.00%** | 1.0000 | **1.0000** | 0.00% | **0.00%** |
| **GAUSSIAN_NOISE** | 0.5590 | **0.5611** | 41.25% | **40.91%** | 0.9731 | **0.9645** | 2.75% | **3.62%** |
| **SALT_PEPPER** | 1.0000 | **1.0000** | 0.00% | **0.00%** | 0.9831 | **0.9761** | 1.69% | **2.44%** |
| **GAUSSIAN_BLUR** | 0.9996 | **1.0000** | 0.03% | **0.00%** | 0.9021 | **0.9025** | 9.63% | **10.25%** |
| **JPEG_COMPRESSION**| 0.7212 | **0.6950** | 32.34% | **34.13%** | 0.7134 | **0.7725** | 24.44% | **20.12%** |
| **RESIZE** | 0.9956 | **0.9937** | 0.44% | **0.62%** | 0.9967 | **0.9944** | 0.34% | **0.56%** |
| **ROTATION** | 1.0000 | **1.0000** | 0.00% | **0.00%** | 0.8332 | **0.8494** | 17.03% | **15.91%** |
| **CROP (15%)** | 1.0000 *(no-op)* | **0.9494** | 0.00% *(no-op)* | **5.41%** | 1.0000 *(no-op)* | **0.9341** | 0.00% *(no-op)* | **6.37%** |
| **CONTRAST_ILLUM** | 0.4057 | **0.4300** | 75.00% | **73.28%** | 0.0000 | **0.0000** | 75.66% | **78.31%** |
| **WATERMARK_REMOVAL**| 1.0000 *(no-op)* | **0.5129** | 0.00% *(no-op)* | **50.16%** | 1.0000 *(no-op)* | **0.7426** | 0.00% *(no-op)* | **27.72%** |

---

## 3. Part B — Detailed Gap 10 Corrections

### B1. Correction of FAR and FRR Formulas
- Under binary classification where **Class 1 = Attack / Manipulated** and **Class 0 = Genuine**:
  - **False Acceptance (FA):** Occurs when an attacked sample (1) is incorrectly classified as genuine (0). In standard terminology, this is a **False Negative (FN)**.
    $$\text{FAR} = \frac{\text{FN}}{\text{FN} + \text{TP}} \times 100\%$$
  - **False Rejection (FR):** Occurs when a genuine sample (0) is incorrectly rejected as an attack (1). In standard terminology, this is a **False Positive (FP)**.
    $$\text{FRR} = \frac{\text{FP}}{\text{FP} + \text{TN}} \times 100\%$$
- **Fix in Code ([`backend/qr_watermark/benchmark_evaluator.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/backend/qr_watermark/benchmark_evaluator.py)):**
  Swapped the previous reversed variables (`far = fp/(fp+tn)` and `frr = fn/(fn+tp)`) to the mathematically correct formulas above.
- **Unit Test Regression:** Added a test in [`tests/test_watermark_benchmark.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/tests/test_watermark_benchmark.py) with 100 genuine and 200 attack samples ($\text{TP}=160, \text{FN}=40, \text{TN}=95, \text{FP}=5$), where $\text{FAR} = 20.0\%$ and $\text{FRR} = 5.0\%$, verifying that an inverted implementation will immediately fail.

### B2 & B3. Root Cause of F1 = 0.9474 and Balanced Accuracy = 0.5000
- **Diagnosis:**
  - In the synthetic dataset, 1 out of 10 conditions is CLEAN (Class 0: Genuine, 10%), while 9 are attacks (Class 1: Manipulated, 90%).
  - The previous unweighted cross-entropy loss allowed the CNN to minimize training loss by trivially predicting Class 1 for all samples.
  - When a model predicts Class 1 for every sample:
    - $\text{TP} = 720, \text{FP} = 80, \text{TN} = 0, \text{FN} = 0$.
    - $\text{Recall (ADR)} = 720 / 720 = 1.0000$.
    - $\text{Precision} = 720 / (720 + 80) = 0.9000$.
    - $\text{F1-Score} = 2 \times 0.9 \times 1.0 / 1.9 = 0.9474$.
    - $\text{Specificity} = 0 / 80 = 0.0000$.
    - $\text{Balanced Accuracy} = (1.0 + 0.0) / 2 = \mathbf{0.5000}$.
    - Under the previous swapped formula, FAR was reported as $80 / 80 = 100.0\%$. Under the true formula, $\text{FAR} = 0 / 720 = 0.0\%$ and $\text{FRR} = 80 / 80 = 100.0\%$.
  - Therefore, the previously reported F1 score was identical to a naive majority-class baseline.

- **Implementation of Balanced Loss & Baselines ([`backend/ml_classifier/train.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/backend/ml_classifier/train.py)):**
  1. Computed balanced class weights on the training split:
     $$w_0 = \frac{N_{train}}{2 \times N_{genuine}} = \frac{2400}{2 \times 240} = 5.000, \quad w_1 = \frac{N_{train}}{2 \times N_{manipulated}} = \frac{2400}{2 \times 2160} = 0.556$$
     Applied `nn.CrossEntropyLoss(weight=class_weights)`.
  2. Applied `class_weight='balanced'` to the Random Forest baseline.
  3. Implemented a transparent `MajorityClassBaseline` for direct scientific comparison.
  4. Evaluated all three models on the exact same 800 held-out test samples across 10 unique payload identities (zero payload leakage).

### Held-Out Test Evaluation Comparison (Gap 10)

| Model Architecture | Precision | Recall (ADR) | Specificity | F1-Score | Balanced Accuracy | FAR (%) | FRR (%) | Inference Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Majority Baseline** | 0.9000 | 1.0000 | 0.0000 | 0.9474 | 0.5000 | 0.0% | 100.0% | 0.00 ms |
| **QRArtifactCNN (Balanced Loss)** | **1.0000** | **0.8889** | **1.0000** | **0.9412** | **0.9444** | **11.1%** | **0.0%** | **17.75 ms** |
| **Random Forest Baseline** | **0.9986** | **0.9778** | **0.9875** | **0.9881** | **0.9826** | **2.2%** | **1.2%** | **0.01 ms** |

*Analysis:*
- The balanced `QRArtifactCNN` achieved a **Balanced Accuracy of 0.9444** (up from 0.5000) and **0.0% False Rejection Rate**, successfully learning to identify genuine clean watermarked QR symbols rather than trivially defaulting to Class 1.
- The Random Forest baseline achieved **0.9826 Balanced Accuracy** and **0.9881 F1-score** with sub-millisecond latency.

### B4. Stealth-Accuracy Pareto Trade-off
- Evaluated all 8 configurations across LSB ($k \in \{1, 2, 3\}$) and DWT–DCT ($\alpha \in \{10, 20, 30, 40, 50\}$).
- **Scale Definition:** $\alpha$ is defined as the raw differential DCT coefficient modulation step size ($|c_1 - c_2| = \alpha$), consistent across `dwt_dct.py`, synthetic datasets, benchmarks, and plots.
- **Trade-off Summary:**
  - `LSB_k1`: Clean $\text{PSNR} = 54.34\text{ dB}$, Scannability = $98.0\%$, Attack Recovery $\text{NC} = 0.7936$, $\text{BER} = 22.72\%$.
  - `DWTDCT_a20`: Clean $\text{PSNR} = 48.71\text{ dB}$, Scannability = $98.0\%$, Attack Recovery $\text{NC} = 0.7929$, $\text{BER} = 18.37\%$, CNN Balanced Accuracy = $0.9444$, RF Balanced Accuracy = $0.9722$.
  - Identified as the recommended balanced operating point: satisfies the $>45\text{ dB}$ imperceptibility requirement while maintaining superior lossy compression recovery ($\text{BER} = 20.12\%$ vs. LSB $34.13\%$).

---

## 4. Regression Testing & Audit Outcomes

1. **PyTest Benchmark & Unit Test Suite (`pytest -v tests/`):**
   - **34 out of 34 tests passed** in $21.77\text{ s}$ ($100\%$ pass rate).
   - Passed all new tests:
     - `test_06_benchmark_metrics_calculation`: Verified unequal FAR (20.0%) and FRR (5.0%).
     - `test_08_multi_version_masking`: Verified QR versions 1, 2, 4, and 7.
     - `test_09_attacks_transform_image`: Verified non-zero distortion across all attacks.
     - `test_10_dwt_dct_conservative_blocks`: Verified that all transform blocks are 100% inside eligible data modules.
2. **Complete System Verification Audit (`python run_complete_system_test.py`):**
   - **27 out of 27 checks passed** in $11.00\text{ s}$ ($100\%$ operational).
   - Verified Ed25519 signatures, canonical hashing, multi-script rendering (English/Latin and Hindi/Devanagari), photocopy detection, credential splicing, and Web-PKI revocation.
3. **Physical Pipeline Integrity Check (Gap 4):**
   - Validated that `data/physical/` and physical scripts were untouched.
   - All 12 physical capture records in `data/physical/manifest.csv` remain intact.

---

## 5. Summary of Files Changed

| Category | File Path | Description of Changes |
| :--- | :--- | :--- |
| **Backup** | `results/backup_gap3_gap10_20261015/` | Complete pre-correction backup of Gap 3 and Gap 10 code, models, and results. |
| **Metrics** | [`backend/qr_watermark/benchmark_evaluator.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/backend/qr_watermark/benchmark_evaluator.py) | Corrected FAR and FRR formulas for Class 1 = Attack, Class 0 = Genuine. |
| **Masking** | [`backend/qr_watermark/masking.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/backend/qr_watermark/masking.py) | Enhanced to ISO/IEC 18004: protects quiet zones, finders, timing, format info, dark module, and version info. |
| **QR Gen** | [`backend/qr_watermark/qr_generator.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/backend/qr_watermark/qr_generator.py) | Passes actual QR version to mask generator. |
| **DWT–DCT** | [`backend/qr_watermark/dwt_dct.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/backend/qr_watermark/dwt_dct.py) | Implemented conservative block eligibility rule ensuring 100% data mask overlap. |
| **Attacks** | [`backend/attack_simulator/qr_attacks.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/backend/attack_simulator/qr_attacks.py) | Corrected CROP (15% ratio) and WATERMARK_REMOVAL (bit-plane scrub + dithering + median). |
| **Dataset** | [`scripts/generate_synthetic_benchmark_dataset.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/scripts/generate_synthetic_benchmark_dataset.py) | Separated embedding from post-attack quality metrics; regenerated 4,000 samples. |
| **Benchmark**| [`scripts/run_gap3_benchmark.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/scripts/run_gap3_benchmark.py) | Separated embedding and attack metrics; saved updated `gap3_lsb_vs_dwtdct_results.csv`. |
| **Model** | [`backend/ml_classifier/model.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/backend/ml_classifier/model.py) | Added balanced class weighting support to `BaselineRFClassifier`. |
| **Training** | [`backend/ml_classifier/train.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/backend/ml_classifier/train.py) | Implemented balanced loss weighting ($w_0=5.000, w_1=0.556$) and Majority Baseline. |
| **Trade-Off**| [`scripts/run_gap10_benchmark.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/scripts/run_gap10_benchmark.py) | Evaluated corrected Pareto trade-off and saved updated results. |
| **Figures** | [`scripts/generate_publication_figures.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/scripts/generate_publication_figures.py) | Re-rendered Figures 4, 5, 8, 9, and 10 from newly measured data; fixed tick labels. |
| **Tests** | [`tests/test_watermark_benchmark.py`](file:///C:/Users/bisha/Downloads/secure-document-authentication/tests/test_watermark_benchmark.py) | Added regression tests for FAR/FRR, multi-version masking, attack transforms, and block safety. |

---

## 6. Commands to Reproduce Corrections

```bash
# 1. Run all regression tests (34 unit and scenario tests)
python -m pytest -v tests/

# 2. Run complete 27-check security and cryptographic audit
python run_complete_system_test.py

# 3. Regenerate synthetic benchmark dataset (4,000 samples)
python scripts/generate_synthetic_benchmark_dataset.py

# 4. Run Gap 3 benchmark (LSB vs DWT-DCT)
python scripts/run_gap3_benchmark.py

# 5. Train AI classifier and evaluate baselines
python backend/ml_classifier/train.py

# 6. Run Gap 10 benchmark & Pareto analysis
python scripts/run_gap10_benchmark.py

# 7. Re-generate all publication figures (300 DPI)
python scripts/generate_publication_figures.py
```
