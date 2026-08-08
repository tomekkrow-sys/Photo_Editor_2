"""Tests for pil_to_qpixmap mode handling."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtWidgets import QApplication

from core.pipeline import pil_to_qimage, pil_to_qpixmap, qimage_to_pil


class PilToQPixmapTests(unittest.TestCase):
    """Verify conversion works for common PIL image modes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def _check(self, mode: str) -> None:
        img = Image.new(mode, (16, 12))

        pixmap = pil_to_qpixmap(img)

        self.assertFalse(pixmap.isNull(), f"mode {mode}")
        self.assertEqual(pixmap.width(), 16)
        self.assertEqual(pixmap.height(), 12)

    def test_rgb(self) -> None:
        self._check("RGB")

    def test_rgba(self) -> None:
        self._check("RGBA")

    def test_grayscale(self) -> None:
        self._check("L")

    def test_grayscale_alpha(self) -> None:
        self._check("LA")

    def test_palette(self) -> None:
        self._check("P")


class PilQImageRoundtripTests(unittest.TestCase):
    """Verify PIL <-> QImage conversion preserves pixels."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_roundtrip_preserves_pixels(self) -> None:
        img = Image.new("RGB", (8, 6))
        img.putpixel((3, 2), (10, 200, 90))

        result = qimage_to_pil(pil_to_qimage(img))

        self.assertEqual(result.mode, "RGB")
        self.assertEqual(result.size, (8, 6))
        self.assertEqual(result.getpixel((3, 2)), (10, 200, 90))


if __name__ == "__main__":
    unittest.main()
