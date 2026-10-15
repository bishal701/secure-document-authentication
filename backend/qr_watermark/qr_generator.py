"""
QR Code Generation, Payload Management, and Optical Decoding Module.
Generates reproducible ISO/IEC 18004 QR codes with non-sensitive unique payload IDs
and provides robust OpenCV-based decoding with adaptive threshold fallback.
"""

import hmac
import hashlib
import qrcode
import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional
from backend.qr_watermark.masking import QRStructureMasker

DEFAULT_HMAC_KEY = b"SDA-Watermark-Secret-Key-2026-VIT"

class QRWatermarkGenerator:
    """
    Manages QR symbol rendering, deterministic watermark bitstream synthesis,
    and standard optical decoding.
    """

    @staticmethod
    def generate_watermark_bits(
        payload_id: str,
        num_bits: int,
        secret_key: bytes = DEFAULT_HMAC_KEY
    ) -> np.ndarray:
        """
        Synthesizes a reproducible, cryptographically pseudorandom binary watermark
        bitstream derived via HMAC-SHA256 from the payload ID and secret key.
        Returns:
            np.ndarray of shape (num_bits,), values in {0, 1} (int32).
        """
        # Derive 32-byte seed from HMAC-SHA256
        h = hmac.new(secret_key, payload_id.encode("utf-8"), hashlib.sha256).digest()
        seed_int = int.from_bytes(h[:8], byteorder="big") % (2**32 - 1)
        rng = np.random.RandomState(seed_int)
        bits = rng.randint(0, 2, size=num_bits).astype(np.int32)
        return bits

    @staticmethod
    def create_qr_symbol(
        payload_id: str,
        version: int = 4,
        box_size: int = 8,
        border: int = 4,
        error_correction: int = qrcode.constants.ERROR_CORRECT_M
    ) -> Dict[str, Any]:
        """
        Creates an ISO/IEC 18004 QR code containing payload_id.
        Returns image, geometry metadata, and the structural data mask.
        """
        qr = qrcode.QRCode(
            version=version,
            error_correction=error_correction,
            box_size=box_size,
            border=border
        )
        qr.add_data(f"SDA1:{payload_id}")
        qr.make(fit=True)

        actual_version = qr.version
        num_modules = (actual_version - 1) * 4 + 21

        pil_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        img_rgb = np.array(pil_img, dtype=np.uint8)

        # Generate pixel safety mask (True = safe data modules, False = quiet zone/finders/timing/format)
        pixel_mask = QRStructureMasker.get_pixel_mask(
            image_shape=img_rgb.shape[:2],
            num_modules=num_modules,
            border_modules=border,
            version=actual_version
        )

        return {
            "image_rgb": img_rgb,
            "version": actual_version,
            "num_modules": num_modules,
            "box_size": box_size,
            "border": border,
            "pixel_mask": pixel_mask,
            "payload": f"SDA1:{payload_id}",
            "payload_id": payload_id
        }

    @staticmethod
    def decode_qr(image_rgb: np.ndarray) -> Tuple[bool, str]:
        """
        Attempts standard optical QR decoding using OpenCV QRCodeDetector.
        Includes grayscale and adaptive histogram equalization fallbacks.
        """
        detector = cv2.QRCodeDetector()

        # 1. Direct color decode
        text, pts, _ = detector.detectAndDecode(image_rgb)
        if text:
            return True, text

        # 2. Grayscale decode
        if len(image_rgb.shape) == 3:
            gray = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2GRAY)
        else:
            gray = image_rgb

        text, pts, _ = detector.detectAndDecode(gray)
        if text:
            return True, text

        # 3. Otsu thresholding fallback
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text, pts, _ = detector.detectAndDecode(thresh)
        if text:
            return True, text

        # 4. Adaptive thresholding fallback
        adapt = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 5
        )
        text, pts, _ = detector.detectAndDecode(adapt)
        if text:
            return True, text

        return False, ""
