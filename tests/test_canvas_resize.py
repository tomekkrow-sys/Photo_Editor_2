#!/usr/bin/env python3
"""Tests for image resizing in Canvas."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication

from core.canvas import Canvas


class CanvasResizeTests(unittest.TestCase):
    """Tests for resizing images and resize history."""

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

    def test_resize_changes_dimensions(self) -> None:
        self._load_test_image()

        self.assertTrue(
            self.canvas.resize_image(20, 10)
        )

        self.assertEqual(
            self.canvas.document.width,
            20,
        )
        self.assertEqual(
            self.canvas.document.height,
            10,
        )
        self.assertTrue(
            self.canvas.document.modified
        )

    def test_resize_undo_redo_restores_dimensions(self) -> None:
        self._load_test_image()

        self.assertTrue(
            self.canvas.resize_image(20, 10)
        )

        self.assertTrue(self.canvas.undo())
        self.assertEqual(
            (
                self.canvas.document.width,
                self.canvas.document.height,
            ),
            (40, 20),
        )

        self.assertTrue(self.canvas.redo())
        self.assertEqual(
            (
                self.canvas.document.width,
                self.canvas.document.height,
            ),
            (20, 10),
        )

    def test_resize_rejects_invalid_dimensions(self) -> None:
        self._load_test_image()

        self.assertFalse(
            self.canvas.resize_image(0, 10)
        )
        self.assertFalse(
            self.canvas.resize_image(10, 0)
        )
        self.assertFalse(
            self.canvas.resize_image(-1, 10)
        )

    def test_resize_without_image_returns_false(self) -> None:
        self.assertFalse(
            self.canvas.resize_image(20, 10)
        )


if __name__ == "__main__":
    unittest.main()