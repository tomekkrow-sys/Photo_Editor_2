"""Tests for the pencil sketch filter."""

from __future__ import annotations

import unittest

import numpy as np
from PIL import Image

from core.filters import (
    auto_enhance,
    black_and_white,
    composite,
    frame,
    negative,
    pencil_sketch,
    sepia,
    straighten,
    vignette,
    watermark,
)


class PencilSketchTests(unittest.TestCase):
    """Verify pencil sketch conversion behavior."""

    def test_returns_grayscale_image_of_same_size(self) -> None:
        img = Image.new("RGB", (120, 80), (200, 120, 60))

        result = pencil_sketch(img)

        self.assertEqual(result.mode, "L")
        self.assertEqual(result.size, img.size)

    def test_does_not_modify_original(self) -> None:
        img = Image.new("RGB", (64, 64), (10, 200, 90))
        before = np.asarray(img).copy()

        pencil_sketch(img)

        np.testing.assert_array_equal(np.asarray(img), before)

    def test_edges_produce_soft_strokes_on_bright_paper(self) -> None:
        from PIL import ImageDraw, ImageFilter

        img = Image.new("RGB", (300, 200))
        draw = ImageDraw.Draw(img)
        for x in range(300):
            value = int(255 * x / 300)
            draw.line([(x, 0), (x, 200)], fill=(value, value, value))
        draw.ellipse([60, 40, 160, 160], fill=(30, 30, 40))
        img = img.filter(ImageFilter.GaussianBlur(2))

        result = np.asarray(pencil_sketch(img))

        # natural look: bright paper, visible dark-gray (never black) strokes
        self.assertGreater(float(result.mean()), 180.0)
        self.assertLess(int(result.min()), int(result.mean()))
        self.assertGreater(int(result.min()), 90)

    def test_blank_white_image_stays_white(self) -> None:
        img = Image.new("RGB", (200, 200), (255, 255, 255))

        result = np.asarray(pencil_sketch(img))

        self.assertGreater(float(result.mean()), 250.0)

    def test_accepts_non_rgb_modes(self) -> None:
        img = Image.new("RGBA", (50, 40), (120, 60, 200, 128))

        result = pencil_sketch(img)

        self.assertEqual(result.mode, "L")
        self.assertEqual(result.size, (50, 40))

    def test_smooth_gradient_keeps_tonal_gradation(self) -> None:
        img = Image.new("RGB", (256, 40))
        for x in range(256):
            for y in range(40):
                img.putpixel((x, y), (x, x, x))

        result = np.asarray(pencil_sketch(img), dtype=np.int16)

        left_mean = int(result[:, :20].mean())
        right_mean = int(result[:, -20:].mean())
        self.assertLess(left_mean, right_mean - 30)
        self.assertGreater(int(result.max()) - int(result.min()), 40)


class BlackAndWhiteTests(unittest.TestCase):
    """Verify black & white conversion behavior."""

    def test_returns_grayscale_image_of_same_size(self) -> None:
        img = Image.new("RGB", (120, 80), (200, 120, 60))

        result = black_and_white(img)

        self.assertEqual(result.mode, "L")
        self.assertEqual(result.size, img.size)

    def test_does_not_modify_original(self) -> None:
        img = Image.new("RGB", (64, 64), (10, 200, 90))
        before = np.asarray(img).copy()

        black_and_white(img)

        np.testing.assert_array_equal(np.asarray(img), before)

    def test_uniform_image_stays_uniform(self) -> None:
        img = Image.new("RGB", (60, 60), (128, 128, 128))

        result = np.asarray(black_and_white(img))

        self.assertEqual(int(result.min()), int(result.max()))

    def test_contrast_curve_increases_spread(self) -> None:
        img = Image.new("RGB", (256, 10))
        for x in range(256):
            for y in range(10):
                img.putpixel((x, y), (x, x, x))

        plain = np.asarray(black_and_white(img, contrast=0.0))
        curved = np.asarray(black_and_white(img, contrast=0.8))

        mid = 128
        self.assertLess(int(curved[0, 64]), int(plain[0, 64]))
        self.assertGreater(int(curved[0, 192]), int(plain[0, 192]))
        self.assertEqual(int(curved[0, mid]), mid)


class SimpleFiltersTests(unittest.TestCase):
    """Verify sepia, negative, vignette and auto-enhance behavior."""

    def test_sepia_warms_image(self) -> None:
        img = Image.new("RGB", (40, 30), (100, 100, 100))

        result = sepia(img)

        self.assertEqual(result.mode, "RGB")
        self.assertEqual(result.size, img.size)
        r, g, b = result.getpixel((0, 0))
        self.assertGreater(r, g)
        self.assertGreater(g, b)

    def test_negative_inverts_colors(self) -> None:
        img = Image.new("RGB", (10, 10), (10, 200, 90))

        result = negative(img)

        self.assertEqual(result.getpixel((0, 0)), (245, 55, 165))
        self.assertEqual(result.mode, "RGB")

    def test_vignette_darkens_corners_not_center(self) -> None:
        img = Image.new("RGB", (100, 100), (200, 200, 200))

        result = vignette(img, strength=0.6)

        center = result.getpixel((50, 50))[0]
        corner = result.getpixel((2, 2))[0]
        self.assertGreater(center, corner)
        self.assertEqual(center, 200)

    def test_auto_enhance_stretches_contrast(self) -> None:
        img = Image.new("RGB", (100, 10))
        for x in range(100):
            value = 100 + x  # narrow tonal range 100..199
            for y in range(10):
                img.putpixel((x, y), (value, value, value))

        result = np.asarray(auto_enhance(img))

        self.assertGreater(
            float(result.max()) - float(result.min()), 150.0
        )

    def test_auto_enhance_does_not_modify_original(self) -> None:
        img = Image.new("RGB", (30, 30), (120, 60, 180))
        before = np.asarray(img).copy()

        auto_enhance(img)

        np.testing.assert_array_equal(np.asarray(img), before)


class FrameTests(unittest.TestCase):
    """Verify the frame filter."""

    def test_frame_enlarges_by_border(self) -> None:
        img = Image.new("RGB", (100, 60), (10, 20, 30))

        result = frame(img, border=10)

        self.assertEqual(result.size, (120, 80))
        self.assertEqual(result.getpixel((0, 0)), (255, 255, 255))
        self.assertEqual(result.getpixel((60, 40)), (10, 20, 30))

    def test_frame_default_border(self) -> None:
        img = Image.new("RGB", (100, 100))

        result = frame(img)

        self.assertGreater(result.width, 100)


class CompositeTests(unittest.TestCase):
    """Verify layer compositing (opacity and blend modes)."""

    def test_normal_mode_replaces_at_full_opacity(self) -> None:
        base = Image.new("RGB", (20, 20), (50, 50, 50))
        overlay = Image.new("RGB", (40, 40), (200, 100, 50))

        result = composite(base, overlay, opacity=1.0, mode="Normalny")

        self.assertEqual(result.size, (20, 20))
        self.assertEqual(result.getpixel((10, 10)), (200, 100, 50))

    def test_zero_opacity_keeps_base(self) -> None:
        base = Image.new("RGB", (10, 10), (50, 60, 70))
        overlay = Image.new("RGB", (10, 10), (250, 250, 250))

        result = composite(base, overlay, opacity=0.0)

        self.assertEqual(result.getpixel((5, 5)), (50, 60, 70))

    def test_multiply_darkens_screen_brightens(self) -> None:
        base = Image.new("RGB", (10, 10), (128, 128, 128))
        overlay = Image.new("RGB", (10, 10), (128, 128, 128))

        dark = composite(base, overlay, mode="Pomnoz")
        light = composite(base, overlay, mode="Ekran")

        self.assertLess(dark.getpixel((5, 5))[0], 128)
        self.assertGreater(light.getpixel((5, 5))[0], 128)

    def test_overlay_is_resized_to_base(self) -> None:
        base = Image.new("RGB", (100, 50), (0, 0, 0))
        overlay = Image.new("RGB", (500, 500), (255, 255, 255))

        result = composite(base, overlay)

        self.assertEqual(result.size, (100, 50))
        self.assertEqual(result.getpixel((50, 25)), (255, 255, 255))


class StraightenTests(unittest.TestCase):
    """Verify arbitrary-angle rotation with auto-crop."""

    def test_zero_angle_keeps_size(self) -> None:
        img = Image.new("RGB", (200, 100), (10, 20, 30))

        result = straighten(img, 0.0)

        self.assertEqual(result.size, (200, 100))

    def test_45_degrees_crops_to_inscribed_rect(self) -> None:
        img = Image.new("RGB", (200, 200), (128, 64, 32))

        result = straighten(img, 45.0)

        self.assertEqual(result.mode, "RGB")
        self.assertLess(result.width, 200)
        self.assertGreater(result.width, 100)

    def test_content_preserved_near_center(self) -> None:
        img = Image.new("RGB", (200, 200), (128, 64, 32))

        result = straighten(img, 10.0)

        cx, cy = result.width // 2, result.height // 2
        r, g, b = result.getpixel((cx, cy))
        self.assertTrue(abs(r - 128) < 30 and abs(g - 64) < 30)


class WatermarkTests(unittest.TestCase):
    """Verify text watermark rendering."""

    def test_watermark_draws_text(self) -> None:
        img = Image.new("RGB", (400, 300), (255, 255, 255))

        result = watermark(img, "TEST", "Prawy dolny rog", 1.0)

        self.assertEqual(result.mode, "RGB")
        self.assertEqual(result.size, img.size)
        pixels = np.asarray(result)
        self.assertLess(int(pixels.min()), 255)

    def test_watermark_respects_position(self) -> None:
        img = Image.new("RGB", (400, 300), (255, 255, 255))

        left = watermark(img, "ABCDEF", "Lewy gorny rog", 1.0)
        right = watermark(img, "ABCDEF", "Prawy dolny rog", 1.0)

        self.assertLess(int(np.asarray(left)[20:60, 20:200].min()), 255)
        top_left_of_right = np.asarray(right)[20:60, 20:200]
        self.assertEqual(int(top_left_of_right.min()), 255)

    def test_empty_opacity_keeps_image(self) -> None:
        img = Image.new("RGB", (100, 100), (200, 100, 50))

        result = watermark(img, "X", "Srodek", 0.0)

        self.assertEqual(result.getpixel((10, 10)), (200, 100, 50))

class GaussianBlurTests(unittest.TestCase):
    """Verify Gaussian blur behavior."""

    def test_returns_image_of_same_size(self) -> None:
        img = Image.new("RGB", (120, 80), (200, 120, 60))

        result = gaussian_blur(img, kernel_size=5, sigma=1.0)

        self.assertEqual(result.mode, "RGB")
        self.assertEqual(result.size, img.size)

    def test_does_not_modify_original(self) -> None:
        img = Image.new("RGB", (64, 64), (10, 200, 90))
        before = np.asarray(img).copy()

        gaussian_blur(img, kernel_size=7)

        np.testing.assert_array_equal(np.asarray(img), before)

    def test_higher_sigma_leads_to_more_blur(self) -> None:
        img = Image.new("RGB", (60, 60), (128, 128, 128))
        # Add some noise
        noise = np.random.randint(-30, 30, (60, 60, 3), dtype=np.int16)
        img_array = np.asarray(img).astype(np.int16)
        noisy = np.clip(img_array + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(noisy, "RGB")

        result_low = np.asarray(gaussian_blur(img, kernel_size=5, sigma=1.0))
        result_high = np.asarray(gaussian_blur(img, kernel_size=5, sigma=3.0))

        # Higher sigma should smooth out variations more
        self.assertLess(result_high.std(), result_low.std())

    def test_accepts_rgba_and_grayscale(self) -> None:
        rgba = Image.new("RGBA", (40, 30), (120, 60, 200, 255))
        gray = Image.new("L", (50, 40), 128)

        result_rgba = gaussian_blur(rgba, kernel_size=5)
        result_gray = gaussian_blur(gray, kernel_size=5)

        self.assertEqual(result_rgba.mode, "RGBA")
        self.assertEqual(result_gray.mode, "L")


class SharpenTests(unittest.TestCase):
    """Verify sharpen filter behavior."""

    def test_sharpen_returns_same_size(self) -> None:
        img = Image.new("RGB", (120, 80), (100, 150, 200))
        result = sharpen(img, amount=1.0)
        self.assertEqual(result.size, img.size)

    def test_sharpen_increases_edge_contrast(self) -> None:
        # Create an image with a sharp edge
        img = Image.new("RGB", (100, 100))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, 50, 100], fill=(100, 100, 100))
        draw.rectangle([50, 0, 100, 100], fill=(200, 200, 200))
        del draw

        result = sharpen(img, amount=1.5)

        # Check edge pixels: left side should get darker, right side lighter
        left_mean = np.mean(np.asarray(result)[:25, 25:75, 0])
        right_mean = np.mean(np.asarray(result)[75:, 25:75, 0])
        # After sharpening, contrast should increase
        self.assertGreater(right_mean - left_mean, 50)

    def test_sharpen_parameters_affect_strength(self) -> None:
        img = Image.new("RGB", (100, 100), 128)
        # Add noise
        arr = np.asarray(img).astype(np.float32)
        arr += np.random.randint(-20, 20, arr.shape, dtype=np.int32)
        img = Image.fromarray(arr.astype(np.uint8), "RGB")

        weak = sharpen(img, amount=0.5)
        strong = sharpen(img, amount=2.0)

        # Strong sharpening should produce more variation
        self.assertGreater(strong.getextrema()[1][0] - strong.getextrema()[0][0],
                          weak.getextrema()[1][0] - weak.getextrema()[0][0])


class EmbossTests(unittest.TestCase):
    """Verify emboss filter behavior."""

    def test_emboss_returns_same_size(self) -> None:
        img = Image.new("RGB", (120, 80), (100, 150, 200))
        result = emboss(img, intensity=1.0)
        self.assertEqual(result.size, img.size)

    def test_emboss_creates_3d_relief(self) -> None:
        # Create image with a clear shape
        img = Image.new("RGB", (100, 100))
        draw = ImageDraw.Draw(img)
        draw.ellipse([20, 20, 80, 80], fill=(200, 100, 100))
        del draw

        result = emboss(img, intensity=1.5)

        # Embossed image should have more variation in pixel values
        arr = np.asarray(result)
        self.assertGreater(arr.std(), 20)

    def test_emboss_angle_affects_lighting(self) -> None:
        img = Image.new("RGB", (100, 100), 128)
        draw = ImageDraw.Draw(img)
        draw.rectangle([25, 25, 75, 75], fill=(255, 255, 255))
        del draw

        left_lit = emboss(img, intensity=1.0, angle=0.0)   # light from right
        top_lit = emboss(img, intensity=1.0, angle=90.0)  # light from bottom

        # Light from right: left side of rectangle should be darker
        left_left = np.mean(np.asarray(left_lit)[30:70, 20:40, 0])
        left_right = np.mean(np.asarray(left_lit)[30:70, 60:80, 0])

        # Light from bottom: top side should be darker
        top_top = np.mean(np.asarray(top_lit)[20:40, 30:70, 0])
        top_bottom = np.mean(np.asarray(top_lit)[60:80, 30:70, 0])

        # Check that left_lit shows left-side darkening more than top_lit
        self.assertGreater(left_right - left_left, 10)


class VignetteTests(unittest.TestCase):
    """Verify vignette filter behavior."""

    def test_vignette_returns_same_size(self) -> None:
        img = Image.new("RGB", (120, 80), (100, 150, 200))
        result = vignette(img, strength=0.5)
        self.assertEqual(result.size, img.size)

    def test_vignette_darkens_corners(self) -> None:
        img = Image.new("RGB", (100, 100), (200, 200, 200))
        result = vignette(img, strength=0.8)

        arr = np.asarray(result)
        corners = np.concatenate([
            arr[:25, :25], arr[:25, -25:],
            arr[-25:, :25], arr[-25:, -25:],
        ])
        center = arr[25:75, 25:75]

        self.assertLess(corners.mean(), center.mean())

    def test_vignette_parameters_affect_strength_and_shape(self) -> None:
        img = Image.new("RGB", (100, 100), (200, 200, 200))

        weak_round = vignette(img, strength=0.3, roundness=1.0)
        strong_square = vignette(img, strength=0.7, roundness=0.3)

        weak_mean_corner = np.mean(np.asarray(weak_round)[:25, :25])
        strong_mean_corner = np.mean(np.asarray(strong_square)[:25, :25])

        self.assertLess(strong_mean_corner, weak_mean_corner)

if __name__ == "__main__":
    unittest.main()
