"""
Comprehensive Attack Simulator for 2D QR Barcode Watermarks.
Implements Gaussian noise, Salt-and-Pepper noise, Gaussian blur, JPEG compression,
resizing, rotation/deskew, cropping, contrast/illumination, QR replacement, and watermark removal.
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional

class QRAttackEngine:
    """
    Standardized attack generator with configurable severity parameters.
    """

    @staticmethod
    def apply_gaussian_noise(image: np.ndarray, sigma: float = 15.0) -> np.ndarray:
        """Adds zero-mean additive Gaussian noise."""
        noise = np.random.normal(0, sigma, image.shape)
        noisy = np.clip(image.astype(np.float64) + noise, 0, 255).astype(np.uint8)
        return noisy

    @staticmethod
    def apply_salt_pepper(image: np.ndarray, density: float = 0.03) -> np.ndarray:
        """Adds impulse Salt-and-Pepper noise."""
        noisy = image.copy()
        num_pixels = int(density * image.shape[0] * image.shape[1])
        # Salt (255)
        r_salt = np.random.randint(0, image.shape[0], num_pixels // 2)
        c_salt = np.random.randint(0, image.shape[1], num_pixels // 2)
        noisy[r_salt, c_salt] = 255
        # Pepper (0)
        r_pep = np.random.randint(0, image.shape[0], num_pixels // 2)
        c_pep = np.random.randint(0, image.shape[1], num_pixels // 2)
        noisy[r_pep, c_pep] = 0
        return noisy

    @staticmethod
    def apply_gaussian_blur(image: np.ndarray, ksize: int = 5, sigma: float = 1.2) -> np.ndarray:
        """Applies spatial Gaussian low-pass filtering."""
        if ksize % 2 == 0:
            ksize += 1
        return cv2.GaussianBlur(image, (ksize, ksize), sigma)

    @staticmethod
    def apply_jpeg_compression(image: np.ndarray, quality: int = 70) -> np.ndarray:
        """Simulates lossy DCT quantization via JPEG encoding."""
        q = max(10, min(100, int(quality)))
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), q]
        _, enc = cv2.imencode(".jpg", image, encode_param)
        return cv2.imdecode(enc, cv2.IMREAD_COLOR)

    @staticmethod
    def apply_resizing(image: np.ndarray, scale: float = 0.75) -> np.ndarray:
        """Downscales then upscales back using bicubic interpolation."""
        h, w = image.shape[:2]
        down_h, down_w = max(16, int(h * scale)), max(16, int(w * scale))
        down = cv2.resize(image, (down_w, down_h), interpolation=cv2.INTER_AREA)
        up = cv2.resize(down, (w, h), interpolation=cv2.INTER_CUBIC)
        return up

    @staticmethod
    def apply_rotation_and_deskew(image: np.ndarray, angle: float = 3.0) -> np.ndarray:
        """
        Rotates image by angle degrees and applies inverse deskew correction,
        simulating perspective alignment interpolation loss.
        """
        h, w = image.shape[:2]
        center = (w / 2.0, h / 2.0)
        M_rot = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M_rot, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        # Deskew back
        M_deskew = cv2.getRotationMatrix2D(center, -angle, 1.0)
        deskewed = cv2.warpAffine(rotated, M_deskew, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        return deskewed

    @staticmethod
    def apply_crop(image: np.ndarray, crop_ratio: float = 0.15) -> np.ndarray:
        """
        Crops outer border by crop_ratio (default 15%, penetrating past the quiet zone
        into active data modules) and pads back with neutral white.
        """
        h, w = image.shape[:2]
        pad_y = int(h * crop_ratio)
        pad_x = int(w * crop_ratio)
        cropped = image[pad_y:h-pad_y, pad_x:w-pad_x]
        padded = cv2.copyMakeBorder(
            cropped, pad_y, h - (h - pad_y), pad_x, w - (w - pad_x),
            cv2.BORDER_CONSTANT, value=[255, 255, 255]
        )
        return cv2.resize(padded, (w, h))

    @staticmethod
    def apply_contrast_illumination(
        image: np.ndarray,
        alpha: float = 1.15,
        beta: float = -15.0
    ) -> np.ndarray:
        """Modifies contrast (alpha) and brightness/illumination (beta)."""
        mod = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        return mod

    @staticmethod
    def apply_qr_replacement(
        image: np.ndarray,
        forged_qr_image: np.ndarray
    ) -> np.ndarray:
        """
        Simulates QR replacement / splicing attack: substitutes genuine QR symbol
        with an unauthorized forged QR code.
        """
        h, w = image.shape[:2]
        forged_resized = cv2.resize(forged_qr_image, (w, h))
        return forged_resized

    @staticmethod
    def apply_watermark_removal(image: np.ndarray) -> np.ndarray:
        """
        Simulates an active watermark-removal / scrubbing attack:
        Applies bit-plane scrubbing (clearing the lower 2 bit-planes and adding dithering noise)
        combined with spatial median filtering to strip both spatial LSB and transform-domain watermarks.
        """
        scrubbed = (image & 0xFC).astype(np.float64)
        rng = np.random.RandomState(42)
        noise = rng.randint(0, 4, image.shape).astype(np.float64)
        scrubbed = np.clip(scrubbed + noise, 0, 255).astype(np.uint8)
        filtered = cv2.medianBlur(scrubbed, 5)
        return filtered

    @classmethod
    def apply_attack(
        cls,
        image: np.ndarray,
        attack_type: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Applies requested attack and returns the attacked image with metadata.
        """
        params = params or {}
        atk = attack_type.upper()

        if atk in ["CLEAN", "NONE"]:
            return image.copy(), {"attack": "NONE"}

        elif atk == "GAUSSIAN_NOISE":
            sigma = params.get("sigma", 15.0)
            return cls.apply_gaussian_noise(image, sigma=sigma), {"attack": atk, "sigma": sigma}

        elif atk == "SALT_PEPPER":
            density = params.get("density", 0.03)
            return cls.apply_salt_pepper(image, density=density), {"attack": atk, "density": density}

        elif atk == "GAUSSIAN_BLUR":
            ksize = params.get("ksize", 5)
            sigma = params.get("sigma", 1.2)
            return cls.apply_gaussian_blur(image, ksize=ksize, sigma=sigma), {"attack": atk, "ksize": ksize, "sigma": sigma}

        elif atk == "JPEG_COMPRESSION":
            quality = params.get("quality", 70)
            return cls.apply_jpeg_compression(image, quality=quality), {"attack": atk, "quality": quality}

        elif atk == "RESIZE":
            scale = params.get("scale", 0.75)
            return cls.apply_resizing(image, scale=scale), {"attack": atk, "scale": scale}

        elif atk == "ROTATION":
            angle = params.get("angle", 3.0)
            return cls.apply_rotation_and_deskew(image, angle=angle), {"attack": atk, "angle": angle}

        elif atk == "CROP":
            crop_ratio = params.get("crop_ratio", 0.15)
            return cls.apply_crop(image, crop_ratio=crop_ratio), {"attack": atk, "crop_ratio": crop_ratio}

        elif atk == "CONTRAST_ILLUMINATION":
            alpha = params.get("alpha", 1.15)
            beta = params.get("beta", -15.0)
            return cls.apply_contrast_illumination(image, alpha=alpha, beta=beta), {"attack": atk, "alpha": alpha, "beta": beta}

        elif atk == "WATERMARK_REMOVAL":
            return cls.apply_watermark_removal(image), {"attack": atk}

        else:
            raise ValueError(f"Unknown attack type: {attack_type}")
