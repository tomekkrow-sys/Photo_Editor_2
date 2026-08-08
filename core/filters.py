#!/usr/bin/env python3
"""Photo filters (pencil sketch, etc.)."""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image


def pencil_sketch(img: Image.Image, shading: float = 0.35) -> Image.Image:
    """Convert a photo to a natural pencil-sketch look.

    Combines cv2 pencil strokes with a soft tonal layer so highlights,
    shadows and their transitions stay visible (white paper is kept).

    Returns a new "L" mode image; the input image is not modified.
    """

    rgb = np.asarray(img.convert("RGB"))
    gray = np.asarray(img.convert("L"), dtype=np.float32)

    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    strokes, _ = cv2.pencilSketch(
        bgr,
        sigma_s=60,
        sigma_r=0.07,
        shade_factor=0.06,
    )

    tone = 255.0 - (255.0 - gray) * shading
    result = np.minimum(strokes.astype(np.float32), tone)

    return Image.fromarray(
        np.clip(result, 0, 255).astype(np.uint8),
        mode="L",
    )
