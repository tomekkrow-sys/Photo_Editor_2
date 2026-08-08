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


def black_and_white(img: Image.Image, contrast: float = 0.5) -> Image.Image:
    """Convert a photo to black & white with a gentle S-curve.

    Weighted luminance keeps natural tones; the S-curve deepens shadows
    and lifts highlights a bit. Returns a new "L" mode image.
    """

    rgb = np.asarray(img.convert("RGB"), dtype=np.float32)
    lum = rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114

    x = lum / 255.0
    y = x + contrast * x * (1.0 - x) * (x - 0.5) * 4.0

    return Image.fromarray(
        np.clip(y * 255.0, 0, 255).astype(np.uint8),
        mode="L",
    )


def sepia(img: Image.Image) -> Image.Image:
    """Warm sepia tone; returns a new RGB image."""

    rgb = np.asarray(img.convert("RGB"), dtype=np.float32)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]

    out = np.stack(
        [
            r * 0.393 + g * 0.769 + b * 0.189,
            r * 0.349 + g * 0.686 + b * 0.168,
            r * 0.272 + g * 0.534 + b * 0.131,
        ],
        axis=-1,
    )
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), mode="RGB")


def negative(img: Image.Image) -> Image.Image:
    """Invert colors; returns a new RGB image."""

    rgb = np.asarray(img.convert("RGB"), dtype=np.uint8)
    return Image.fromarray(255 - rgb, mode="RGB")


def vignette(img: Image.Image, strength: float = 0.6) -> Image.Image:
    """Darken image corners; returns a new RGB image."""

    rgb = np.asarray(img.convert("RGB"), dtype=np.float32)
    h, w = rgb.shape[:2]

    y, x = np.ogrid[:h, :w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    corner = np.sqrt(2.0)
    falloff = np.clip((d - 0.5) / (corner - 0.5), 0.0, 1.0)
    mask = 1.0 - strength * falloff

    out = rgb * mask[..., None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), mode="RGB")


def auto_enhance(img: Image.Image) -> Image.Image:
    """One-click enhancement: gray-world white balance + contrast stretch.

    Returns a new RGB image.
    """

    rgb = np.asarray(img.convert("RGB"), dtype=np.float32)

    means = rgb.reshape(-1, 3).mean(axis=0)
    gray_mean = means.mean()
    gains = gray_mean / np.maximum(means, 1e-3)
    balanced = np.clip(rgb * gains, 0, 255)

    lum = balanced @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    lo, hi = np.percentile(lum, 1.0), np.percentile(lum, 99.0)
    if hi - lo < 1.0:
        return Image.fromarray(balanced.astype(np.uint8), mode="RGB")

    out = np.clip((balanced - lo) * (255.0 / (hi - lo)), 0, 255)
    return Image.fromarray(out.astype(np.uint8), mode="RGB")
