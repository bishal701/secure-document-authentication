"""
Comprehensive Watermarking and Authentication Benchmark Evaluator.
Computes PSNR, SSIM, NC, BER, WESR, QDSR, ADR, FAR, FRR, Precision, Recall, F1, Balanced Accuracy,
and execution latencies with exact mathematical definitions.
"""

import time
import numpy as np
import cv2
from skimage.metrics import structural_similarity as compute_ssim
from typing import Dict, Any, List, Optional, Tuple

class BenchmarkEvaluator:
    """
    Implements standardized evaluation metrics for digital watermarking,
    optical barcode scannability, and classification accuracy.
    """

    @staticmethod
    def calculate_psnr(orig: np.ndarray, mod: np.ndarray) -> float:
        """
        Peak Signal-to-Noise Ratio (PSNR) in decibels (dB).
        PSNR = 10 * log10( 255^2 / MSE )
        """
        if orig.shape != mod.shape:
            mod = cv2.resize(mod, (orig.shape[1], orig.shape[0]))
        mse = float(np.mean((orig.astype(np.float64) - mod.astype(np.float64)) ** 2))
        if mse == 0.0:
            return 100.0
        return float(10.0 * np.log10((255.0 ** 2) / mse))

    @staticmethod
    def calculate_ssim(orig: np.ndarray, mod: np.ndarray) -> float:
        """
        Structural Similarity Index Measure (SSIM) in [-1, 1].
        """
        if orig.shape != mod.shape:
            mod = cv2.resize(mod, (orig.shape[1], orig.shape[0]))
        if len(orig.shape) == 3:
            return float(compute_ssim(orig, mod, channel_axis=2, data_range=255))
        return float(compute_ssim(orig, mod, data_range=255))

    @staticmethod
    def calculate_nc(wm_orig: np.ndarray, wm_ext: np.ndarray) -> float:
        """
        Normalized Correlation (NC / NCC) in [-1, 1].
        NC = sum(w * w') / ( sqrt(sum(w^2)) * sqrt(sum(w'^2)) )
        """
        w1 = wm_orig.astype(np.float64).flatten()
        w2 = wm_ext.astype(np.float64).flatten()
        norm1 = np.linalg.norm(w1)
        norm2 = np.linalg.norm(w2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(w1, w2) / (norm1 * norm2))

    @staticmethod
    def calculate_ber(wm_orig: np.ndarray, wm_ext: np.ndarray) -> float:
        """
        Watermark Bit Error Rate (BER) in percentage [0, 100]%.
        BER = (sum(b != b') / N) * 100%
        """
        b1 = (wm_orig.flatten() > 0.5).astype(np.int32)
        b2 = (wm_ext.flatten() > 0.5).astype(np.int32)
        if len(b1) != len(b2):
            min_len = min(len(b1), len(b2))
            b1, b2 = b1[:min_len], b2[:min_len]
        errors = int(np.sum(b1 != b2))
        total = len(b1)
        if total == 0:
            return 0.0
        return float((errors / total) * 100.0)

    @staticmethod
    def calculate_wesr(
        nc_list: List[float],
        ber_list: List[float],
        nc_threshold: float = 0.75,
        ber_threshold: float = 20.0
    ) -> float:
        """
        Watermark Extraction Success Rate (WESR) in percentage [0, 100]%.
        WESR = (Count of samples where NC >= tau_nc and BER <= tau_ber) / Total Samples
        """
        if not nc_list:
            return 0.0
        successes = sum(
            1 for nc, ber in zip(nc_list, ber_list)
            if nc >= nc_threshold and ber <= ber_threshold
        )
        return float((successes / len(nc_list)) * 100.0)

    @staticmethod
    def calculate_qdsr(decode_success_list: List[bool]) -> float:
        """
        Standard QR Decoding Success Rate (QDSR) in percentage [0, 100]%.
        QDSR = (Decoded QR Count / Total QR Count) * 100%
        """
        if not decode_success_list:
            return 0.0
        return float((sum(1 for s in decode_success_list if s) / len(decode_success_list)) * 100.0)

    @staticmethod
    def calculate_classification_metrics(
        y_true: np.ndarray,
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """
        Computes binary classification metrics:
        y_true, y_pred in {0, 1} where 1 = Attack / Fraud / Tampered, 0 = Genuine / Authentic.
        Metrics:
            - True Positives (TP): Attacks correctly identified as attacks (y_true=1, y_pred=1)
            - False Positives (FP): Genuine samples incorrectly flagged as attacks (y_true=0, y_pred=1)
            - True Negatives (TN): Genuine samples correctly identified as genuine (y_true=0, y_pred=0)
            - False Negatives (FN): Attacks incorrectly accepted as genuine (y_true=1, y_pred=0)
            - Precision (P) = TP / (TP + FP)
            - Recall (R) / Attack Detection Rate (ADR) = TP / (TP + FN)
            - Specificity = TN / (TN + FP)
            - F1-Score = 2 * P * R / (P + R)
            - False Acceptance Rate (FAR) = FN / (FN + TP): Attacks incorrectly accepted as genuine
            - False Rejection Rate (FRR) = FP / (FP + TN): Genuine samples incorrectly rejected as attacks
            - Balanced Accuracy = (Recall + Specificity) / 2
        """
        y_t = np.array(y_true).astype(int)
        y_p = np.array(y_pred).astype(int)

        tp = int(np.sum((y_t == 1) & (y_p == 1)))
        fp = int(np.sum((y_t == 0) & (y_p == 1)))
        tn = int(np.sum((y_t == 0) & (y_p == 0)))
        fn = int(np.sum((y_t == 1) & (y_p == 0)))

        precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        # Corrected definitions:
        # FAR: Attacks (y_true=1) accepted as genuine (y_pred=0) -> FN / Total Attacks (TP + FN)
        far = float(fn / (fn + tp)) * 100.0 if (fn + tp) > 0 else 0.0
        # FRR: Genuine (y_true=0) rejected as attacks (y_pred=1) -> FP / Total Genuine (TN + FP)
        frr = float(fp / (fp + tn)) * 100.0 if (fp + tn) > 0 else 0.0
        balanced_acc = float((recall + specificity) / 2.0)

        return {
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn,
            "total_samples": len(y_t),
            "precision": precision,
            "recall": recall,
            "attack_detection_rate": recall * 100.0,
            "specificity": specificity,
            "f1_score": f1,
            "far_percent": far,
            "frr_percent": frr,
            "balanced_accuracy": balanced_acc
        }
