"""Unit tests for image history."""

from __future__ import annotations

import unittest

from PySide6.QtGui import QColor, QImage

from core.history import ImageHistory


class ImageHistoryTests(unittest.TestCase):
    """Verify independent QImage history states."""

    def _make_image(self, color: str, width: int = 4, height: int = 3) -> QImage:
        image = QImage(width, height, QImage.Format.Format_RGB32)
        image.fill(QColor(color))
        return image

    def test_push_undo_redo_uses_independent_copies(self) -> None:
        history = ImageHistory()

        first = self._make_image("red")
        history.push(first)
        first.fill(QColor("blue"))

        second = self._make_image("green")
        history.push(second)
        second.fill(QColor("yellow"))

        self.assertTrue(history.can_undo)
        self.assertFalse(history.can_redo)

        undo_image = history.undo()
        self.assertIsNotNone(undo_image)
        self.assertEqual(undo_image.pixelColor(0, 0).name(), "#ff0000")
        self.assertTrue(history.can_redo)

        redo_image = history.redo()
        self.assertIsNotNone(redo_image)
        self.assertEqual(redo_image.pixelColor(0, 0).name(), "#008000")
        self.assertTrue(history.can_undo)

    def test_clear_resets_history(self) -> None:
        history = ImageHistory()
        history.push(self._make_image("red"))
        history.push(self._make_image("green"))

        history.clear()

        self.assertFalse(history.can_undo)
        self.assertFalse(history.can_redo)
        self.assertIsNone(history.undo())
        self.assertIsNone(history.redo())


if __name__ == "__main__":
    unittest.main()
