#!/usr/bin/env python3
"""Photo filters (pencil sketch, etc.)."""

from __future__ import annotations

import cv2
import numpy as np
from PIL import Image, ImageOps


def pencil_sketch(
    img: Image.Image,
    shading: float = 0.35,
    stroke_strength: float = 0.65,
    lift: float = 0.15,
) -> Image.Image:
    """Convert a photo to a natural pencil-sketch look.

    OpenCV hatching texture (softened so it never goes pitch black)
    combined with a tonal layer whose shadows are lifted: bright paper,
    visible pencil grain, smooth highlight-shadow transitions.

    Returns a new "L" mode image; the input image is not modified.
    """

    gray = img.convert("L")
    g = np.asarray(gray, dtype=np.float32)

    bgr = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)
    strokes_cv, _ = cv2.pencilSketch(
        bgr,
        sigma_s=60,
        sigma_r=0.07,
        shade_factor=0.09,
    )

    strokes = 255.0 - (255.0 - strokes_cv.astype(np.float32)) * stroke_strength

    lifted = g * (1.0 - lift) + 255.0 * lift
    tone = 255.0 - (255.0 - lifted) * shading

    result = np.minimum(strokes, tone)
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


def frame(img: Image.Image, border: int | None = None, color=(255, 255, 255)) -> Image.Image:
    """Add a solid border around the photo; returns a new RGB image."""

    if border is None:
        border = max(4, min(img.size) // 25)
    return ImageOps.expand(img.convert("RGB"), border=border, fill=color)


def _largest_rotated_rect(w: float, h: float, angle_deg: float) -> tuple[float, float]:
    """Largest axis-aligned rectangle fitting inside a rotated w x h rect."""

    import math

    a = abs(math.radians(angle_deg)) % math.pi
    if a > math.pi / 2:
        a = math.pi - a
    if a < 1e-9:
        return float(w), float(h)

    sin_a, cos_a = math.sin(a), math.cos(a)
    if w >= h:
        side_long, side_short = float(w), float(h)
    else:
        side_long, side_short = float(h), float(w)

    if side_short <= 2.0 * sin_a * cos_a * side_long:
        x = 0.5 * side_short
        if w >= h:
            wr, hr = x / sin_a, x / cos_a
        else:
            wr, hr = x / cos_a, x / sin_a
    else:
        cos_2a = cos_a * cos_a - sin_a * sin_a
        wr = (w * cos_a - h * sin_a) / cos_2a
        hr = (h * cos_a - w * sin_a) / cos_2a
    return wr, hr


def straighten(img: Image.Image, angle_deg: float) -> Image.Image:
    """Rotate by an arbitrary angle and crop away the empty corners.

    Positive angle rotates counter-clockwise. Returns a new RGB image.
    """

    rgb = img.convert("RGB")
    if abs(angle_deg) < 1e-9:
        return rgb

    rotated = rgb.rotate(
        angle_deg, expand=True, resample=Image.Resampling.BICUBIC
    )
    wr, hr = _largest_rotated_rect(*rgb.size, angle_deg)
    wr, hr = int(wr), int(hr)
    if wr < 1 or hr < 1:
        return rotated

    left = (rotated.width - wr) // 2
    top = (rotated.height - hr) // 2
    return rotated.crop((left, top, left + wr, top + hr))


WATERMARK_POSITIONS = (
    "Lewy gorny rog",
    "Prawy gorny rog",
    "Srodek",
    "Lewy dolny rog",
    "Prawy dolny rog",
)


def watermark(
    img: Image.Image,
    text: str,
    position: str = "Prawy dolny rog",
    opacity: float = 0.6,
    size: int | None = None,
) -> Image.Image:
    """Draw a text watermark; returns a new RGB image."""

    from PIL import ImageDraw, ImageFont

    base = img.convert("RGBA")
    w, h = base.size
    if size is None:
        size = max(14, min(base.size) // 20)

    font = ImageFont.load_default(size)
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    margin = max(8, size // 2)

    x = margin
    y = margin
    if "Prawy" in position:
        x = w - tw - margin
    if "dolny" in position:
        y = h - th - margin
    if position == "Srodek":
        x = (w - tw) // 2
        y = (h - th) // 2

    alpha = int(255 * max(0.0, min(1.0, opacity)))
    draw.text(
        (x, y),
        text,
        font=font,
        fill=(255, 255, 255, alpha),
        stroke_width=max(1, size // 12),
        stroke_fill=(0, 0, 0, alpha),
    )
    return Image.alpha_composite(base, layer).convert("RGB")


BLEND_MODES = ("Normalny", "Pomnoz", "Nakladka", "Ekran")


def composite(
    base: Image.Image,
    overlay: Image.Image,
    opacity: float = 1.0,
    mode: str = "Normalny",
) -> Image.Image:
    """Composite an overlay image onto base with opacity and blend mode.

    The overlay is resized to the base size. Returns a new RGB image.
    """

    b = np.asarray(base.convert("RGB"), dtype=np.float32) / 255.0
    o = overlay.convert("RGB").resize(base.size, Image.Resampling.LANCZOS)
    o = np.asarray(o, dtype=np.float32) / 255.0

    if mode == "Pomnoz":
        mixed = b * o
    elif mode == "Nakladka":
        mixed = np.where(b < 0.5, 2.0 * b * o, 1.0 - 2.0 * (1.0 - b) * (1.0 - o))
    elif mode == "Ekran":
        mixed = 1.0 - (1.0 - b) * (1.0 - o)
    else:
        mixed = o

    out = b * (1.0 - opacity) + mixed * opacity
    return Image.fromarray(
        np.clip(out * 255.0, 0, 255).astype(np.uint8),
        mode="RGB",
    )


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
