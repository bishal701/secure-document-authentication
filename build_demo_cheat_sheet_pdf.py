import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / "Secure_Document_Authentication_Sequential_Demo_and_Viva_Cheat_Sheet.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0f2942"))
        self.drawString(36, 758, "SECURE DOCUMENT AUTHENTICATION — DEMONSTRATION & VIVA CHEAT SHEET")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawRightString(576, 758, "BCSE323L | Fall 2026-2027")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.6)
        self.line(36, 752, 576, 752)
        self.line(36, 40, 576, 40)
        self.setFont("Helvetica", 8)
        self.drawString(36, 28, "Confidential — Academic Research Defense & Placement Reference")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(576, 28, page_text)
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    navy = colors.HexColor("#0f2942")
    blue = colors.HexColor("#1d4ed8")
    teal = colors.HexColor("#0f766e")
    slate = colors.HexColor("#334155")
    card_bg = colors.HexColor("#f8fafc")
    border_color = colors.HexColor("#e2e8f0")
    green = colors.HexColor("#15803d")
    red = colors.HexColor("#b91c1c")
    amber = colors.HexColor("#b45309")

    title_style = ParagraphStyle(
        'MainTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        textColor=navy, alignment=1, spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'SubTitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14,
        textColor=colors.HexColor("#475569"), alignment=1, spaceAfter=12
    )
    h1_style = ParagraphStyle(
        'H1', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=13, leading=17,
        textColor=navy, spaceBefore=10, spaceAfter=4, keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=10.5, leading=14,
        textColor=blue, spaceBefore=6, spaceAfter=3, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=slate, spaceAfter=4
    )
    bullet_style = ParagraphStyle(
        'Bullet', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.2, leading=11.5,
        textColor=slate, leftIndent=12, spaceAfter=2
    )
    bold_bullet_style = ParagraphStyle(
        'BoldBullet', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.2, leading=11.5,
        textColor=navy, leftIndent=12, spaceAfter=2
    )
    talk_style = ParagraphStyle(
        'Talk', parent=styles['Normal'],
        fontName='Helvetica-Oblique', fontSize=8.2, leading=11.5,
        textColor=colors.HexColor("#1e3a8a"), leftIndent=8
    )
    th_style = ParagraphStyle(
        'TH', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8, leading=10,
        textColor=colors.white, alignment=1
    )
    td_style = ParagraphStyle(
        'TD', parent=styles['Normal'],
        fontName='Helvetica', fontSize=7.8, leading=10,
        textColor=navy
    )
    td_bold = ParagraphStyle(
        'TDBold', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=7.8, leading=10,
        textColor=navy
    )

    story = []

    # Title Block
    story.append(Paragraph("Secure Document Authentication Using Hybrid QR Codes & Invisible Watermarking", title_style))
    story.append(Paragraph("<b>Comprehensive Sequential Demonstration Protocol, Module Breakdown, & Viva Cheat Sheet</b><br/>"
                           "Course: Digital Watermarking & Steganography (BCSE323L) | Target: Evaluation, Viva & Placement Interviews", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=blue, spaceAfter=10))

    # SECTION 1: MASTER SEQUENTIAL PROTOCOL
    story.append(Paragraph("1. Master Sequential Demonstration Protocol (5 Steps to Present)", h1_style))
    story.append(Paragraph("When demonstrating this project to professors, evaluators, or placement interviewers, execute the demonstration in this exact chronological order. Each step logically builds on the previous one to tell a complete, compelling security story.", body_style))

    steps_data = [
        [
            Paragraph("<b>Sequence</b>", th_style),
            Paragraph("<b>Web Tab / Action</b>", th_style),
            Paragraph("<b>What to Do (Hands-on)</b>", th_style),
            Paragraph("<b>Key Observable Output</b>", th_style),
            Paragraph("<b>Research Gap Solved</b>", th_style)
        ],
        [
            Paragraph("<b>STEP 1</b>", td_bold),
            Paragraph("<b>🎓 Document Studio</b><br/>(Issuance)", td_style),
            Paragraph("Enter recipient details (e.g. <i>Aarav Sharma</i>, 23BCI0888), select template, click <b>Cryptographically Seal & Issue</b>.", td_style),
            Paragraph("High-res diploma rendered with Ed25519 signature in CBOR-ZLIB QR, invisible DWT-SVD embedded (PSNR &gt; 51 dB).", td_style),
            Paragraph("Gaps 1 & 2 (High-density QR & imperceptible watermarking)", td_style)
        ],
        [
            Paragraph("<b>STEP 2</b>", td_bold),
            Paragraph("<b>🔍 Verification Center</b><br/>(Pristine Check)", td_style),
            Paragraph("Click <b>Run Unified Multi-Layer Verification</b> on the generated genuine credential.", td_style),
            Paragraph("<b>VERIFIED</b> (Green). All 5 layers PASS: QR PASS, Signature PASS, Watermark NC &gt; 0.99, Copy Score &lt; 0.07. Latency &lt; 28 ms.", td_style),
            Paragraph("Gap 4 (Sub-50ms unified pipeline latency)", td_style)
        ],
        [
            Paragraph("<b>STEP 3</b>", td_bold),
            Paragraph("<b>⚡ Attack Simulator</b><br/>(Threat Vectors)", td_style),
            Paragraph("<b>3A:</b> Select <i>Print-Scan Channel</i> &rarr; Verify.<br/><b>3B:</b> Select <i>Content Splicing / Forgery</i> &rarr; Verify.", td_style),
            Paragraph("<b>3A:</b> Copy Score &gt; 0.52 &rarr; <b>SUSPICIOUS</b>.<br/><b>3B:</b> Watermark NC drops to 0.48 &rarr; <b>VERIFIED-WITH-WARNING</b>.", td_style),
            Paragraph("Gap 3 (Analog photocopy bypass) & Gap 4 (Tamper localization)", td_style)
        ],
        [
            Paragraph("<b>STEP 4</b>", td_bold),
            Paragraph("<b>🏛️ Web-PKI Registry</b><br/>(Trust Lifecycle)", td_style),
            Paragraph("<b>4A:</b> Click <b>Revoke Key</b> on vit.ac.in &rarr; Re-verify doc.<br/><b>4B:</b> Audit spoof domain <code>vlt.ac.in</code> in inspector.", td_style),
            Paragraph("<b>4A:</b> Key revoked in 17 ms; verification immediately gives <b>INVALID</b>.<br/><b>4B:</b> 88.9% Typosquatting Alert.", td_style),
            Paragraph("Gap 5 (Homoglyph spoofing) & Gap 6 (Instant revocation &lt; 20ms)", td_style)
        ],
        [
            Paragraph("<b>STEP 5</b>", td_bold),
            Paragraph("<b>📊 Ablation & Research</b><br/>(Scientific Proof)", td_style),
            Paragraph("Inspect live ROC curve and 5-stage ablation matrix. Run 5-trial benchmark and view SQLite database audit trail.", td_style),
            Paragraph("Empirical ROC AUC = 0.999. Scheme E achieves 100% threat detection. Live microsecond SQLite log displayed.", td_style),
            Paragraph("Empirical scientific rigor & publication reproducibility", td_style)
        ]
    ]

    t_steps = Table(steps_data, colWidths=[42, 90, 160, 160, 88])
    t_steps.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, card_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_steps)
    story.append(Spacer(1, 10))

    # SECTION 2: MODULE-BY-MODULE DEEP DIVE
    story.append(Paragraph("2. Deep-Dive by Module: Purpose, Security Motivation, & Talking Points", h1_style))

    # Module 1
    story.append(Paragraph("Module 1: 🎓 Document Studio (Issuance & Cryptographic Sealing)", h2_style))
    story.append(Paragraph("<b>• What it does:</b> Takes institutional credential fields, computes canonical SHA-256 digest, generates an Ed25519 elliptic-curve signature (Curve25519), packs metadata into CBOR binary format, compresses with ZLIB, generates a high-density QR code, and embeds an invisible 64-bit watermark matrix into the luminance channel via 2-Level DWT-SVD.", body_style))
    story.append(Paragraph("<b>• Why it is necessary:</b> Standard QR codes lack cryptographic authentication and can be generated by anyone. Plain digital certificates without watermarks can have text modified in Photoshop without altering the QR visual. Combining digital signature + invisible frequency-domain watermark binds the physical visual canvas to the mathematical signature.", body_style))
    story.append(Paragraph("<b>• What to Say (Viva Talking Point):</b> <i>\"In Module 1, we solve the QR payload density problem. An RSA-2048 signature is 256 bytes, making QR codes unreadable on low-cost phone cameras. We use Ed25519, which provides 128-bit post-quantum security with a compact 64-byte signature. With CBOR-ZLIB compression, the entire payload fits into a Level-M QR code of under 290 characters.\"</i>", talk_style))
    story.append(Spacer(1, 6))

    # Module 2
    story.append(Paragraph("Module 2: 🔍 Verification Center (Autonomous Multi-Layer Engine)", h2_style))
    story.append(Paragraph("<b>• What it does:</b> Executes autonomous 5-stage verification: (1) QR Preprocessing & Decoding, (2) Web-PKI Domain Binding, (3) Ed25519 Signature Validation, (4) Canonical Hash Match, (5) DWT-SVD Watermark Extraction ($NC$), (6) Blind Copy Residual Filtering, and (7) Secondary Edge AI layout inference.", body_style))
    story.append(Paragraph("<b>• Why it is necessary:</b> Single-point verification is brittle. If only the QR is checked, photocopies pass. If only the watermark is checked, someone could embed a valid watermark with fake data. Multi-layer defense ensures that every threat vector is independently covered.", body_style))
    story.append(Paragraph("<b>• What to Say (Viva Talking Point):</b> <i>\"Our verification engine is strictly non-blocking and executes in under 28 ms on standard CPU hardware, beating our 50 ms edge budget. On clean documents, the watermark achieves an NC of 0.995 and the copy score stays at 0.067, granting an immediate green VERIFIED verdict.\"</i>", talk_style))
    story.append(Spacer(1, 6))

    # Module 3
    story.append(Paragraph("Module 3: ⚡ Multi-Vector Attack & Distortion Simulator", h2_style))
    story.append(Paragraph("<b>• What it does:</b> Simulates 8 real-world physical and digital distortions: Analog Print-and-Scan (halftoning, downsampling, MTF blur), Heavy JPEG Compression (Q=25), Content Splicing / Forgery (altering recipient name/grade pixels), Perspective Warp (smartphone tilt), Glare & Flashlight, Optical Sensor Noise, Focal Blur, and Skew Rotation.", body_style))
    story.append(Paragraph("<b>• Why it is necessary:</b> Security systems must be proven resilient against adversaries. Testing both photocopies and content tampering proves that the system handles both threat classes distinctly.", body_style))
    story.append(Paragraph("<b>• What to Say (Viva Talking Point):</b> <i>\"When an attacker photocopies a certificate, the QR signature remains valid, but our Component A Laplacian high-frequency residual detects the dot-gain artifacts, pushing the copy score above 0.52 and flagging it as SUSPICIOUS. When an attacker alters the student's name, our DWT-SVD watermark correlation collapses from 0.995 to 0.48, triggering an automatic tamper warning.\"</i>", talk_style))
    story.append(Spacer(1, 6))

    story.append(PageBreak())

    # Module 4
    story.append(Paragraph("Module 4: 🏛️ Web-PKI Trust Registry & Homoglyph Inspector", h2_style))
    story.append(Paragraph("<b>• What it does:</b> Maintains an authoritative institutional registry mapping university domains to active public keys and revocation statuses. Evaluates arbitrary domain strings using Damerau-Levenshtein distance to detect confusable Unicode characters and typosquatting.", body_style))
    story.append(Paragraph("<b>• Why it is necessary:</b> (1) <i>Revocation Flaw:</i> In static QR systems, if an administrator's private key is leaked, forged certificates can circulate indefinitely. (2) <i>Domain Spoofing:</i> Fraudsters create fake websites like <code>v1t.ac.in</code> or <code>vlt.ac.in</code> to trick verification portals into trusting rogue public keys.", body_style))
    story.append(Paragraph("<b>• What to Say (Viva Talking Point):</b> <i>\"Our Web-PKI solves Research Gap 6 with sub-20ms instant key revocation. When a key is revoked, every document signed by that key is rejected immediately worldwide without server document storage. Furthermore, our semantic inspector catches deceptive domains like 'vlt.ac.in' with an 88.9% similarity alert, solving Research Gap 5.\"</i>", talk_style))
    story.append(Spacer(1, 6))

    # Module 5
    story.append(Paragraph("Module 5: 📊 Ablation & Research Lab", h2_style))
    story.append(Paragraph("<b>• What it does:</b> Displays live empirical research benchmarks including the Component A ROC Curve (AUC = 0.999), 5-Stage Ablation Comparison Matrix (Schemes A through E), automated 54-combination multi-condition stress test (across 3 papers, 3 printers, 2 scripts, 3 templates), and live SQLite verification audit trail.", body_style))
    story.append(Paragraph("<b>• Why it is necessary:</b> Demonstrates that this is an academic research contribution rather than a simple college software project. Every metric is computed dynamically from real image arrays and logged to a persistent SQLite database.", body_style))
    story.append(Paragraph("<b>• What to Say (Viva Talking Point):</b> <i>\"In our ablation study, Scheme A (QR-only) achieves only 20% threat detection. Progressive addition of DWT-SVD (Scheme B), Blind Copy Detection (Scheme C), and Web-PKI (Scheme D) culminates in Scheme E achieving 100% detection across all attack vectors while maintaining a mean verification latency of ~22 ms.\"</i>", talk_style))
    story.append(Spacer(1, 10))

    # SECTION 3: VIVA CHEAT SHEET & THRESHOLDS TABLE
    story.append(Paragraph("3. Quantitative Metrics & Viva Cheat Sheet (Quick Memory Reference)", h1_style))
    story.append(Paragraph("Memorize these exact threshold numbers and experimental metrics. Evaluators and technical interviewers will specifically ask for numbers to test whether you understand the underlying mathematics.", body_style))

    cheat_data = [
        [
            Paragraph("<b>Metric / Parameter</b>", th_style),
            Paragraph("<b>Formula / Definition</b>", th_style),
            Paragraph("<b>Genuine Baseline</b>", th_style),
            Paragraph("<b>Attacked / Distorted</b>", th_style),
            Paragraph("<b>Decision Threshold</b>", th_style)
        ],
        [
            Paragraph("<b>Watermark NC</b><br/>(Normalized Correlation)", td_bold),
            Paragraph("$$NC = \\frac{\\sum W \\cdot W^*}{\\sqrt{\\sum W^2 \\sum (W^*)^2}}$$", td_style),
            Paragraph("<b>0.994 &ndash; 0.997</b><br/>(Intact / PASS)", td_style),
            Paragraph("<b>0.37 &ndash; 0.58</b><br/>(Tampered / Degraded)", td_style),
            Paragraph("Threshold: <b>&ge; 0.70</b><br/>(&lt;0.70 &rarr; WARN/FAIL)", td_style)
        ],
        [
            Paragraph("<b>Copy Score</b><br/>(Blind High-Freq Residual)", td_bold),
            Paragraph("$$R = I - G_\\sigma(I)$$<br/>Kurtosis &amp; spectral power", td_style),
            Paragraph("<b>0.065 &ndash; 0.068</b><br/>(Crisp print / PASS)", td_style),
            Paragraph("<b>0.520 &ndash; 0.540</b><br/>(Photocopy / FLAG)", td_style),
            Paragraph("Threshold: <b>&lt; 0.35</b><br/>(&ge;0.35 &rarr; SUSPICIOUS)", td_style)
        ],
        [
            Paragraph("<b>Watermark PSNR</b><br/>(Imperceptibility)", td_bold),
            Paragraph("$$PSNR = 10 \\log_{10}\\left(\\frac{255^2}{MSE}\\right)$$", td_style),
            Paragraph("<b>&gt; 51.9 dB</b><br/>(Industry: &gt;38 dB)", td_style),
            Paragraph("&mdash;", td_style),
            Paragraph("Standard: <b>&gt; 38.0 dB</b><br/>(Zero visual artifact)", td_style)
        ],
        [
            Paragraph("<b>Watermark SSIM</b><br/>(Structural Similarity)", td_bold),
            Paragraph("$$\\text{SSIM}(x,y) = \\frac{(2\\mu_x\\mu_y+c_1)(2\\sigma_{xy}+c_2)}{(\\mu_x^2+\\mu_y^2+c_1)(\\sigma_x^2+\\sigma_y^2+c_2)}$$", td_style),
            Paragraph("<b>0.9973</b><br/>(Near-lossless)", td_style),
            Paragraph("&mdash;", td_style),
            Paragraph("Standard: <b>&gt; 0.95</b>", td_style)
        ],
        [
            Paragraph("<b>Revocation Latency</b><br/>(Web-PKI Trust Check)", td_bold),
            Paragraph("Database write + memory state refresh", td_style),
            Paragraph("<b>4.3 &ndash; 17.2 ms</b>", td_style),
            Paragraph("Rejects immediately", td_style),
            Paragraph("Budget: <b>&lt; 50 ms</b><br/>(Gap 6 solved)", td_style)
        ],
        [
            Paragraph("<b>Pipeline Latency</b><br/>(All 5 Layers)", td_bold),
            Paragraph("QR + PKI + Sig + DWT + Residual + AI", td_style),
            Paragraph("<b>22.5 &ndash; 28.0 ms</b>", td_style),
            Paragraph("&mdash;", td_style),
            Paragraph("Budget: <b>&lt; 50.0 ms</b><br/>(Edge real-time)", td_style)
        ],
        [
            Paragraph("<b>ROC AUC</b><br/>(Component A Copy Model)", td_bold),
            Paragraph("Area under Receiver Operating Characteristic", td_style),
            Paragraph("<b>0.9988 &ndash; 0.9990</b>", td_style),
            Paragraph("&mdash;", td_style),
            Paragraph("Near-perfect classification separation", td_style)
        ]
    ]

    t_cheat = Table(cheat_data, colWidths=[95, 125, 95, 95, 130])
    t_cheat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, card_bg]),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_cheat)
    story.append(Spacer(1, 10))

    # SECTION 4: TOUGH VIVA QUESTIONS
    story.append(Paragraph("4. Anticipated Tough Viva Questions & Model Answers", h1_style))

    qas = [
        ("Q1: Why did you choose DWT-SVD instead of spatial-domain LSB watermarking?",
         "Spatial LSB is extremely fragile and easily destroyed by JPEG compression, low-resolution rescanning, or camera noise. In DWT-SVD, the image is decomposed into wavelet frequency sub-bands (LL, LH, HL, HH). Singular values of the HL band represent algebraic energy that is invariant to minor geometric and compression distortions, yet highly sensitive to local pixel modifications."),
        ("Q2: How does Component A detect a photocopy if the verifier does not have the original certificate?",
         "It is a blind copy detection algorithm. First-generation laser prints exhibit crisp edge gradients and high Laplacian kurtosis. When a document is scanned and reprinted, the modulation transfer function (MTF) of the scanner and printer halftoning screen destroys high spatial frequencies. We extract a high-pass residual image R = I - G(I) and analyze frequency energy and noise distributions, which reliably distinguish copies without requiring an original image."),
        ("Q3: Why use Ed25519 over RSA-2048 or ECDSA?",
         "RSA-2048 signatures are 256 bytes long, which forces QR codes to be dense and difficult to scan on smartphone cameras. Ed25519 uses Curve25519 to produce a compact 64-byte signature with equivalent 128-bit security. It signs and verifies in microseconds, is deterministic (immune to weak RNG vulnerabilities), and provides resistance to side-channel attacks."),
        ("Q4: How do you prove this system is dynamic and not hardcoded?",
         "First, when any student name or ID is changed in the Studio, a unique SHA-256 hash and unique Ed25519 signature are generated. Second, revoking the key in SQLite causes verifications to fail dynamically. Third, all watermark NC scores are floating-point SVD correlations that vary dynamically with pixel content (e.g. 0.9957 vs 0.4898). Fourth, every transaction is logged with microsecond timestamps into SQLite."),
        ("Q5: What are the 6 Research Gaps addressed by your work?",
         "Gap 1: QR payload capacity & barcode density limits (solved via CBOR-ZLIB). Gap 2: Fragility vs. imperceptibility tradeoff in watermarks (solved via DWT-SVD with PSNR > 51 dB). Gap 3: Analog photocopy/print-scan bypass (solved via blind residual copy detection). Gap 4: Absence of unified multi-layer verification under 50ms latency (solved via our 25ms engine). Gap 5: Institutional domain spoofing & homoglyph attacks (solved via Levenshtein inspector). Gap 6: Lack of real-time cryptographic revocation (solved via sub-20ms Web-PKI).")
    ]

    for q, a in qas:
        story.append(Paragraph(f"<b>{q}</b>", bold_bullet_style))
        story.append(Paragraph(f"{a}", bullet_style))
        story.append(Spacer(1, 3))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
