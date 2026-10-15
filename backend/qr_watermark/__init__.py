"""
QR-Symbol Watermarking and Benchmarking Package.
Supports spatial-domain LSB, transform-domain DWT-DCT, QR structural masking,
attack simulation, and comprehensive evaluation metrics.
"""

from backend.qr_watermark.masking import QRStructureMasker
from backend.qr_watermark.qr_generator import QRWatermarkGenerator
from backend.qr_watermark.lsb import LSBWatermarker
from backend.qr_watermark.dwt_dct import DWTDCTWatermarker
from backend.qr_watermark.benchmark_evaluator import BenchmarkEvaluator

__all__ = [
    "QRStructureMasker",
    "QRWatermarkGenerator",
    "LSBWatermarker",
    "DWTDCTWatermarker",
    "BenchmarkEvaluator"
]
