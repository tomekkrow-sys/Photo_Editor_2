#!/usr/bin/env python3
"""Tests for image flipping in Canvas."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QColor, QImage
from PySide6.QtWidgets import QApplication

from core.canvas import Canvas


class CanvasFlipTests(unittest.TestCase):
    """Tests for horizontal and vertical image flipping."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.canvas = Canvas()

    def tearDown(self) -> None:
        self.canvas.deleteLater()
        self.app.processEvents()

    def _load_test_image(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        path = Path(self.temp_dir.name) / "test.png"

        image = QImage(
            2,
            2,
            QImage.Format.Format_RGB32,
        )

        image.setPixelColor(0, 0, QColor("red"))
        image.setPixelColor(1, 0, QColor("green"))
        image.setPixelColor(0, 1, QColor("blue"))
        image.setPixelColor(1, 1, QColor("white"))

        self.assertTrue(image.save(str(path)))
        self.assertTrue(self.canvas.load_image(path))

    def test_flip_horizontal(self) -> None:
        self._load_test_image()

        self.assertTrue(self.canvas.flip_horizontal())

        image = self.canvas.document.active_image

        self.assertEqual(
            image.pixelColor(0, 0),
            QColor("green"),
        )
        self.assertEqual(
            image.pixelColor(1, 0),
            QColor("red"),
        )

    def test_flip_vertical(self) -> None:
        self._load_test_image()

        self.assertTrue(self.canvas.flip_vertical())

        image = self.canvas.document.active_image

        self.assertEqual(
            image.pixelColor(0, 0),
            QColor("blue"),
        )
        self.assertEqual(
            image.pixelColor(0, 1),
            QColor("red"),
        )

    def test_flip_undo_redo(self) -> None:
        self._load_test_image()

        original = self.canvas.document.active_image.copy()

        self.assertTrue(self.canvas.flip_horizontal())
        flipped = self.canvas.document.active_image.copy()

        self.assertTrue(self.canvas.undo())
        self.assertEqual(
            self.canvas.document.active_image,
            original,
        )

        self.assertTrue(self.canvas.redo())
        self.assertEqual(
            self.canvas.document.active_image,
            flipped,
        )

    def test_flip_without_image_returns_false(self) -> None:
        self.assertFalse(self.canvas.flip_horizontal())
        self.assertFalse(self.canvas.flip_vertical())


if __name__ == "__main__":
    unittest.main()