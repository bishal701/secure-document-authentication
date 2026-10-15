"""
QR Structural Pattern Masking Module.
Protects QR quiet zones, finder patterns (with separators), timing patterns,
format information, fixed dark modules, version information (versions >= 7),
and alignment patterns from watermark embedding artifacts to maintain high optical decodability.
Compliant with ISO/IEC 18004 specification.
"""

import numpy as np
from typing import Tuple, List, Optional

class QRStructureMasker:
    """
    Computes boolean masks over QR module grids and rendered pixel images.
    True = Eligible data/error-correction region (safe to watermark).
    False = Critical structural pattern or quiet zone (protected).
    """

    @staticmethod
    def get_module_mask(num_modules: int, version: Optional[int] = None) -> np.ndarray:
        """
        Creates a 2D boolean mask of shape (num_modules, num_modules).
        True indicates data/ECC modules; False indicates structural patterns.
        """
        if version is None:
            version = max(1, min(40, (num_modules - 17) // 4))

        mask = np.ones((num_modules, num_modules), dtype=bool)

        # 1. Finder patterns + 1-module separators (8x8 at 3 corners)
        # Top-Left finder + separator
        mask[0:8, 0:8] = False
        # Top-Right finder + separator
        mask[0:8, num_modules - 8:num_modules] = False
        # Bottom-Left finder + separator
        mask[num_modules - 8:num_modules, 0:8] = False

        # 2. Timing patterns: Row 6 and Column 6 (0-indexed)
        mask[6, :] = False
        mask[:, 6] = False

        # 3. Format Information & Fixed Dark Module
        # Top-Left: Row 8 (cols 0..8) and Col 8 (rows 0..8)
        mask[8, 0:9] = False
        mask[0:9, 8] = False
        # Top-Right: Row 8 (cols num_modules-8..num_modules-1)
        mask[8, num_modules - 8:num_modules] = False
        # Bottom-Left: Col 8 (rows num_modules-8..num_modules-1, including dark module at num_modules-8, 8)
        mask[num_modules - 8:num_modules, 8] = False

        # 4. Version Information (Versions 7 through 40, 18 bits each)
        if version >= 7:
            # 6x3 block to the left of Top-Right finder: rows 0:6, cols num_modules-11:num_modules-8
            mask[0:6, num_modules - 11:num_modules - 8] = False
            # 3x6 block above Bottom-Left finder: rows num_modules-11:num_modules-8, cols 0:6
            mask[num_modules - 11:num_modules - 8, 0:6] = False

        # 5. Alignment patterns for applicable versions (ISO/IEC 18004)
        alignment_centers = QRStructureMasker._get_alignment_centers(version, num_modules)
        for r_c in alignment_centers:
            for c_c in alignment_centers:
                # Skip if overlapping with finder patterns + separators
                if (r_c < 10 and c_c < 10) or (r_c < 10 and c_c > num_modules - 10) or (r_c > num_modules - 10 and c_c < 10):
                    continue
                r_start, r_end = max(0, r_c - 2), min(num_modules, r_c + 3)
                c_start, c_end = max(0, c_c - 2), min(num_modules, c_c + 3)
                mask[r_start:r_end, c_start:c_end] = False

        return mask

    @staticmethod
    def get_pixel_mask(
        image_shape: Tuple[int, int],
        num_modules: int,
        border_modules: int = 4,
        version: Optional[int] = None
    ) -> np.ndarray:
        """
        Scales the module mask up to the full rendered image dimension,
        accounting for the quiet zone border.
        """
        if version is None:
            version = max(1, min(40, (num_modules - 17) // 4))

        img_h, img_w = image_shape[:2]
        total_modules = num_modules + 2 * border_modules
        module_h = img_h / total_modules
        module_w = img_w / total_modules

        pixel_mask = np.zeros((img_h, img_w), dtype=bool)
        module_mask = QRStructureMasker.get_module_mask(num_modules, version=version)

        for r in range(num_modules):
            for c in range(num_modules):
                if module_mask[r, c]:
                    r_start = int(np.round((r + border_modules) * module_h))
                    r_end = int(np.round((r + border_modules + 1) * module_h))
                    c_start = int(np.round((c + border_modules) * module_w))
                    c_end = int(np.round((c + border_modules + 1) * module_w))
                    pixel_mask[r_start:r_end, c_start:c_end] = True

        return pixel_mask

    @staticmethod
    def _get_alignment_centers(version: int, num_modules: int) -> List[int]:
        """Returns standard alignment pattern center module indices for ISO/IEC 18004."""
        alignment_table = {
            1: [],
            2: [6, 18],
            3: [6, 22],
            4: [6, 26],
            5: [6, 30],
            6: [6, 34],
            7: [6, 22, 38],
            8: [6, 24, 42],
            9: [6, 26, 46],
            10: [6, 28, 50],
        }
        if version in alignment_table:
            return alignment_table[version]
        # General formula fallback for version > 10
        if version < 2:
            return []
        step = int(np.ceil((num_modules - 13) / (version // 7 + 1)))
        centers = [6]
        pos = num_modules - 7
        while pos > 6:
            centers.insert(1, pos)
            pos -= step
        return sorted(list(set(centers)))
