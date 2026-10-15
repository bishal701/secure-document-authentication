"""
Spatial-Domain Least Significant Bit (LSB) Watermarking Engine.
Embeds pseudorandom watermark payloads into the luminance channel of eligible
data modules with configurable bit planes and repetition redundancy.
"""

import cv2
import numpy as np
from typing import Tuple, Dict, Any, Optional
from backend.watermark.metrics import WatermarkMetrics

class LSBWatermarker:
    """
    Spatial-domain LSB watermarker with repetition coding and structural masking.
    Supports bit-plane depths k in {1, 2, 3}.
    """

    def __init__(self, bit_plane: int = 1, redundancy: bool = True):
        """
        Args:
            bit_plane: Number of LSB planes to use (1 = LSB0, 2 = LSB1, etc.)
            redundancy: If True, spreads each watermark bit across multiple pixels via repetition.
        """
        self.bit_plane = max(1, min(3, bit_plane))
        self.bit_index = self.bit_plane - 1
        self.redundancy = redundancy

    def embed(
        self,
        image_rgb: np.ndarray,
        watermark_bits: np.ndarray,
        pixel_mask: np.ndarray
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Embeds watermark_bits into the luminance channel of pixels where pixel_mask is True.
        Returns:
            watermarked_rgb: np.ndarray (uint8)
            metadata: dictionary of embedding statistics
        """
        h, w = image_rgb.shape[:2]
        ycrcb = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2YCrCb)
        Y = ycrcb[:, :, 0].copy()

        eligible_indices = np.where(pixel_mask)
        total_eligible = len(eligible_indices[0])
        num_bits = len(watermark_bits)

        if total_eligible == 0:
            raise ValueError("Pixel mask contains 0 eligible data modules for embedding.")

        # Determine repetition count
        rep = total_eligible // num_bits if self.redundancy else 1
        used_pixels = rep * num_bits

        # Map bits to pixels
        bit_stream = np.repeat(watermark_bits, rep) if self.redundancy else watermark_bits
        if len(bit_stream) < used_pixels:
            bit_stream = np.pad(bit_stream, (0, used_pixels - len(bit_stream)), mode="wrap")

        # Embed into bit plane
        mask_clear = ~(1 << self.bit_index) & 0xFF
        bit_val = (bit_stream[:used_pixels].astype(np.uint8) << self.bit_index)

        coords_r = eligible_indices[0][:used_pixels]
        coords_c = eligible_indices[1][:used_pixels]

        Y[coords_r, coords_c] = (Y[coords_r, coords_c] & mask_clear) | bit_val

        ycrcb[:, :, 0] = Y
        watermarked_rgb = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)

        psnr = WatermarkMetrics.calculate_psnr(image_rgb, watermarked_rgb)
        ssim = WatermarkMetrics.calculate_ssim(image_rgb, watermarked_rgb)

        meta = {
            "method": "LSB",
            "bit_plane": self.bit_plane,
            "num_bits": num_bits,
            "rep_factor": rep,
            "used_pixels": used_pixels,
            "psnr": float(psnr),
            "ssim": float(ssim)
        }
        return watermarked_rgb, meta

    def extract(
        self,
        watermarked_rgb: np.ndarray,
        pixel_mask: np.ndarray,
        num_bits: int
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Blindly extracts watermark_bits from the luminance channel.
        Applies majority voting across repeated pixels.
        Returns:
            extracted_bits: np.ndarray (shape (num_bits,), int32 {0, 1})
            meta: extraction diagnostic statistics
        """
        ycrcb = cv2.cvtColor(watermarked_rgb, cv2.COLOR_RGB2YCrCb)
        Y = ycrcb[:, :, 0]

        eligible_indices = np.where(pixel_mask)
        total_eligible = len(eligible_indices[0])

        rep = total_eligible // num_bits if self.redundancy else 1
        used_pixels = rep * num_bits

        coords_r = eligible_indices[0][:used_pixels]
        coords_c = eligible_indices[1][:used_pixels]

        extracted_raw_bits = (Y[coords_r, coords_c] >> self.bit_index) & 1

        if self.redundancy and rep > 1:
            reshaped = extracted_raw_bits[:used_pixels].reshape((num_bits, rep))
            # Majority voting
            extracted_bits = (np.mean(reshaped, axis=1) >= 0.5).astype(np.int32)
        else:
            extracted_bits = extracted_raw_bits[:num_bits].astype(np.int32)

        return extracted_bits, {"extracted_count": len(extracted_bits), "rep_factor": rep}
