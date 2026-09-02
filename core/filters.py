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
# New filters: GaussianBlur, Sharpen, Emboss, Vignette


def gaussian_blur(img: Image.Image, kernel_size: int = 5, sigma: float = 1.0) -> Image.Image:
    """Apply Gaussian blur to an image.

    Smooths the image by convolving with a Gaussian kernel, reducing noise and detail.

    Args:
        img: Input image (RGB, RGBA, L, or P).
        kernel_size: Size of the Gaussian kernel (must be odd).
        sigma: Standard deviation of the Gaussian kernel.

    Returns:
        New image with Gaussian blur applied.
    """
    # Ensure RGB or RGBA for processing
    if img.mode in ("P",):
        img = img.convert("RGB")
    elif img.mode == "L":
        # For grayscale, keep it but convert back later
        pass

    arr = np.asarray(img.convert("RGB"), dtype=np.float32)

    # OpenCV uses BGR, so convert
    bgr = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2BGR)

    # Ensure kernel_size is odd
    if kernel_size % 2 == 0:
        kernel_size += 1

    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(
        bgr,
        (kernel_size, kernel_size),
        sigma,
        borderType=cv2.BORDER_DEFAULT,
    )

    # Convert back to RGB
    result = cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB)

    # Preserve original mode if grayscale
    if img.mode == "L":
        # Compute luminance from blurred RGB to get back grayscale
        gray = 0.299 * result[..., 0] + 0.587 * result[..., 1] + 0.114 * result[..., 2]
        result = gray.astype(np.uint8)

    return Image.fromarray(result.astype(np.uint8), mode=img.mode)


def sharpen(
    img: Image.Image, amount: float = 1.0, radius: int = 1
) -> Image.Image:
    """Apply sharpening to enhance edges and details.

    Uses unsharp masking: sharp = original + amount * (original - blurred).

    Args:
        img: Input image (RGB, RGBA, L).
        amount: Strength of sharpening (0.0 = no sharpening, 1.0 = standard).
        radius: Blur radius for creating the blurred version.

    Returns:
        New image with sharpening applied.
    """
    if img.mode == "P":
        img = img.convert("RGB")

    arr = np.asarray(img.convert("RGB"), dtype=np.float32)

    # Create blurred version for unsharp mask
    blurred = cv2.GaussianBlur(arr.astype(np.uint8), (0, 0), radius)

    # Unsharp mask: sharp = original + amount * (original - blurred)
    sharpened = arr + amount * (arr - blurred)

    result = np.clip(sharpened, 0, 255).astype(np.uint8)

    return Image.fromarray(result, mode=img.mode if img.mode in ("RGB", "L") else "RGB")


def emboss(
    img: Image.Image, intensity: float = 1.0, angle: float = 45.0
) -> Image.Image:
    """Apply emboss effect to create a 3D relief appearance.

    Uses Sobel-based edge detection with directional lighting.

    Args:
        img: Input image (RGB, RGBA, L).
        intensity: Strength of embossing (0.0 = no emboss, 1.0 = standard).
        angle: Direction of light source in degrees (0 = from right, 90 = from top).

    Returns:
        New RGB image with emboss effect.
    """
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    elif img.mode == "L":
        pass

    arr = np.asarray(img.convert("RGB"), dtype=np.float32)

    # Convert to grayscale for edge detection
    gray = 0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]

    # Sobel operators
    sobel_x = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)

    # Combine Sobel gradients
    magnitude = np.sqrt(sobel_x**2 + sobel_y**2)

    # Normalize to [0, 1]
    magnitude = magnitude / (np.max(magnitude) + 1e-6)

    # Create emboss base (mid-gray)
    embossed = np.full_like(arr, 128, dtype=np.float32)

    # Apply emboss based on gradient direction and intensity
    angle_rad = np.radians(angle)
    light_x = np.cos(angle_rad)
    light_y = np.sin(angle_rad)

    # Dot product of gradient with light direction
    gradient_direction = np.arctan2(sobel_y, sobel_x)
    light_direction = angle_rad
    dot_product = np.cos(gradient_direction - light_direction)

    # Apply emboss
    embossed += magnitude * dot_product * intensity * 64

    # Add subtle lighting gradient for depth
    h, w = gray.shape
    y, x = np.ogrid[:h, :w]
    depth = (x / w + y / h) * 0.5
    embossed += depth * intensity * 16

    result = np.clip(embossed, 0, 255).astype(np.uint8)

    return Image.fromarray(result, mode="RGB")


def vignette(
    img: Image.Image,
    strength: float = 0.6,
    roundness: float = 1.0,
    center: tuple[float, float] = (0.5, 0.5),
) -> Image.Image:
    """Apply vignette effect to darken image corners.

    Args:
        img: Input image (RGB, RGBA, L).
        strength: Darkness of corners (0.0 = no vignette, 1.0 = strong).
        roundness: Shape of vignette (0.0 = square, 1.0 = circular).
        center: Vignette center as (x_ratio, y_ratio) in [0, 1].

    Returns:
        New RGB image with vignette applied.
    """
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    elif img.mode == "L":
        pass

    arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    h, w = arr.shape[:2]

    y, x = np.ogrid[:h, :w]

    # Normalize coordinates relative to center
    x_norm = (x - w * center[0]) / (w / 2)
    y_norm = (y - h * center[1]) / (h / 2)

    # Distance from center (with roundness control)
    d = np.sqrt(x_norm**2 + y_norm**2)
    corner_distance = np.sqrt(2.0)
    # Adjust for roundness: power transformation
    falloff = np.power(d / corner_distance, roundness)
    falloff = np.clip(falloff, 0.0, 1.0)

    # Vignette mask: 1.0 at center, decreasing toward corners
    mask = 1.0 - strength * falloff

    # Apply mask
    result = arr * mask[..., None]

    return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8), mode="RGB")


# ============================================================================
# PLUGIN METADATA
# ============================================================================


__plugin_meta__ = {
    "gaussian_blur": {
        "name": "Gaussian Blur",
        "description": "Rozmycie Gaussa – wygładzenie obrazu poprzez rozkład Gaussa, przydatne do usuwania szumów i tworzenia efektu tła.",
        "parameters": {
            "kernel_size": {
                "type": "int",
                "default": 5,
                "min": 3,
                "max": 31,
                "step": 2,
                "description": "Rozmiar macierzy Gaussa (musi być nieparzysta).",
            },
            "sigma": {
                "type": "float",
                "default": 1.0,
                "min": 0.1,
                "max": 10.0,
                "step": 0.1,
                "description": "Odchylenie standardowe rozkładu Gaussa.",
            },
        },
        "output_mode": "RGB",
        "supported_modes": ["RGB", "RGBA", "L", "P"],
    },
    "sharpen": {
        "name": "Sharpen",
        "description": "Ostrzenie – wzmocnienie krawędzi i szczegółów obrazu.",
        "parameters": {
            "amount": {
                "type": "float",
                "default": 1.0,
                "min": 0.0,
                "max": 3.0,
                "step": 0.1,
                "description": "Siła ostrzenia (0.0 = brak, 1.0 = standardowe).",
            },
            "radius": {
                "type": "int",
                "default": 1,
                "min": 1,
                "max": 10,
                "step": 1,
                "description": "Promień rozmycia do tworzenia wersji rozmytej.",
            },
        },
        "output_mode": "RGB",
        "supported_modes": ["RGB", "RGBA", "L", "P"],
    },
    "emboss": {
        "name": "Emboss",
        "description": "Wydrążenie – efekt 3D poprzez wykrywanie gradientów (Sobel) z kierunkiem światła.",
        "parameters": {
            "intensity": {
                "type": "float",
                "default": 1.0,
                "min": 0.0,
                "max": 2.0,
                "step": 0.1,
                "description": "Siła efektu wydrążenia (0.0 = brak, 1.0 = standardowe).",
            },
            "angle": {
                "type": "float",
                "default": 45.0,
                "min": 0.0,
                "max": 360.0,
                "step": 1.0,
                "description": "Kierunek źródła światła w stopniach (0 = z prawej, 90 = z góry).",
            },
        },
        "output_mode": "RGB",
        "supported_modes": ["RGB", "RGBA", "L", "P"],
    },
    "vignette": {
        "name": "Vignette",
        "description": "Winieta – przyciemnienie rogów obrazu w porównaniu do środka.",
        "parameters": {
            "strength": {
                "type": "float",
                "default": 0.6,
                "min": 0.0,
                "max": 1.0,
                "step": 0.1,
                "description": "Siła przyciemnienia rogów (0.0 = brak, 1.0 = silne).",
            },
            "roundness": {
                "type": "float",
                "default": 1.0,
                "min": 0.0,
                "max": 2.0,
                "step": 0.1,
                "description": "Kształt winietowania (0.0 = kwadratowy, 1.0 = kołowy).",
            },
            "center": {
                "type": "tuple[float, float]",
                "default": [0.5, 0.5],
                "min": [0.0, 0.0],
                "max": [1.0, 1.0],
                "step": [0.1, 0.1],
                "description": "Środek winietu jako (x_ratio, y_ratio) w zakresie [0, 1].",
            },
        },
        "output_mode": "RGB",
        "supported_modes": ["RGB", "RGBA", "L", "P"],
    },
}
