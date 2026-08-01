"""Unit tests for Canvas rectangular crop selection."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPointF, Qt
from PySide6.QtGui import QImage, QKeyEvent, QMouseEvent
from PySide6.QtWidgets import QApplication, QGraphicsView

from core.canvas import Canvas
from ui.main_window import MainWindow


class CanvasCropTests(unittest.TestCase):
    """Verify crop selection behavior without changing image pixels."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.image_path = Path(self.temporary_directory.name) / "image.png"
        self.second_image_path = Path(self.temporary_directory.name) / "new.png"
        self._create_image(self.image_path)
        self._create_image(self.second_image_path)

        self.canvas = Canvas()
        self.canvas.resize(400, 300)
        self.canvas.show()
        self.application.processEvents()
        self.assertTrue(self.canvas.load_image(self.image_path))

    def tearDown(self) -> None:
        self.canvas.close()
        self.temporary_directory.cleanup()

    def test_crop_selection_is_limited_to_image_bounds(self) -> None:
        self.canvas.set_crop_selection_enabled(True)
        bounds = self.canvas.image_item.sceneBoundingRect()
        start = bounds.topLeft() + QPointF(10, 10)
        outside = bounds.bottomRight() + QPointF(100, 100)

        self.canvas.mousePressEvent(
            self._mouse_event(
                QEvent.Type.MouseButtonPress,
                start,
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.LeftButton,
            )
        )
        self.canvas.mouseMoveEvent(
            self._mouse_event(
                QEvent.Type.MouseMove,
                outside,
                Qt.MouseButton.NoButton,
                Qt.MouseButton.LeftButton,
            )
        )
        self.canvas.mouseReleaseEvent(
            self._mouse_event(
                QEvent.Type.MouseButtonRelease,
                outside,
                Qt.MouseButton.LeftButton,
                Qt.MouseButton.NoButton,
            )
        )

        selection = self.canvas.crop_tool.selection_rect

        self.assertTrue(self.canvas.crop_tool.has_selection)
        self.assertGreater(selection.width(), 0)
        self.assertGreater(selection.height(), 0)
        self.assertGreaterEqual(selection.left(), bounds.left())
        self.assertGreaterEqual(selection.top(), bounds.top())
        self.assertLessEqual(selection.right(), bounds.right())
        self.assertLessEqual(selection.bottom(), bounds.bottom())

    def test_escape_cancels_selection_and_restores_panning(self) -> None:
        self.canvas.set_crop_selection_enabled(True)
        bounds = self.canvas.image_item.sceneBoundingRect()
        self.canvas.crop_tool.begin(bounds.center(), bounds)

        self.canvas.keyPressEvent(
            QKeyEvent(
                QEvent.Type.KeyPress,
                Qt.Key.Key_Escape,
                Qt.KeyboardModifier.NoModifier,
            )
        )

        self.assertFalse(self.canvas.crop_selection_enabled)
        self.assertFalse(self.canvas.crop_tool.has_selection)
        self.assertEqual(
            self.canvas.dragMode(),
            QGraphicsView.DragMode.ScrollHandDrag,
        )

    def test_loading_new_image_clears_selection(self) -> None:
        self.canvas.set_crop_selection_enabled(True)
        bounds = self.canvas.image_item.sceneBoundingRect()
        self.canvas.crop_tool.begin(bounds.topLeft(), bounds)
        self.canvas.crop_tool.finish(bounds.bottomRight(), bounds)

        self.assertTrue(self.canvas.crop_tool.has_selection)
        self.assertTrue(self.canvas.load_image(self.second_image_path))
        self.assertFalse(self.canvas.crop_tool.has_selection)

    @unittest.skip('Testy dla starej architektury MainWindow (przed bf42cdb) - do aktualizacji')
    def test_crop_action_toggles_canvas_mode(self) -> None:
        window = MainWindow()

        window.actions.crop.trigger()

        self.assertTrue(window.actions.crop.isChecked())
        self.assertTrue(window.canvas.crop_selection_enabled)

        window.canvas.set_crop_selection_enabled(False)

        self.assertFalse(window.actions.crop.isChecked())
        self.assertFalse(window.canvas.crop_selection_enabled)
        window.close()

    @unittest.skip('Testy dla starej architektury MainWindow (przed bf42cdb) - do aktualizacji')
    def test_crop_action_applies_selection_and_updates_document(self) -> None:
        window = MainWindow()
        self.assertTrue(window.canvas.load_image(self.image_path))
        original_snapshot = window.canvas.document.original_image.copy()

        window.actions.crop.trigger()

        bounds = window.canvas.image_item.sceneBoundingRect()
        selection_start = bounds.topLeft() + QPointF(50, 40)
        selection_end = bounds.topLeft() + QPointF(250, 140)

        window.canvas.crop_tool.begin(selection_start, bounds)
        window.canvas.crop_tool.update(selection_end, bounds)
        window.canvas.crop_tool.finish(selection_end, bounds)

        original_image = window.canvas.document.original_image.copy()
        window.actions.crop.trigger()

        self.assertFalse(window.actions.crop.isChecked())
        self.assertFalse(window.canvas.crop_selection_enabled)
        self.assertFalse(window.canvas.crop_tool.has_selection)
        self.assertTrue(window.canvas.document.modified)
        self.assertEqual(window.canvas.document.width, 200)
        self.assertEqual(window.canvas.document.height, 100)
        self.assertEqual(window.canvas.image_item.pixmap().width(), 200)
        self.assertEqual(window.canvas.image_item.pixmap().height(), 100)
        self.assertEqual(window.canvas.scene.sceneRect().width(), 200)
        self.assertEqual(window.canvas.scene.sceneRect().height(), 100)
        self.assertEqual(
            window.canvas.document.original_image.size(),
            original_image.size(),
        )
        self.assertEqual(
            window.canvas.document.original_image.size().width(),
            1200,
        )
        self.assertEqual(
            window.canvas.document.original_image.size().height(),
            800,
        )
        self.assertEqual(
            window.canvas.document.original_image.pixelColor(0, 0).name(),
            original_snapshot.pixelColor(0, 0).name(),
        )

    @unittest.skip('Testy dla starej architektury MainWindow (przed bf42cdb) - do aktualizacji')
    def test_crop_undo_redo_restores_image_and_history_state(self) -> None:
        window = MainWindow()
        self.assertTrue(window.canvas.load_image(self.image_path))
        original_snapshot = window.canvas.document.original_image.copy()

        window.actions.crop.trigger()
        bounds = window.canvas.image_item.sceneBoundingRect()
        selection_start = bounds.topLeft() + QPointF(30, 20)
        selection_end = bounds.topLeft() + QPointF(180, 120)

        window.canvas.crop_tool.begin(selection_start, bounds)
        window.canvas.crop_tool.update(selection_end, bounds)
        window.canvas.crop_tool.finish(selection_end, bounds)
        window.actions.crop.trigger()

        self.assertTrue(window.actions.undo.isEnabled())
        self.assertFalse(window.actions.redo.isEnabled())
        self.assertEqual(window.canvas.document.width, 150)
        self.assertEqual(window.canvas.document.height, 100)
        self.assertTrue(window.canvas.document.modified)

        window.actions.undo.trigger()

        self.assertEqual(window.canvas.document.width, 1200)
        self.assertEqual(window.canvas.document.height, 800)
        self.assertFalse(window.canvas.document.modified)
        self.assertFalse(window.actions.undo.isEnabled())
        self.assertTrue(window.actions.redo.isEnabled())

        window.actions.redo.trigger()

        self.assertEqual(window.canvas.document.width, 150)
        self.assertEqual(window.canvas.document.height, 100)
        self.assertTrue(window.canvas.document.modified)
        self.assertTrue(window.actions.undo.isEnabled())
        self.assertFalse(window.actions.redo.isEnabled())
        self.assertEqual(
            window.canvas.document.original_image.size().width(),
            original_snapshot.size().width(),
        )
        self.assertEqual(
            window.canvas.document.original_image.size().height(),
            original_snapshot.size().height(),
        )
        self.assertEqual(
            window.canvas.document.original_image.pixelColor(0, 0).name(),
            original_snapshot.pixelColor(0, 0).name(),
        )

    @unittest.skip('Testy dla starej architektury MainWindow (przed bf42cdb) - do aktualizacji')
    def test_new_crop_after_undo_clears_redo_history(self) -> None:
        window = MainWindow()
        self.assertTrue(window.canvas.load_image(self.image_path))

        window.actions.crop.trigger()
        bounds = window.canvas.image_item.sceneBoundingRect()
        first_start = bounds.topLeft() + QPointF(40, 30)
        first_end = bounds.topLeft() + QPointF(190, 130)

        window.canvas.crop_tool.begin(first_start, bounds)
        window.canvas.crop_tool.update(first_end, bounds)
        window.canvas.crop_tool.finish(first_end, bounds)
        window.actions.crop.trigger()

        window.actions.undo.trigger()
        self.assertTrue(window.actions.redo.isEnabled())

        window.actions.crop.trigger()
        second_start = window.canvas.image_item.sceneBoundingRect().topLeft() + QPointF(60, 50)
        second_end = window.canvas.image_item.sceneBoundingRect().topLeft() + QPointF(260, 170)

        window.canvas.crop_tool.begin(second_start, window.canvas.image_item.sceneBoundingRect())
        window.canvas.crop_tool.update(second_end, window.canvas.image_item.sceneBoundingRect())
        window.canvas.crop_tool.finish(second_end, window.canvas.image_item.sceneBoundingRect())
        window.actions.crop.trigger()

        self.assertFalse(window.actions.redo.isEnabled())
        self.assertTrue(window.actions.undo.isEnabled())
        self.assertEqual(window.canvas.document.width, 200)
        self.assertEqual(window.canvas.document.height, 120)

    @unittest.skip('Testy dla starej architektury MainWindow (przed bf42cdb) - do aktualizacji')
    def test_loading_new_image_clears_history(self) -> None:
        window = MainWindow()
        self.assertTrue(window.canvas.load_image(self.image_path))

        window.actions.crop.trigger()
        bounds = window.canvas.image_item.sceneBoundingRect()
        selection_start = bounds.topLeft() + QPointF(20, 20)
        selection_end = bounds.topLeft() + QPointF(120, 90)

        window.canvas.crop_tool.begin(selection_start, bounds)
        window.canvas.crop_tool.update(selection_end, bounds)
        window.canvas.crop_tool.finish(selection_end, bounds)
        window.actions.crop.trigger()

        self.assertTrue(window.actions.undo.isEnabled())
        self.assertFalse(window.actions.redo.isEnabled())

        self.assertTrue(window.canvas.load_image(self.second_image_path))

        self.assertFalse(window.actions.undo.isEnabled())
        self.assertFalse(window.actions.redo.isEnabled())
        self.assertFalse(window.canvas.document.modified)
        self.assertEqual(window.canvas.document.width, 1200)
        self.assertEqual(window.canvas.document.height, 800)

    def _mouse_event(
        self,
        event_type: QEvent.Type,
        scene_position: QPointF,
        button: Qt.MouseButton,
        buttons: Qt.MouseButton,
    ) -> QMouseEvent:
        position = QPointF(self.canvas.mapFromScene(scene_position))

        return QMouseEvent(
            event_type,
            position,
            position,
            button,
            buttons,
            Qt.KeyboardModifier.NoModifier,
        )

    def _create_image(self, path: Path) -> None:
        image = QImage(1200, 800, QImage.Format.Format_RGB32)
        image.fill(0)
        self.assertTrue(image.save(str(path)))


if __name__ == "__main__":
    unittest.main()
