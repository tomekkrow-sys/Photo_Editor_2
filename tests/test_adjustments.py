#!/usr/bin/env python3
"""Tests for image brightness and contrast adjustments."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication

from core.adjustments import ImageAdjustments
from core.canvas import Canvas


class ImageAdjustmentsTests(unittest.TestCase):
    """Tests for brightness and contrast operations."""

    def setUp(self) -> None:
        self.image = QImage(
            2,
            2,
            QImage.Format.Format_RGBA8888,
        )
        self.image.fill(QColor(100, 100, 100, 255))

    def test_zero_adjustments_preserve_pixels(self) -> None:
        result = ImageAdjustments.apply(
            self.image,
            brightness=0,
            contrast=0,
        )

        self.assertEqual(
            result.pixelColor(0, 0),
            QColor(100, 100, 100, 255),
        )

    def test_positive_brightness_increases_values(self) -> None:
        result = ImageAdjustments.apply(
            self.image,
            brightness=20,
        )

        self.assertGreater(
            result.pixelColor(0, 0).red(),
            100,
        )

    def test_negative_brightness_decreases_values(self) -> None:
        result = ImageAdjustments.apply(
            self.image,
            brightness=-20,
        )

        self.assertLess(
            result.pixelColor(0, 0).red(),
            100,
        )

    def test_positive_saturation_increases_color_difference(
        self,
    ) -> None:
        self.image.fill(QColor(180, 100, 80, 255))

        result = ImageAdjustments.apply(
            self.image,
            saturation=50,
        )

        original = self.image.pixelColor(0, 0)
        adjusted = result.pixelColor(0, 0)

        original_difference = (
            original.red() - original.blue()
        )
        adjusted_difference = (
            adjusted.red() - adjusted.blue()
        )

        self.assertGreater(
            adjusted_difference,
            original_difference,
        )

    def test_negative_saturation_reduces_color_difference(
        self,
    ) -> None:
        self.image.fill(QColor(180, 100, 80, 255))

        result = ImageAdjustments.apply(
            self.image,
            saturation=-100,
        )

        color = result.pixelColor(0, 0)

        self.assertAlmostEqual(
            color.red(),
            color.green(),
            delta=1,
        )
        self.assertAlmostEqual(
            color.green(),
            color.blue(),
            delta=1,
        )

    def test_adjustments_preserve_alpha(self) -> None:
        self.image.setPixelColor(
            0,
            0,
            QColor(100, 100, 100, 123),
        )

        result = ImageAdjustments.apply(
            self.image,
            brightness=20,
            contrast=20,
        )

        self.assertEqual(
            result.pixelColor(0, 0).alpha(),
            123,
        )
    def test_positive_temperature_warms_image(self) -> None:
        result = ImageAdjustments.apply(
            self.image,
            temperature=50,
        )

        color = result.pixelColor(0, 0)

        self.assertGreater(color.red(), 100)
        self.assertLess(color.blue(), 100)

    def test_negative_temperature_cools_image(self) -> None:
        result = ImageAdjustments.apply(
            self.image,
            temperature=-50,
        )

        color = result.pixelColor(0, 0)

        self.assertLess(color.red(), 100)
        self.assertGreater(color.blue(), 100)

class CanvasAdjustmentsTests(unittest.TestCase):
    """Tests for applying adjustments through Canvas."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.canvas = Canvas()

        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        path = Path(self.temp_dir.name) / "test.png"

        image = QImage(
            10,
            10,
            QImage.Format.Format_RGB32,
        )
        image.fill(QColor(100, 100, 100))

        self.assertTrue(image.save(str(path)))
        self.assertTrue(self.canvas.load_image(path))

    def tearDown(self) -> None:
        self.canvas.deleteLater()
        self.app.processEvents()

    def test_apply_adjustments_changes_image(self) -> None:
        original = self.canvas.document.image.copy()

        self.assertTrue(
            self.canvas.apply_adjustments(20, 10)
        )

        self.assertNotEqual(
            self.canvas.document.image,
            original,
        )

    def test_zero_adjustments_return_false(self) -> None:
        self.assertFalse(
            self.canvas.apply_adjustments(0, 0)
        )

    def test_adjustments_support_undo_redo(self) -> None:
        original = self.canvas.document.image.copy()

        self.assertTrue(
            self.canvas.apply_adjustments(20, 10)
        )

        adjusted = self.canvas.document.image.copy()

        self.assertTrue(self.canvas.undo())
        self.assertEqual(
            self.canvas.document.image,
            original,
        )

        self.assertTrue(self.canvas.redo())
        self.assertEqual(
            self.canvas.document.image,
            adjusted,
        )


if __name__ == "__main__":
    unittest.main()
