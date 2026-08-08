"""Unit tests for EditHistory (PIL undo/redo stacks)."""

from __future__ import annotations

import unittest

from PIL import Image

from core.history import EditHistory


class EditHistoryTests(unittest.TestCase):
    """Verify two-stack undo/redo semantics for PIL images."""

    def _make_image(self, color: tuple) -> Image.Image:
        return Image.new("RGB", (8, 6), color)

    def test_undo_redo_roundtrip(self) -> None:
        history = EditHistory()
        red = self._make_image((255, 0, 0))
        green = self._make_image((0, 128, 0))

        history.push(red)
        previous = history.undo(green)

        self.assertIsNotNone(previous)
        self.assertEqual(previous.getpixel((0, 0)), (255, 0, 0))
        self.assertTrue(history.can_redo)

        restored = history.redo(previous)
        self.assertIsNotNone(restored)
        self.assertEqual(restored.getpixel((0, 0)), (0, 128, 0))

    def test_push_stores_independent_copy(self) -> None:
        history = EditHistory()
        img = self._make_image((255, 0, 0))

        history.push(img)
        img.paste((0, 0, 255), (0, 0, 8, 6))

        previous = history.undo(self._make_image((1, 1, 1)))
        self.assertEqual(previous.getpixel((4, 3)), (255, 0, 0))

    def test_push_clears_redo(self) -> None:
        history = EditHistory()
        img = self._make_image((0, 0, 0))

        history.push(img)
        history.undo(self._make_image((9, 9, 9)))
        self.assertTrue(history.can_redo)

        history.push(self._make_image((5, 5, 5)))
        self.assertFalse(history.can_redo)

    def test_empty_stacks_return_none(self) -> None:
        history = EditHistory()
        img = self._make_image((0, 0, 0))

        self.assertIsNone(history.undo(img))
        self.assertIsNone(history.redo(img))
        self.assertFalse(history.can_undo)
        self.assertFalse(history.can_redo)

    def test_clear_resets(self) -> None:
        history = EditHistory()
        img = self._make_image((0, 0, 0))

        history.push(img)
        history.clear()

        self.assertFalse(history.can_undo)
        self.assertIsNone(history.undo(img))

    def test_limit_drops_oldest_states(self) -> None:
        history = EditHistory(limit=3)
        current = self._make_image((0, 0, 0))

        for value in range(1, 6):
            history.push(self._make_image((value, value, value)))

        for _ in range(3):
            current = history.undo(current)
            self.assertIsNotNone(current)

        self.assertFalse(history.can_undo)
        self.assertIsNone(history.undo(current))


if __name__ == "__main__":
    unittest.main()
