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

    def test_resize_image_supports_undo(self) -> None:
        self.assertTrue(self.window._resize_image(60, 40))
        self.assertEqual(self.window._orig.size, (60, 40))

        self.window._on_undo()
        self.assertEqual(self.window._orig.size, (120, 80))

    def test_resize_image_rejects_invalid_size(self) -> None:
        self.assertFalse(self.window._resize_image(0, 40))
        self.assertEqual(self.window._orig.size, (120, 80))

    def test_auto_enhance_is_undoable(self) -> None:
        before = self.window._orig.copy()

        self.window._on_auto_enhance()
        self.assertTrue(self.window._history.can_undo)

        self.window._on_undo()
        self.assertEqual(
            list(self.window._orig.getdata()),
            list(before.getdata()),
        )

    def test_spot_removal_heals_dot_and_supports_undo(self) -> None:
        from PySide6.QtCore import QPointF

        for dx in range(-4, 5):
            for dy in range(-4, 5):
                self.window._orig.putpixel((60 + dx, 40 + dy), (0, 0, 0))
        preview = self.window._preview_arr
        self.assertIsNotNone(preview)

        self.window._on_spot_click(QPointF(60.0, 40.0))

        healed = self.window._orig.getpixel((60, 40))
        self.assertGreater(healed[0], 150)

        self.window._on_undo()
        self.assertEqual(self.window._orig.getpixel((60, 40)), (0, 0, 0))


class MainWindowAdjUndoTests(unittest.TestCase):
    """Verify undo/redo covers slider adjustments."""

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

    def test_slider_change_is_undoable(self) -> None:
        from core.adjustments import Adjustments

        adj = Adjustments()
        adj.exposure = 2.5
        self.window._on_adj(adj)

        self.window._on_undo()
        self.assertEqual(self.window._adj.exposure, 0.0)

        self.window._on_redo()
        self.assertEqual(self.window._adj.exposure, 2.5)

    def test_rapid_slider_ticks_form_one_session(self) -> None:
        from core.adjustments import Adjustments

        for value in (0.5, 1.0, 1.5):
            adj = Adjustments()
            adj.exposure = value
            self.window._on_adj(adj)

        self.window._on_undo()
        self.assertEqual(self.window._adj.exposure, 0.0)
        self.assertFalse(self.window._adj_history.can_undo)

    def test_newest_action_wins_on_undo(self) -> None:
        from core.adjustments import Adjustments

        self.window._on_rotate(90)
        adj = Adjustments()
        adj.contrast = 40.0
        self.window._on_adj(adj)

        self.window._on_undo()
        self.assertEqual(self.window._adj.contrast, 0.0)
        self.assertEqual(self.window._orig.size, (80, 120))

        self.window._on_undo()
        self.assertEqual(self.window._orig.size, (120, 80))

    def test_load_clears_adjustment_history(self) -> None:
        from core.adjustments import Adjustments

        adj = Adjustments()
        adj.exposure = 1.0
        self.window._on_adj(adj)
        self.assertTrue(self.window._adj_history.can_undo)

        self.window._load(self.image_path)
        self.assertFalse(self.window._adj_history.can_undo)


class MainWindowBrushAndRecentTests(unittest.TestCase):
    """Verify dodge/burn brush, recent files and info text."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        from PySide6.QtCore import QSettings

        QSettings.setPath(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            tempfile.mkdtemp(),
        )
        self.window = MainWindow()
        self.tmp = tempfile.TemporaryDirectory()
        self.image_path = Path(self.tmp.name) / "photo.png"
        Image.new("RGB", (120, 80), (128, 128, 128)).save(self.image_path)
        self.window._load(self.image_path)

    def tearDown(self) -> None:
        self.window._worker.wait(2000)
        self.window.close()
        self.window.deleteLater()
        self.app.processEvents()
        self.tmp.cleanup()

    def test_brush_dodge_brightens_stroke_with_undo(self) -> None:
        from PySide6.QtCore import QPointF, Qt

        points = [QPointF(30.0 + i, 40.0) for i in range(20)]
        self.window._on_brush_stroke(points, Qt.MouseButton.LeftButton)

        self.assertGreater(self.window._orig.getpixel((40, 40))[0], 128)

        self.window._on_undo()
        self.assertEqual(self.window._orig.getpixel((40, 40))[0], 128)

    def test_brush_burn_darkens_stroke(self) -> None:
        from PySide6.QtCore import QPointF, Qt

        points = [QPointF(30.0 + i, 40.0) for i in range(20)]
        self.window._on_brush_stroke(points, Qt.MouseButton.RightButton)

        self.assertLess(self.window._orig.getpixel((40, 40))[0], 128)

    def test_recent_files_updated_on_load(self) -> None:
        entries = self.window._recent_list()

        self.assertIn(str(self.image_path), entries)
        self.assertEqual(entries[0], str(self.image_path))

    def test_open_recent_missing_file_shows_status(self) -> None:
        self.window._open_recent("/nie/istnieje/zdjecie.png")

        self.assertNotIn(
            "/nie/istnieje/zdjecie.png", self.window._recent_list()
        )

    def test_info_text_contains_dimensions_and_filename(self) -> None:
        text = self.window._build_info_text()

        self.assertIn("120 x 80", text)
        self.assertIn("photo.png", text)

    def test_overlay_layer_applies_and_supports_undo(self) -> None:
        layer = Image.new("RGB", (300, 300), (255, 255, 255))

        self.assertTrue(self.window.apply_overlay(layer, 1.0, "Normalny"))
        self.assertEqual(self.window._orig.getpixel((60, 40)), (255, 255, 255))

        self.window._on_undo()
        self.assertEqual(self.window._orig.getpixel((60, 40)), (128, 128, 128))

    def test_straighten_supports_undo(self) -> None:
        original_size = self.window._orig.size

        self.assertTrue(self.window.apply_straighten(15.0))
        self.assertNotEqual(self.window._orig.size, original_size)

        self.window._on_undo()
        self.assertEqual(self.window._orig.size, original_size)

    def test_watermark_applies_and_supports_undo(self) -> None:
        before = self.window._orig.copy()

        self.assertTrue(
            self.window.apply_watermark("TEST", "Prawy dolny rog", 1.0)
        )
        self.assertNotEqual(
            list(self.window._orig.getdata()),
            list(before.getdata()),
        )

        self.window._on_undo()
        self.assertEqual(
            list(self.window._orig.getdata()),
            list(before.getdata()),
        )


if __name__ == "__main__":
    unittest.main()
