# Physical Print–Scan–Reprint Capture and Evaluation Protocol

**Project Title:** Stealth-Aware QR Watermarking for Secure Document Authentication  
**Protocol Version:** 2.0 (Physical Validation Standard)  
**Author:** Bishal Paul (23BCI0224)  
**Storage Directories:**
- Raw Camera / Scanner Captures: `data/physical/raw/`
- Perspective-Rectified & Segmented QR Symbols: `data/physical/processed/`
- Experiment Manifest: `data/physical/manifest.csv`

---

## 1. Physical Hardware & Substrate Specifications

### 1.1 Printing Devices
1. **P1 (Monochrome Electro-photographic Laser):** Brother HL-L2321D / HP LaserJet Pro (Resolution: 600 DPI, toner particle micro-scattering).
2. **P2 (Continuous Ink Droplet Inkjet):** Epson EcoTank L3250 / Canon PIXMA (Resolution: 1200 DPI, liquid absorption bleed).
3. **P3 (Commercial High-Speed Photocopier / Secondary Reprint):** Xerox WorkCentre / Ricoh Aficio (Simulating secondary unauthorized reproduction).

### 1.2 Paper Substrates
1. **Substrate S1 (Standard Bond / Copy Paper):** 80 gsm wood-pulp multipurpose paper.
2. **Substrate S2 (Premium Executive Bond):** 100 gsm acid-free watermarked bond paper.
3. **Substrate S3 (Heavyweight Smooth Stock):** 200 gsm glossy photographic/cardstock paper.

### 1.3 Optical Digitization & Capture Hardware
1. **Scanner SC1 (Calibrated Flatbed Scanner):** Canon CanoScan LiDE 300 / Epson Perfection V39 (Optical resolution: 600 DPI, 24-bit RGB, uncompressed TIFF or lossless PNG).
2. **Mobile C1 (Handheld Smartphone Camera):** 48 MP / 12 MP camera sensor (e.g., iPhone 14/15, Samsung Galaxy S23, Google Pixel 7/8).
   - Ambient illuminance: 400–600 lux (standard diffuse indoor white LED).
   - Capture distance: 20–30 cm perpendicular to paper surface.
   - Tilt angles: $0^\circ$ (perpendicular), $15^\circ$ (handheld normal tilt), $30^\circ$ (perspective stress test).

---

## 2. Standardized Printable Calibration Sheet

The print sheet is generated programmatically at **300 DPI A4** ($2480 \times 3508$ pixels) using `scripts/export_print_sheets.py`.

### 2.1 Sheet Components
1. **Header Block:** Protocol metadata, trial batch UUID, timestamp, author name.
2. **Fiducial Registration Crosshairs:** Four corner markers located at $(150, 150)$, $(2330, 150)$, $(150, 3358)$, and $(2330, 3358)$ to enable exact 4-point perspective homography estimation.
3. **QR Sample Grid:** A structured $3 \times 2$ grid containing 6 distinct watermarked QR symbols (LSB vs. DWT–DCT across multiple strengths).
   - Physical dimensions: $50 \times 50\text{ mm}$ per QR code ($590 \times 590$ pixels at 300 DPI).
4. **Photometric Calibration Step-Wedge:** 8-step neutral density gray patches ($0\%, 15\%, 30\%, 45\%, 60\%, 75\%, 90\%, 100\%$ optical density) for scanner gamma compensation.
5. **Physical Metric Scale Bar:** 50 mm graduated millimeter ruler for physical scale verification.

---

## 3. Two-Generation Capture Methodology

```
               [ DIGITAL AUTHENTIC MASTER ]
                            │
               (Print on P1/P2 Laser/Inkjet)
                            │
                            ▼
              [ 1ST-GEN PHYSICAL PRINTOUT ]
                 /                     \
       (Flatbed Scan / Camera)    (Xerox Photocopier Reprint)
               /                         \
              ▼                           ▼
    [ 1ST-GEN CAPTURE (G1) ]    [ 2ND-GEN PRINTOUT (G2) ]
    Label: GENUINE / AUTHENTIC            │
                                 (Flatbed Scan / Camera)
                                          │
                                          ▼
                               [ 2ND-GEN CAPTURE (G2) ]
                               Label: REPRINT / SUSPICIOUS
```

### 3.1 First-Generation Capture (G1: Print-Scan)
1. Print the generated PDF sheet on Printer P1 at **100% scale (no fit-to-page scaling)**.
2. Allow ink/toner to stabilize for 5 minutes.
3. Place on flatbed scanner glass or flat desk under diffuse illumination.
4. Digitize at 600 DPI (scanner) or take perpendicular camera capture.
5. Save image in `data/physical/raw/G1_<printer>_<paper>_<device>_<trial>.png`.
6. Ground-Truth Label: `GENUINE`.

### 3.2 Second-Generation Capture (G2: Reprint-Scan)
1. Take the physical 1st-generation print sheet.
2. Duplicate using standard commercial photocopier (P3) in black-and-white / color photo mode onto Substrate S1.
3. Digitize the duplicated sheet using the same capture device under identical settings.
4. Save image in `data/physical/raw/G2_reprint_<printer>_<paper>_<device>_<trial>.png`.
5. Ground-Truth Label: `REPRINT_MANIPULATED`.

---

## 4. Manifest Schema (`data/physical/manifest.csv`)

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `sample_id` | str | Unique sample identifier (e.g. `PHYS-G1-001`) |
| `payload_id` | str | Document credential UUID encoded in QR |
| `watermark_method` | str | `LSB` or `DWT-DCT` |
| `embedding_strength`| float | Alpha parameter or bit-plane |
| `capture_stage` | str | `G1_PRINT_SCAN` or `G2_REPRINT_SCAN` |
| `printer_model` | str | Documented printer make and model |
| `paper_type` | str | Paper weight and stock name |
| `capture_device` | str | Scanner or smartphone camera model |
| `lighting_lux` | int | Measured ambient illumination in lux |
| `tilt_angle_deg` | float | Perspective tilt angle (0.0 for flatbed) |
| `raw_image_path` | str | Path relative to repository root |
| `ground_truth_label`| str | `GENUINE` or `MANIPULATED` |
| `verification_status`| str | `EVALUATED` or `PENDING_PHYSICAL_CAPTURE` |

---

## 5. Non-Fabrication Rule

In strict compliance with empirical research integrity:
- Simulated digital degradation (e.g., software Gaussian blur or halftoning filters) **must NEVER** be recorded in `data/physical/manifest.csv` or labeled as physical data.
- If physical printed and scanned captures have not yet been produced, all physical evaluation tables and metrics must be explicitly designated as **`[PENDING REAL USER CAPTURES]`**.
- The pipeline provides fully functional automated extraction, alignment, and scoring tools so that once real physical captures are placed in `data/physical/raw/`, evaluation executes seamlessly in a single command:
  ```bash
  python scripts/evaluate_physical_captures.py
  ```
