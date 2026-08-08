"""Tests for the pencil sketch filter."""

from __future__ import annotations

import unittest

import numpy as np
from PIL import Image

from core.filters import black_and_white, pencil_sketch


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


if __name__ == "__main__":
    unittest.main()
