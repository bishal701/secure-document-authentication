"""
Transform-Domain DWT-DCT Blind Watermarking Engine.
Operates on the QR luminance channel by applying 1-level 2D Haar DWT
followed by block-based 2D-DCT on eligible data module regions.
Embeds pseudorandom watermark bits via differential mid-frequency coefficient modulation.
"""

import cv2
import pywt
import scipy.fft
import numpy as np
from typing import Tuple, Dict, Any, Optional, List
from backend.watermark.metrics import WatermarkMetrics

class DWTDCTWatermarker:
    """
    Transform-domain DWT-DCT blind watermarking engine.
    - Discrete Wavelet Transform (1-level Haar) separates low-frequency spatial structure.
    - Block Discrete Cosine Transform (4x4 or 8x8) exposes mid-frequency spectral coefficients.
    - Differential coefficient modulation embeds binary bits blindly with zero reference image required.
    """

    def __init__(
        self,
        wavelet: str = "haar",
        block_size: int = 4,
        alpha: float = 20.0,
        coeff_pair: Tuple[Tuple[int, int], Tuple[int, int]] = ((1, 2), (2, 1))
    ):
        """
        Args:
            wavelet: Wavelet family (default 'haar')
            block_size: Block dimension inside subband (default 4)
            alpha: Embedding strength parameter (modulation step)
            coeff_pair: Indices of the two mid-frequency DCT coefficients to modulate
        """
        self.wavelet = wavelet
        self.block_size = block_size
        self.alpha = float(alpha)
        self.coeff1, self.coeff2 = coeff_pair

    def embed(
        self,
        image_rgb: np.ndarray,
        watermark_bits: np.ndarray,
        pixel_mask: np.ndarray
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Embeds watermark_bits into the luminance channel using DWT-DCT.
        Only modulates blocks whose center falls within pixel_mask.
        Returns:
            watermarked_rgb: np.ndarray (uint8)
            metadata: dictionary of embedding statistics
        """
        h, w = image_rgb.shape[:2]
        ycrcb = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2YCrCb)
        Y = ycrcb[:, :, 0].astype(np.float64)

        # 1-level 2D DWT
        cA, (cH, cV, cD) = pywt.dwt2(Y, self.wavelet)
        sub_h, sub_w = cA.shape

        bs = self.block_size
        num_blocks_r = sub_h // bs
        num_blocks_c = sub_w // bs

        # Identify eligible blocks using conservative spatial rule
        eligible_blocks = self._get_eligible_blocks(pixel_mask, sub_h, sub_w, h, w)

        if not eligible_blocks:
            raise ValueError("No eligible transform blocks found within data mask.")

        num_bits = len(watermark_bits)
        cA_mod = cA.copy()

        # Embed bits across eligible blocks
        u1, v1 = self.coeff1
        u2, v2 = self.coeff2

        for idx, (br, bc) in enumerate(eligible_blocks):
            blk = cA[br*bs:(br+1)*bs, bc*bs:(bc+1)*bs]
            dct_blk = scipy.fft.dctn(blk, norm="ortho")

            c1 = dct_blk[u1, v1]
            c2 = dct_blk[u2, v2]
            avg = (c1 + c2) / 2.0
            bit = watermark_bits[idx % num_bits]

            if bit == 1:
                dct_blk[u1, v1] = avg + self.alpha / 2.0
                dct_blk[u2, v2] = avg - self.alpha / 2.0
            else:
                dct_blk[u1, v1] = avg - self.alpha / 2.0
                dct_blk[u2, v2] = avg + self.alpha / 2.0

            cA_mod[br*bs:(br+1)*bs, bc*bs:(bc+1)*bs] = scipy.fft.idctn(dct_blk, norm="ortho")

        # Inverse 2D DWT
        Y_watermarked = pywt.idwt2((cA_mod, (cH, cV, cD)), self.wavelet)
        Y_watermarked = np.clip(Y_watermarked, 0, 255)

        # Handle potential boundary rounding from DWT
        Y_watermarked = Y_watermarked[:h, :w]
        ycrcb[:, :, 0] = Y_watermarked.astype(np.uint8)
        watermarked_rgb = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2RGB)

        psnr = WatermarkMetrics.calculate_psnr(image_rgb, watermarked_rgb)
        ssim = WatermarkMetrics.calculate_ssim(image_rgb, watermarked_rgb)

        meta = {
            "method": "DWT-DCT",
            "wavelet": self.wavelet,
            "alpha": self.alpha,
            "block_size": self.block_size,
            "eligible_blocks": len(eligible_blocks),
            "num_bits": num_bits,
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
        Blindly extracts watermark_bits from transform domain.
        Returns:
            extracted_bits: np.ndarray (shape (num_bits,), int32 {0, 1})
            meta: extraction diagnostic statistics
        """
        h, w = watermarked_rgb.shape[:2]
        ycrcb = cv2.cvtColor(watermarked_rgb, cv2.COLOR_RGB2YCrCb)
        Y = ycrcb[:, :, 0].astype(np.float64)

        cA, _ = pywt.dwt2(Y, self.wavelet)
        sub_h, sub_w = cA.shape

        bs = self.block_size
        num_blocks_r = sub_h // bs
        num_blocks_c = sub_w // bs

        eligible_blocks = self._get_eligible_blocks(pixel_mask, sub_h, sub_w, h, w)

        u1, v1 = self.coeff1
        u2, v2 = self.coeff2

        votes = [[] for _ in range(num_bits)]
        for idx, (br, bc) in enumerate(eligible_blocks):
            blk = cA[br*bs:(br+1)*bs, bc*bs:(bc+1)*bs]
            dct_blk = scipy.fft.dctn(blk, norm="ortho")
            c1 = dct_blk[u1, v1]
            c2 = dct_blk[u2, v2]
            vote = 1 if c1 > c2 else 0
            votes[idx % num_bits].append(vote)

        extracted_bits = np.array([int(np.mean(v) >= 0.5) for v in votes], dtype=np.int32)
        return extracted_bits, {"eligible_blocks": len(eligible_blocks), "bits": num_bits}

    def _get_eligible_blocks(
        self,
        pixel_mask: np.ndarray,
        sub_h: int,
        sub_w: int,
        spatial_h: int,
        spatial_w: int
    ) -> List[Tuple[int, int]]:
        """
        Conservative block eligibility rule:
        A transform block is eligible if and only if all spatial pixels
        corresponding to the block belong strictly to the unmasked data region.
        This guarantees zero transform coefficient ringing into quiet zones or structural patterns.
        """
        bs = self.block_size
        num_blocks_r = sub_h // bs
        num_blocks_c = sub_w // bs
        eligible = []
        for br in range(num_blocks_r):
            for bc in range(num_blocks_c):
                r0 = br * bs * 2
                r1 = min(spatial_h, (br + 1) * bs * 2)
                c0 = bc * bs * 2
                c1 = min(spatial_w, (bc + 1) * bs * 2)
                if np.all(pixel_mask[r0:r1, c0:c1]):
                    eligible.append((br, bc))
        return eligible

