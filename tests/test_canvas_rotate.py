#!/usr/bin/env python3
"""Tests for image rotation in Canvas."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from core.canvas import Canvas


class CanvasRotateTests(unittest.TestCase):
    """Tests for rotating images and rotation history."""

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
            40,
            20,
            QImage.Format.Format_RGB32,
        )
        image.fill(0xFFFFFFFF)

        self.assertTrue(image.save(str(path)))
        self.assertTrue(self.canvas.load_image(path))

    def test_rotate_right_swaps_dimensions(self) -> None:
        self._load_test_image()

        self.assertTrue(self.canvas.rotate_right())

        self.assertEqual(self.canvas.document.width, 20)
        self.assertEqual(self.canvas.document.height, 40)
        self.assertTrue(self.canvas.document.modified)

    def test_rotate_left_swaps_dimensions(self) -> None:
        self._load_test_image()

        self.assertTrue(self.canvas.rotate_left())

        self.assertEqual(self.canvas.document.width, 20)
        self.assertEqual(self.canvas.document.height, 40)
        self.assertTrue(self.canvas.document.modified)

    def test_rotate_undo_redo_restores_dimensions(self) -> None:
        self._load_test_image()

        self.assertTrue(self.canvas.rotate_right())
        self.assertEqual(
            (self.canvas.document.width, self.canvas.document.height),
            (20, 40),
        )

        self.assertTrue(self.canvas.undo())
        self.assertEqual(
            (self.canvas.document.width, self.canvas.document.height),
            (40, 20),
        )

        self.assertTrue(self.canvas.redo())
        self.assertEqual(
            (self.canvas.document.width, self.canvas.document.height),
            (20, 40),
        )

    def test_rotate_without_image_returns_false(self) -> None:
        self.assertFalse(self.canvas.rotate_left())
        self.assertFalse(self.canvas.rotate_right())


if __name__ == "__main__":
    unittest.main()