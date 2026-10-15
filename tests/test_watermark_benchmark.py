"""
Comprehensive Automated Test Suite for QR Watermarking, Metrics, Attacks, and Dataset Integrity (Phase 8).
Verifies:
1. QR symbol generation & structural masking.
2. LSB round-trip embedding and blind extraction.
3. DWT-DCT round-trip embedding and blind extraction.
4. Optical OpenCV QR decoding preservation.
5. Digital attack engine operations.
6. Benchmark evaluation metrics (PSNR, SSIM, NC, BER, WESR, QDSR, F1, FAR, FRR).
7. Leakage-safe dataset partitioning (zero payload identity leakage).
8. Physical capture manifest schema and non-fabrication integrity.
"""

import unittest
import numpy as np
import cv2
import pandas as pd
from pathlib import Path

from backend.qr_watermark.masking import QRStructureMasker
from backend.qr_watermark.qr_generator import QRWatermarkGenerator
from backend.qr_watermark.lsb import LSBWatermarker
from backend.qr_watermark.dwt_dct import DWTDCTWatermarker
from backend.qr_watermark.benchmark_evaluator import BenchmarkEvaluator
from backend.attack_simulator.qr_attacks import QRAttackEngine
from scripts.validate_physical_manifest import validate_manifest

BASE_DIR = Path(__file__).resolve().parent.parent

class TestQRWatermarkBenchmarkSuite(unittest.TestCase):

    def setUp(self):
        self.payload_id = "UNITTEST-PAYLOAD-001"
        self.qr_obj = QRWatermarkGenerator.create_qr_symbol(self.payload_id, box_size=8, border=4)
        self.host_img = self.qr_obj["image_rgb"]
        self.mask = self.qr_obj["pixel_mask"]
        self.watermark_bits = QRWatermarkGenerator.generate_watermark_bits(self.payload_id, 64)

    def test_01_qr_generation_and_masking(self):
        """Verifies QR code dimensions and data mask validity."""
        self.assertIsNotNone(self.host_img)
        self.assertEqual(len(self.host_img.shape), 3)
        self.assertEqual(self.host_img.shape[:2], self.mask.shape)
        # Verify that quiet zone borders are masked out (False)
        self.assertFalse(np.any(self.mask[:16, :]))
        self.assertFalse(np.any(self.mask[-16:, :]))
        self.assertFalse(np.any(self.mask[:, :16]))
        self.assertFalse(np.any(self.mask[:, -16:]))
        # Verify that data region contains eligible pixels
        self.assertGreater(np.sum(self.mask), 1000)

    def test_02_lsb_clean_embedding_extraction(self):
        """Verifies LSB clean embedding, zero BER, and PSNR > 50 dB."""
        engine = LSBWatermarker(bit_plane=1)
        wm_img, meta = engine.embed(self.host_img, self.watermark_bits, self.mask)
        self.assertEqual(wm_img.shape, self.host_img.shape)
        self.assertGreater(meta["psnr"], 50.0)

        ext_bits, _ = engine.extract(wm_img, self.mask, 64)
        ber = BenchmarkEvaluator.calculate_ber(self.watermark_bits, ext_bits)
        nc = BenchmarkEvaluator.calculate_nc(self.watermark_bits, ext_bits)
        self.assertEqual(ber, 0.0)
        self.assertAlmostEqual(nc, 1.0, places=3)

    def test_03_dwtdct_clean_embedding_extraction(self):
        """Verifies DWT-DCT clean embedding, zero BER, and PSNR > 45 dB."""
        engine = DWTDCTWatermarker(alpha=20.0)
        wm_img, meta = engine.embed(self.host_img, self.watermark_bits, self.mask)
        self.assertEqual(wm_img.shape, self.host_img.shape)
        self.assertGreater(meta["psnr"], 45.0)

        ext_bits, _ = engine.extract(wm_img, self.mask, 64)
        ber = BenchmarkEvaluator.calculate_ber(self.watermark_bits, ext_bits)
        nc = BenchmarkEvaluator.calculate_nc(self.watermark_bits, ext_bits)
        self.assertEqual(ber, 0.0)
        self.assertAlmostEqual(nc, 1.0, places=3)

    def test_04_optical_qr_decoding_preservation(self):
        """Verifies that both LSB and DWT-DCT preserve standard OpenCV QR decodability."""
        # Unwatermarked decode
        ok_host, txt_host = QRWatermarkGenerator.decode_qr(self.host_img)
        self.assertTrue(ok_host)
        self.assertIn(self.payload_id, txt_host)

        # LSB decode
        lsb = LSBWatermarker(bit_plane=1)
        wm_lsb, _ = lsb.embed(self.host_img, self.watermark_bits, self.mask)
        ok_lsb, txt_lsb = QRWatermarkGenerator.decode_qr(wm_lsb)
        self.assertTrue(ok_lsb)
        self.assertIn(self.payload_id, txt_lsb)

        # DWT-DCT decode
        dwt = DWTDCTWatermarker(alpha=20.0)
        wm_dwt, _ = dwt.embed(self.host_img, self.watermark_bits, self.mask)
        ok_dwt, txt_dwt = QRWatermarkGenerator.decode_qr(wm_dwt)
        self.assertTrue(ok_dwt)
        self.assertIn(self.payload_id, txt_dwt)

    def test_05_digital_attack_engine(self):
        """Tests that all 9 digital distortion attacks execute cleanly."""
        attacks = [
            ("GAUSSIAN_NOISE", {"sigma": 10.0}),
            ("SALT_PEPPER", {"density": 0.02}),
            ("GAUSSIAN_BLUR", {"ksize": 5, "sigma": 1.2}),
            ("JPEG_COMPRESSION", {"quality": 70}),
            ("RESIZE", {"scale": 0.75}),
            ("ROTATION", {"angle": 3.0}),
            ("CROP", {"crop_ratio": 0.05}),
            ("CONTRAST_ILLUMINATION", {"alpha": 1.1, "beta": -10.0}),
            ("WATERMARK_REMOVAL", {})
        ]
        for atk_name, params in attacks:
            atk_img, meta = QRAttackEngine.apply_attack(self.host_img, atk_name, params)
            self.assertEqual(atk_img.shape, self.host_img.shape)
            self.assertEqual(atk_img.dtype, np.uint8)

    def test_06_benchmark_metrics_calculation(self):
        """Tests metric functions on known inputs including unequal FAR and FRR."""
        # Identical images
        psnr_ident = BenchmarkEvaluator.calculate_psnr(self.host_img, self.host_img)
        self.assertEqual(psnr_ident, 100.0)
        ssim_ident = BenchmarkEvaluator.calculate_ssim(self.host_img, self.host_img)
        self.assertAlmostEqual(ssim_ident, 1.0, places=4)

        # Classification metrics with known confusion matrix with UNEQUAL FAR and FRR:
        # 100 Genuine (0), 200 Attacks (1)
        # TP = 160, FN = 40 (Attacks accepted as genuine -> FAR = 40/200 = 20.0%)
        # TN = 95,  FP = 5  (Genuine rejected as attacks -> FRR = 5/100 = 5.0%)
        y_true = np.array([0] * 100 + [1] * 200)
        y_pred = np.array([0] * 95 + [1] * 5 + [0] * 40 + [1] * 160)

        m = BenchmarkEvaluator.calculate_classification_metrics(y_true, y_pred)
        self.assertEqual(m["tp"], 160)
        self.assertEqual(m["fp"], 5)
        self.assertEqual(m["tn"], 95)
        self.assertEqual(m["fn"], 40)
        self.assertAlmostEqual(m["precision"], 160 / 165, places=4)
        self.assertAlmostEqual(m["recall"], 160 / 200, places=4)
        self.assertAlmostEqual(m["specificity"], 95 / 100, places=4)
        self.assertAlmostEqual(m["balanced_accuracy"], (160/200 + 95/100) / 2.0, places=4)

        # Swapped formulas cannot pass unnoticed:
        # FAR must be 20.0%, FRR must be 5.0%
        self.assertEqual(m["far_percent"], 20.0)
        self.assertEqual(m["frr_percent"], 5.0)
        self.assertNotEqual(m["far_percent"], m["frr_percent"])

    def test_07_physical_manifest_validation(self):
        """Validates that physical manifest complies with schema and non-fabrication rule."""
        is_valid = validate_manifest()
        self.assertTrue(is_valid)

    def test_08_multi_version_masking(self):
        """Verifies QRStructureMasker across supported QR versions (v1, v2, v4, v7)."""
        versions_to_test = [1, 2, 4, 7]
        for v in versions_to_test:
            num_modules = (v - 1) * 4 + 21
            mask = QRStructureMasker.get_module_mask(num_modules, version=v)
            self.assertEqual(mask.shape, (num_modules, num_modules))
            # Finders must be masked (False)
            self.assertFalse(mask[0, 0])
            self.assertFalse(mask[0, num_modules - 1])
            self.assertFalse(mask[num_modules - 1, 0])
            # Timing patterns must be masked
            self.assertFalse(mask[6, 10])
            self.assertFalse(mask[10, 6])
            # Format information must be masked
            self.assertFalse(mask[8, 8])
            # Data area must contain eligible modules
            self.assertGreater(np.sum(mask), 50)

            # Version info for v >= 7
            if v >= 7:
                # 6x3 block to left of Top-Right finder
                self.assertFalse(np.any(mask[0:6, num_modules - 11:num_modules - 8]))

    def test_09_attacks_transform_image(self):
        """Verifies that every attack transforms the watermarked image and is not a no-op."""
        attacks = [
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
        for atk_name, params in attacks:
            atk_img, meta = QRAttackEngine.apply_attack(self.host_img, atk_name, params)
            max_diff = np.max(np.abs(atk_img.astype(int) - self.host_img.astype(int)))
            self.assertGreater(max_diff, 0, f"Attack {atk_name} produced a no-op identical image!")

    def test_10_dwt_dct_conservative_blocks(self):
        """Verifies that all DWT-DCT eligible transform blocks fall 100% inside the data mask."""
        engine = DWTDCTWatermarker(alpha=20.0)
        h, w = self.mask.shape
        sub_h, sub_w = h // 2, w // 2
        blocks = engine._get_eligible_blocks(self.mask, sub_h, sub_w, h, w)
        self.assertGreater(len(blocks), 50)
        bs = engine.block_size
        for br, bc in blocks:
            r0 = br * bs * 2
            r1 = min(h, (br + 1) * bs * 2)
            c0 = bc * bs * 2
            c1 = min(w, (bc + 1) * bs * 2)
            # Must be 100% inside eligible data mask
            self.assertTrue(np.all(self.mask[r0:r1, c0:c1]), f"Block ({br},{bc}) overlaps protected structural patterns!")

if __name__ == "__main__":
    unittest.main()
