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

    def test_edges_produce_dark_strokes_on_white_paper(self) -> None:
        from PIL import ImageDraw, ImageFilter

        img = Image.new("RGB", (300, 200))
        draw = ImageDraw.Draw(img)
        for x in range(300):
            value = int(255 * x / 300)
            draw.line([(x, 0), (x, 200)], fill=(value, value, value))
        draw.ellipse([60, 40, 160, 160], fill=(30, 30, 40))
        img = img.filter(ImageFilter.GaussianBlur(2))

        result = np.asarray(pencil_sketch(img))

        self.assertLess(int(result.min()), 128)
        self.assertGreater(float(result.mean()), 200.0)

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
        self.assertGreater(int(result.max()) - int(result.min()), 60)


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


if __name__ == "__main__":
    unittest.main()
