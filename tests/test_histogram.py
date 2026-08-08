"""Tests for the histogram widget luminance channel."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
from PIL import Image
from PySide6.QtWidgets import QApplication

from ui.histogram import HistogramWidget


class HistogramLuminanceTests(unittest.TestCase):
    """Verify luminance histogram has no uint8 overflow (regression)."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_gray_200_peaks_at_200_not_overflow(self) -> None:
        widget = HistogramWidget()
        img = Image.new("RGB", (50, 50), (200, 200, 200))

        widget.set_image(img)

        self.assertEqual(int(np.argmax(widget._hist_l)), 200)

    def test_rgb_channels_peak_at_channel_value(self) -> None:
        widget = HistogramWidget()
        img = Image.new("RGB", (50, 50), (10, 128, 250))

        widget.set_image(img)

        self.assertEqual(int(np.argmax(widget._hist_r)), 10)
        self.assertEqual(int(np.argmax(widget._hist_g)), 128)
        self.assertEqual(int(np.argmax(widget._hist_b)), 250)


if __name__ == "__main__":
    unittest.main()
