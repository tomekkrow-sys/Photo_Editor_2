"""Tests for the pencil sketch filter."""

from __future__ import annotations

import unittest

import numpy as np
from PIL import Image

from core.filters import pencil_sketch


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
        img = Image.new("RGB", (100, 100), 255)
        for x in range(50):
            for y in range(100):
                img.putpixel((x, y), (0, 0, 0))

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


if __name__ == "__main__":
    unittest.main()
