"""Validation and refinement module for detected Hebrew columns.

CONSERVATIVE: Only fixes very specific, clear problems.
"""

import cv2
import numpy as np
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


def expand_width_if_text_cut(
    thresh: np.ndarray, x: int, w: int, max_expand: int = 200
) -> Tuple[int, int]:
    """
    Check if text is cut off at the right edge and expand width if needed.
    
    CONSERVATIVE: Only expands when there's clear evidence of text being cut.
    Targets specific problem images: 000016, 000056, 000062
    
    Args:
        thresh: Thresholded binary image
        x: Current x position
        w: Current width
        max_expand: Maximum pixels to expand
        
    Returns:
        Updated (x, w) tuple
    """
    height, width = thresh.shape[:2]
    
    # Only check narrow columns (<850px) - wider columns are less likely to be cut
    if w >= 850:
        return x, w
    
    # Check density at right edge (last 40px of column)
    right_edge_start = max(x + w - 40, x)
    right_edge_end = min(x + w, width)
    right_edge_region = thresh[:, right_edge_start:right_edge_end]
    
    if right_edge_region.size == 0:
        return x, w
    
    right_edge_density = np.sum(right_edge_region > 0) / right_edge_region.size
    
    # Only expand if there's HIGH density at edge (>18%) indicating text is present
    if right_edge_density > 0.18:
        # Check region beyond current width (first 60px)
        expand_start = min(x + w, width - 1)
        expand_end = min(x + w + 60, width)
        
        if expand_end > expand_start:
            beyond_region = thresh[:, expand_start:expand_end]
            beyond_density = np.sum(beyond_region > 0) / beyond_region.size if beyond_region.size > 0 else 0
            
            # Need significant density beyond edge (>12%) to expand
            if beyond_density > 0.12:
                # Find where text actually ends
                expand_full_end = min(x + w + max_expand, width)
                best_end = expand_start
                
                # Check in 20px increments to find end of text
                for check_x in range(expand_start, expand_full_end, 20):
                    check_strip = thresh[:, check_x:min(check_x + 40, width)]
                    if check_strip.size == 0:
                        break
                        
                    strip_density = np.sum(check_strip > 0) / check_strip.size
                    
                    # Track where text ends (density drops below threshold)
                    if strip_density > 0.08:
                        best_end = check_x + 40
                    else:
                        # Text ended, stop here
                        break
                
                # Only expand if we found meaningful continuation (at least 40px)
                if best_end > expand_start + 40:
                    new_w = best_end - x
                    # Don't expand beyond reasonable Hebrew column width
                    new_w = min(new_w, 1100)
                    # Only expand if it's a meaningful increase (at least 40px)
                    if new_w > w + 40:
                        logger.info(f"Expanding width from {w} to {new_w} (text cut detected)")
                        return x, new_w
    
    return x, w
