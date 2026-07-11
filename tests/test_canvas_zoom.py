"""Unit tests for Canvas zoom behavior."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QImage, QWheelEvent
from PySide6.QtWidgets import QApplication

from core.canvas import Canvas


class CanvasZoomTests(unittest.TestCase):
    """Verify Canvas calculates and reports its actual zoom level."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.image_path = Path(self.temporary_directory.name) / "image.png"
        image = QImage(1200, 800, QImage.Format.Format_RGB32)
        image.fill(0)
        self.assertTrue(image.save(str(self.image_path)))

        self.canvas = Canvas()
        self.canvas.resize(400, 300)
        self.canvas.show()
        self.application.processEvents()
        self.assertTrue(self.canvas.load_image(self.image_path))

    def tearDown(self) -> None:
        self.canvas.close()
        self.temporary_directory.cleanup()

    def test_actual_size_sets_one_to_one_scale_and_reports_zoom(self) -> None:
        zoom_values: list[float] = []
        self.canvas.zoom_changed.connect(zoom_values.append)

        self.canvas.actual_size()

        self.assertEqual(self.canvas.transform().m11(), 1.0)
        self.assertEqual(self.canvas.document.zoom, 100.0)
        self.assertEqual(zoom_values[-1], 100.0)

    def test_fit_to_window_reports_transform_scale(self) -> None:
        self.canvas.fit_to_window()

        expected_zoom = self.canvas.transform().m11() * 100.0

        self.assertLess(expected_zoom, 100.0)
        self.assertAlmostEqual(self.canvas.document.zoom, expected_zoom)

    def test_relative_zoom_updates_document_from_transform(self) -> None:
        self.canvas.actual_size()
        self.canvas.zoom_in()

        expected_zoom = self.canvas.transform().m11() * 100.0

        self.assertAlmostEqual(self.canvas.document.zoom, expected_zoom)
        self.assertAlmostEqual(expected_zoom, 115.0)

    def test_ctrl_wheel_zooms_around_cursor(self) -> None:
        self.canvas.actual_size()

        self.canvas.wheelEvent(
            self._wheel_event(Qt.KeyboardModifier.ControlModifier)
        )

        self.assertAlmostEqual(self.canvas.transform().m11(), 1.15)

    def test_wheel_without_ctrl_does_not_change_zoom(self) -> None:
        self.canvas.actual_size()

        self.canvas.wheelEvent(
            self._wheel_event(Qt.KeyboardModifier.NoModifier)
        )

        self.assertEqual(self.canvas.transform().m11(), 1.0)

    @staticmethod
    def _wheel_event(modifiers: Qt.KeyboardModifier) -> QWheelEvent:
        return QWheelEvent(
            QPointF(200, 150),
            QPointF(200, 150),
            QPoint(),
            QPoint(0, 120),
            Qt.MouseButton.NoButton,
            modifiers,
            Qt.ScrollPhase.ScrollUpdate,
            False,
        )


if __name__ == "__main__":
    unittest.main()
