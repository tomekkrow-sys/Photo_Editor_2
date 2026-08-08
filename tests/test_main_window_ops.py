"""Tests for MainWindow save and undo/redo operations (new architecture)."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PIL import Image
from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


class MainWindowOpsTests(unittest.TestCase):
    """Verify load -> edit -> undo/redo -> save flow."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.window = MainWindow()
        self.tmp = tempfile.TemporaryDirectory()
        self.image_path = Path(self.tmp.name) / "photo.png"
        Image.new("RGB", (120, 80), (200, 120, 60)).save(self.image_path)
        self.window._load(self.image_path)

    def tearDown(self) -> None:
        self.window._worker.wait(2000)
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.tmp.cleanup()

    def test_loads_image(self) -> None:
        self.assertIsNotNone(self.window._orig)
        self.assertEqual(self.window._orig.size, (120, 80))
        self.assertEqual(self.window._path, self.image_path)

    def test_rotate_undo_redo_restores_dimensions(self) -> None:
        self.window._on_rotate(90)
        self.assertEqual(self.window._orig.size, (80, 120))

        self.window._on_undo()
        self.assertEqual(self.window._orig.size, (120, 80))

        self.window._on_redo()
        self.assertEqual(self.window._orig.size, (80, 120))

    def test_flip_undo_restores_pixels(self) -> None:
        original_pixel = self.window._orig.getpixel((0, 0))

        self.window._on_flip(True, False)
        self.window._on_undo()

        self.assertEqual(self.window._orig.getpixel((0, 0)), original_pixel)

    def test_new_edit_clears_redo(self) -> None:
        self.window._on_rotate(90)
        self.window._on_undo()
        self.assertTrue(self.window._history.can_redo)

        self.window._on_flip(True, False)
        self.assertFalse(self.window._history.can_redo)

    def test_loading_new_image_clears_history(self) -> None:
        self.window._on_rotate(90)
        self.assertTrue(self.window._history.can_undo)

        second = Path(self.tmp.name) / "second.png"
        Image.new("RGB", (50, 50), (10, 10, 10)).save(second)
        self.window._load(second)

        self.assertFalse(self.window._history.can_undo)
        self.assertFalse(self.window._history.can_redo)

    def test_new_creates_blank_image(self) -> None:
        self.window._on_new()

        self.assertIsNotNone(self.window._orig)
        self.assertEqual(self.window._orig.size, (1920, 1080))
        self.assertIsNone(self.window._path)

    def test_save_to_writes_png(self) -> None:
        out = Path(self.tmp.name) / "out.png"

        self.assertTrue(self.window._save_to(str(out)))
        self.assertTrue(out.exists())

        saved = Image.open(out)
        self.assertEqual(saved.size, (120, 80))

    def test_save_to_writes_jpeg(self) -> None:
        out = Path(self.tmp.name) / "out.jpg"

        self.assertTrue(self.window._save_to(str(out)))
        self.assertTrue(out.exists())

    def test_save_applies_adjustments(self) -> None:
        out = Path(self.tmp.name) / "adjusted.png"
        self.window._adj.exposure = 80.0

        self.assertTrue(self.window._save_to(str(out)))

        saved = Image.open(out).convert("RGB")
        original = Image.open(self.image_path).convert("RGB")
        self.assertGreater(
            saved.getpixel((60, 40))[0],
            original.getpixel((60, 40))[0],
        )

    def test_copy_paste_roundtrip(self) -> None:
        from PySide6.QtGui import QGuiApplication

        self.window._on_copy()
        self.assertFalse(QGuiApplication.clipboard().image().isNull())

        self.window._on_new()
        self.assertEqual(self.window._orig.size, (1920, 1080))

        self.window._on_paste()
        self.assertEqual(self.window._orig.size, (120, 80))
        self.assertIsNone(self.window._path)
        self.assertFalse(self.window._history.can_undo)

    def test_cut_clears_editor_but_keeps_clipboard(self) -> None:
        from PySide6.QtGui import QGuiApplication

        self.window._on_cut()

        self.assertIsNone(self.window._orig)
        self.assertFalse(QGuiApplication.clipboard().image().isNull())
        self.assertTrue(self.image_path.exists())

    def test_delete_clears_editor_and_keeps_file(self) -> None:
        self.window._on_delete()

        self.assertIsNone(self.window._orig)
        self.assertTrue(self.image_path.exists())

    def test_paste_with_empty_clipboard_does_not_crash(self) -> None:
        from PySide6.QtGui import QGuiApplication

        QGuiApplication.clipboard().clear()
        self.window._on_paste()

        self.assertEqual(self.window._orig.size, (120, 80))


if __name__ == "__main__":
    unittest.main()
