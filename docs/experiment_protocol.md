# Experimental Protocol and Benchmarking Specification

**Project Title:** Stealth-Aware QR Watermarking for Secure Document Authentication: Comparative Analysis of LSB and DWT–DCT, Physical Print–Scan–Reprint Robustness, and AI Classification  
**Author:** Bishal Paul (23BCI0224)  
**Standard Protocol Version:** 2.0 (Post-Audit Extended Edition)  

---

## 1. Research Objectives & Hypotheses

### 1.1 Research Questions
1. **RQ1 (Gap 3 - Transform vs. Spatial Domain):** How does transform-domain DWT–DCT watermarking inside a 2D QR barcode compare to spatial LSB watermarking in terms of visual imperceptibility (PSNR, SSIM), scannability preservation (standard OpenCV QR decoding), and resilience against digital attacks (compression, noise, filtering, geometric transforms)?
   - *Hypothesis 1 ($H_1$):* DWT–DCT watermarking significantly outperforms LSB in watermark recovery (higher NC, lower BER) under lossy JPEG compression and Gaussian filtering, while LSB achieves higher PSNR on clean images but suffers catastrophic failure under lossy compression.
2. **RQ2 (Gap 4 - Physical Print-Scan Channel):** How does real-world optical printing and scanning (1st generation) and photocopying/reprinting (2nd generation) degrade embedded QR watermarks and high-frequency spectral signatures compared to digital degradation models?
   - *Hypothesis 2 ($H_2$):* 2nd-generation reprinted QR codes exhibit pronounced high-frequency attenuation and luminance quantization, measurable by GLCM microtexture and watermark correlation drops, enabling reliable physical clone detection.
3. **RQ3 (Gap 10 - Stealth-Accuracy Trade-off):** What is the empirical relationship between watermark embedding strength ($\alpha$), QR visual imperceptibility, optical decodability, watermark survivability, and deep-learning classification accuracy?
   - *Hypothesis 3 ($H_3$):* Increasing embedding strength $\alpha$ improves watermark recovery and classifier attack-detection rate up to a critical threshold $\alpha^*$, beyond which optical scannability drops precipitously due to module edge deformation. A Pareto-optimal frontier balances imperceptibility ($\text{PSNR} > 40\text{ dB}$), scannability ($>95\%$), and classification F1 ($>0.90$).

---

## 2. Experimental Design and Variables

### 2.1 Independent Variables
1. **Watermarking Algorithm:**
   - Spatial Domain: LSB (1-bit plane replacement, 2-bit plane replacement).
   - Transform Domain: DWT–DCT (1-level Haar DWT followed by $8 \times 8$ block DCT, embedding pseudo-random watermark bits into mid-frequency coefficients).
2. **Watermark Embedding Strength:**
   - DWT–DCT: $\alpha \in \{0.05, 0.10, 0.20, 0.35, 0.50\}$.
   - LSB: Bit plane depth $k \in \{1, 2, 3\}$.
3. **Digital Attack Scenarios:**
   - `CLEAN` / `NONE`: Unattacked control baseline.
   - `GAUSSIAN_NOISE`: Zero-mean Gaussian noise ($\sigma \in \{5, 15, 25\}$).
   - `SALT_PEPPER`: Impulse noise (density $p \in \{0.01, 0.03, 0.05\}$).
   - `GAUSSIAN_BLUR`: Low-pass filter ($k_{\text{size}} \in \{3, 5, 7\}$).
   - `JPEG_COMPRESSION`: Lossy quantization ($Q \in \{30, 50, 70, 90\}$).
   - `RESIZE`: Downscale-upscale cycle (scale factors $s \in \{0.50, 0.75\}$).
   - `ROTATION`: Affine rotation with bilinear interpolation and deskew ($\theta \in \{1^\circ, 3^\circ, 5^\circ, 10^\circ\}$).
   - `CROP`: Center crop with border padding ($5\%, 10\%$).
   - `CONTRAST_BRIGHTNESS`: Linear scaling ($I' = \alpha_{\text{c}} I + \beta_{\text{b}}$ with $\alpha_{\text{c}} \in \{0.8, 1.2\}, \beta_{\text{b}} \in \{-20, +20\}$).
   - `QR_REPLACEMENT`: Splicing attack replacing genuine QR payload with forged payload.
   - `WATERMARK_REMOVAL`: Frequency-domain filtering attempting to strip watermark.

### 2.2 Dependent Variables & Metrics

| Metric | Symbol | Definition / Formula | Denominator / Scale |
| :--- | :--- | :--- | :--- |
| **Peak Signal-to-Noise Ratio** | $\text{PSNR}$ | $10 \log_{10} \left( \frac{255^2}{\text{MSE}} \right)$ | Decibels (dB), $[0, 100]$ |
| **Structural Similarity** | $\text{SSIM}$ | $\frac{(2\mu_x\mu_y + c_1)(2\sigma_{xy} + c_2)}{(\mu_x^2 + \mu_y^2 + c_1)(\sigma_x^2 + \sigma_y^2 + c_2)}$ | Dimensionless, $[-1, 1]$ |
| **Normalized Correlation** | $\text{NC}$ | $\frac{\sum_i w_i \cdot w'_i}{\sqrt{\sum_i w_i^2} \sqrt{\sum_i (w'_i)^2}}$ | Dimensionless, $[-1, 1]$ |
| **Bit Error Rate** | $\text{BER}$ | $\frac{\sum_{i=1}^N |b_i - b'_i|}{N} \times 100\%$ | Total watermark bits $N$, $[0, 100]\%$ |
| **Watermark Extraction Success** | $\text{WESR}$ | $\mathbb{I}(\text{NC} \ge \tau_{\text{NC}} \land \text{BER} \le \tau_{\text{BER}})$ | Binary thresholded rate ($\tau_{\text{NC}}=0.75, \tau_{\text{BER}}=20\%$) |
| **QR Decoding Success Rate** | $\text{QDSR}$ | $\frac{N_{\text{decoded}}}{N_{\text{total}}} \times 100\%$ | Total scanned QR instances, $[0, 100]\%$ |
| **Attack Detection Rate** | $\text{ADR}$ | $\frac{\text{True Positives (Attacks detected)}}{\text{Total Attacked Samples}} \times 100\%$ | Total attacked samples |
| **False Acceptance Rate** | $\text{FAR}$ | $\frac{\text{Forged or Attacked Samples Classified as Genuine}}{\text{Total Forged/Attacked Samples}} \times 100\%$ | Total fraudulent/attacked samples |
| **False Rejection Rate** | $\text{FRR}$ | $\frac{\text{Genuine Samples Rejected as Fraudulent}}{\text{Total Genuine Samples}} \times 100\%$ | Total authentic samples |
| **Classifier Precision** | $\text{P}$ | $\frac{\text{TP}}{\text{TP} + \text{FP}}$ | Positive predictions |
| **Classifier Recall** | $\text{R}$ | $\frac{\text{TP}}{\text{TP} + \text{FN}}$ | Ground-truth positives |
| **Classifier F1-Score** | $\text{F1}$ | $2 \cdot \frac{P \cdot R}{P + R}$ | Harmonic mean |
| **Balanced Accuracy** | $\text{BA}$ | $\frac{1}{2} \left( \frac{\text{TP}}{\text{TP} + \text{FN}} + \frac{\text{TN}}{\text{TN} + \text{FP}} \right)$ | Class-balanced mean |
| **Latency** | $t_{\text{embed}}, t_{\text{extract}}, t_{\text{infer}}$ | Execution duration per instance | Milliseconds (ms) |

---

## 3. Dataset Generation and Partitioning Protocol

### 3.1 Non-Leakage Grouping Principle
To guarantee scientific validity and eliminate optimistic data leakage:
- All samples are grouped by **Unique Payload ID** ($UID$).
- A unique QR payload represents an individual document credential (UUIDv4 + timestamp + canonical fields).
- **Rule:** Every derivative of a payload (clean watermarked, all 10 attack variants, multiple embedding strengths, repeated captures) MUST be assigned to the **same split**.
- Under no circumstance may variant $A$ of payload $i$ appear in train while variant $B$ of payload $i$ appears in test.

### 3.2 Target Dataset Partitioning
- **Total Unique QR Payloads:** 50 distinct cryptographic credentials.
- **Split Ratio:**
  - Training Set: 30 payloads ($60\%$).
  - Validation Set: 10 payloads ($20\%$).
  - Test Set (Held-out Digital): 10 payloads ($20\%$).
- **Per-Payload Derivations:**
  - Methods: 2 (LSB, DWT–DCT).
  - Strengths per method: 3 (Low, Medium, High).
  - Conditions per instance: 1 Clean + 9 Digital Attacks + 1 Forgery/Tamper = 11 conditions.
  - Total Synthetic Images Generated: $50 \times 2 \times 3 \times 11 = 3,300$ fully tracked image samples.

---

## 4. Hardware, Environment, & Determinism Controls

- **Operating System:** Windows 11 (AMD64).
- **Execution Runtime:** Python 3.13.5 (CPython).
- **Primary Libraries:** PyTorch 2.14.1 (CPU), OpenCV 5.0.0, PyWavelets 1.10.0, Scikit-Learn 1.9.0, ReportLab 5.0.1, python-docx 1.2.0.
- **Random Seeds:**
  - Global NumPy Seed: `42`.
  - Global PyTorch Seed: `42`.
  - Python `random` Seed: `42`.
  - HMAC-SHA256 Secret Seed: `b"SDA-Watermark-Secret-Key-2026-VIT"`.

---

## 5. Physical Capture Protocol Requirements (Gap 4)

- Real physical captures require actual printouts on physical paper and digitizations via optical scanners or smartphone cameras.
- Synthetic noise MUST NOT be recorded as physical data.
- The pipeline provides printable sheet templates (`scripts/export_print_sheets.py`), manifest validation (`scripts/validate_physical_manifest.py`), and capture evaluators (`scripts/evaluate_physical_captures.py`).
- Until physical prints and scans are supplied by the user, the physical results table will be transparently designated as `[PENDING USER PHYSICAL CAPTURE]` with full reproduction instructions.
