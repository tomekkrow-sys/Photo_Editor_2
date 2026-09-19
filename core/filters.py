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


# ==========================================================
# NEW FILTERS
# ==========================================================


def hdr_tone_map(img: Image.Image, strength: float = 0.5) -> Image.Image:
    """HDR-like tone mapping effect."""
    arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    # Local tone mapping via bilateral filter
    bgr = cv2.cvtColor(arr.astype(np.uint8), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Create HDR effect by enhancing contrast locally
    clahe = cv2.createCLAHE(clipLimit=3.0 + strength * 5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    # Blend with original
    enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    result = cv2.addWeighted(bgr, 1.0 - strength * 0.4, enhanced_bgr, strength * 0.4, 0)
    return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))


def cartoon(img: Image.Image, strength: float = 0.5) -> Image.Image:
    """Cartoon / comic book effect."""
    arr = np.asarray(img.convert("RGB"), dtype=np.uint8)
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    # Edge detection
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.adaptiveThreshold(
        cv2.medianBlur(gray, 7),
        255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9
    )
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    # Smooth colors
    num_bilateral = max(1, int(strength * 7))
    color = bgr
    for _ in range(num_bilateral):
        color = cv2.bilateralFilter(color, 9, 9, 9)
    # Combine edges with smooth colors
    result = cv2.bitwise_and(color, edges_bgr)
    return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))


def glitch_art(img: Image.Image, strength: float = 0.5) -> Image.Image:
    """Glitch art effect - RGB channel displacement and scanlines."""
    arr = np.asarray(img.convert("RGB"), dtype=np.uint8)
    h, w, _ = arr.shape
    result = arr.copy()
    num_shifts = max(1, int(strength * 10))
    for _ in range(num_shifts):
        # Random horizontal shift for one channel
        channel = np.random.randint(0, 3)
        shift = np.random.randint(-int(w * 0.1 * strength), int(w * 0.1 * strength) + 1)
        result[:, :, channel] = np.roll(arr[:, :, channel], shift, axis=1)
    # Add scanlines
    scanline_spacing = max(2, int(6 - strength * 4))
    result[::scanline_spacing] = (result[::scanline_spacing] * 0.7).astype(np.uint8)
    # Add random color blocks
    num_blocks = int(strength * 5)
    for _ in range(num_blocks):
        y = np.random.randint(0, h)
        x = np.random.randint(0, w)
        bh = np.random.randint(1, max(2, int(h * 0.05)))
        bw = np.random.randint(1, max(2, int(w * 0.3)))
        color = [np.random.randint(0, 256) for _ in range(3)]
        y2 = min(y + bh, h)
        x2 = min(x + bw, w)
        result[y:y2, x:x2] = color
    return Image.fromarray(result)


def thermal(img: Image.Image, strength: float = 0.5) -> Image.Image:
    """Thermal camera / heat map effect."""
    arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    gray = np.mean(arr, axis=2).astype(np.uint8)
    # Apply colormap
    thermal_map = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    thermal_rgb = cv2.cvtColor(thermal_map, cv2.COLOR_BGR2RGB)
    # Blend with original based on strength
    result = (
        arr * (1.0 - strength) + thermal_rgb.astype(np.float32) * strength
    ).clip(0, 255).astype(np.uint8)
    return Image.fromarray(result)


def pixelate(img: Image.Image, block_size: int = 8) -> Image.Image:
    """Pixelate / mosaic effect."""
    w, h = img.size
    small = img.resize((max(1, w // block_size), max(1, h // block_size)), Image.Resampling.NEAREST)
    return small.resize((w, h), Image.Resampling.NEAREST)


def duotone(img: Image.Image, color1: str = "#FF6B35", color2: str = "#004E89") -> Image.Image:
    """Duotone effect - map grayscale to two colors."""
    from PIL import ImageDraw
    gray = img.convert("L")
    w, h = gray.size
    c1 = ImageDraw.Draw(Image.new("RGB", (1, 1))).getrgb(color1)
    c2 = ImageDraw.Draw(Image.new("RGB", (1, 1))).getrgb(color2)
    result = Image.new("RGB", (w, h))
    gray_arr = np.asarray(gray, dtype=np.float32) / 255.0
    r = (gray_arr * c1[0] + (1 - gray_arr) * c2[0]).astype(np.uint8)
    g = (gray_arr * c1[1] + (1 - gray_arr) * c2[1]).astype(np.uint8)
    b = (gray_arr * c1[2] + (1 - gray_arr) * c2[2]).astype(np.uint8)
    return Image.fromarray(np.stack([r, g, b], axis=2))


def denoise(img: Image.Image, strength: int = 10) -> Image.Image:
    """Reduce noise using Non-Local Means denoising."""
    arr = np.array(img.convert("RGB"))
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    result = cv2.fastNlMeansDenoisingColored(bgr, None, strength, strength, 7, 21)
    return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))


def perspective(img: Image.Image, corners: list = None) -> Image.Image:
    """Apply perspective transform given 4 corner points (top-left, top-right, bottom-right, bottom-left).
    corners should be list of 4 (x,y) tuples in original image coords.
    """
    if corners is None or len(corners) != 4:
        return img
    arr = np.array(img.convert("RGB"))
    h, w = arr.shape[:2]
    src = np.float32(corners)
    # Calculate output rectangle
    w_top = np.linalg.norm(src[1] - src[0])
    w_bot = np.linalg.norm(src[2] - src[3])
    h_left = np.linalg.norm(src[3] - src[0])
    h_right = np.linalg.norm(src[2] - src[1])
    out_w = int(max(w_top, w_bot))
    out_h = int(max(h_left, h_right))
    dst = np.float32([[0, 0], [out_w - 1, 0], [out_w - 1, out_h - 1], [0, out_h - 1]])
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    matrix = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(bgr, matrix, (out_w, out_h))
    return Image.fromarray(cv2.cvtColor(warped, cv2.COLOR_BGR2RGB))


def add_text_overlay(img: Image.Image, text: str, font_name: str = "Arial",
                     font_size: int = 48, color: tuple = (255, 255, 255),
                     opacity: float = 1.0, position: tuple = (0, 0),
                     anchor: str = "center", bold: bool = False,
                     shadow: dict | None = None, outline: dict | None = None) -> Image.Image:
    """Add text overlay with optional shadow and outline."""
    from PIL import ImageDraw, ImageFont, ImageFilter
    result = img.convert("RGBA")
    overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
                                  "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except (OSError, IOError):
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (OSError, IOError):
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x, y = position

    if anchor == "center":
        x -= tw // 2
        y -= th // 2
    elif anchor == "right":
        x -= tw
    elif anchor == "topleft":
        pass
    elif anchor == "topright":
        x -= tw
    elif anchor == "bottomleft":
        y -= th
    elif anchor == "bottomright":
        x -= tw
        y -= th

    alpha = int(255 * opacity)
    fill = (color[0], color[1], color[2], alpha)

    # Shadow
    if shadow:
        sh_alpha = int(255 * shadow.get("opacity", 0.7))
        sh_fill = (shadow["color"][0], shadow["color"][1], shadow["color"][2], sh_alpha)
        sh_ox = shadow.get("offset_x", 3)
        sh_oy = shadow.get("offset_y", 3)
        # Shadow layer with blur
        sh_layer = Image.new("RGBA", result.size, (0, 0, 0, 0))
        sh_draw = ImageDraw.Draw(sh_layer)
        sh_draw.text((x + sh_ox, y + sh_oy), text, font=font, fill=sh_fill)
        sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(radius=3))
        overlay = Image.alpha_composite(overlay, sh_layer)
        draw = ImageDraw.Draw(overlay)

    # Outline
    if outline:
        ow = outline.get("width", 3)
        ol_fill = (outline["color"][0], outline["color"][1], outline["color"][2], alpha)
        for dx in range(-ow, ow + 1):
            for dy in range(-ow, ow + 1):
                if dx * dx + dy * dy <= ow * ow:
                    draw.text((x + dx, y + dy), text, font=font, fill=ol_fill)

    # Main text
    draw.text((x, y), text, font=font, fill=fill)
    result = Image.alpha_composite(result, overlay)
    return result.convert("RGB")


def lens_correction(img: Image.Image, k1: float = 0.0, k2: float = 0.0,
                    k3: float = 0.0, p1: float = 0.0, p2: float = 0.0) -> Image.Image:
    """Apply lens distortion correction (radial + tangential)."""
    arr = np.array(img.convert("RGB"))
    h, w = arr.shape[:2]
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    camera_matrix = np.array([[w / 2, 0, w / 2], [0, w / 2, h / 2], [0, 0, 1]], dtype=np.float32)
    dist_coeffs = np.array([k1, k2, p1, p2, k3], dtype=np.float32)
    new_camera, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))
    result = cv2.undistort(bgr, camera_matrix, dist_coeffs, None, new_camera)
    return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))


def smart_crop(img: Image.Image, ratio: float = 16/9, margin: float = 0.05) -> Image.Image:
    """Smart crop: find the most interesting region using edge/saliency analysis.
    
    ratio: target aspect ratio (width/height), e.g. 16/9
    margin: how much of the shorter axis to use as search window step
    Returns cropped PIL Image.
    """
    arr = np.array(img.convert("RGB"))
    h, w = arr.shape[:2]
    
    # Target crop dimensions
    cur_ratio = w / h
    if ratio > cur_ratio:
        crop_w = w
        crop_h = int(w / ratio)
    else:
        crop_h = h
        crop_w = int(h * ratio)
    
    # Ensure crop fits
    crop_w = min(crop_w, w)
    crop_h = min(crop_h, h)
    
    if crop_w >= w and crop_h >= h:
        return img.copy()
    
    # Edge detection for saliency
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edges = edges.astype(np.float32) / 255.0
    
    # Rule-of-thirds grid preference (bonus for center composition)
    rof = np.zeros_like(edges)
    cy, cx = h / 2, w / 2
    for y in range(h):
        for x in range(w):
            # Distance from rule-of-thirds intersection points
            d1 = ((x/3 - cx)**2 + (y/3 - cy)**2)**0.5
            d2 = ((2*x/3 - cx)**2 + (2*y/3 - cy)**2)**0.5
            d = min(d1, d2)
            rof[y, x] = max(0, 1.0 - d / (w * 0.3))
    
    # Combine edge saliency with rule-of-thirds
    saliency = edges * 0.7 + rof * 0.3
    
    # Sliding window search
    best_score = -1
    best_x, best_y = 0, 0
    
    step_x = max(1, int(w * margin / 10))
    step_y = max(1, int(h * margin / 10))
    
    for y in range(0, h - crop_h + 1, step_y):
        for x in range(0, w - crop_w + 1, step_x):
            window = saliency[y:y+crop_h, x:x+crop_w]
            score = window.mean()
            # Slight center preference
            cy_score = 1.0 - abs(y + crop_h/2 - h/2) / (h/2)
            cx_score = 1.0 - abs(x + crop_w/2 - w/2) / (w/2)
            score *= (0.85 + 0.15 * (cy_score + cx_score) / 2)
            if score > best_score:
                best_score = score
                best_x, best_y = x, y
    
    return img.crop((best_x, best_y, best_x + crop_w, best_y + crop_h))


def smart_crop_auto(img: Image.Image) -> Image.Image:
    """Smart crop with auto-detected aspect ratio (keep closest standard ratio)."""
    w, h = img.size
    ratio = w / h
    # Pick closest standard ratio
    standards = [16/9, 4/3, 3/2, 1/1, 2/3, 3/4, 9/16]
    closest = min(standards, key=lambda r: abs(r - ratio))
    return smart_crop(img, ratio=closest)
