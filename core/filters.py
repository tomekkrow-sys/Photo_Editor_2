#!/usr/bin/env python3
"""Photo filters (pencil sketch, etc.)."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter, ImageOps


def pencil_sketch(img: Image.Image, blur_radius: float | None = None) -> Image.Image:
    """Convert a photo to a pencil-sketch look (grayscale dodge-blend).

    Returns a new "L" mode image; the input image is not modified.
    """

    gray = img.convert("L")

    if blur_radius is None:
        blur_radius = max(3.0, max(gray.size) / 100.0)

    inverted = ImageOps.invert(gray)
    blurred = inverted.filter(ImageFilter.GaussianBlur(blur_radius))

    g = np.asarray(gray, dtype=np.float32)
    b = np.asarray(blurred, dtype=np.float32)

    # color dodge: g * 255 / (255 - b); where b == 255 -> white paper
    sketch = np.divide(
        g * 255.0,
        255.0 - b,
        out=np.full_like(g, 255.0),
        where=b < 255.0,
    )
    sketch = np.clip(sketch, 0, 255).astype(np.uint8)

    result = Image.fromarray(sketch, mode="L")
    return ImageOps.autocontrast(result, cutoff=1)
