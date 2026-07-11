#!/usr/bin/env python3
"""Tests for MainWindow save and unsaved-change handling."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication, QMessageBox

from ui.main_window import MainWindow


class MainWindowTests(unittest.TestCase):
    """Tests for main window document handling."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self.window = MainWindow()

    def tearDown(self) -> None:
        self.window.deleteLater()
        self.app.processEvents()

    def _create_image(self, path: Path) -> None:
        image = QImage(
            40,
            30,
            QImage.Format.Format_RGB32,
        )
        image.fill(0xFFFFFFFF)
        self.assertTrue(image.save(str(path)))

    def test_suggests_edited_copy_for_standard_image(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "photo.jpg"
            self._create_image(source)

            self.assertTrue(
                self.window.canvas.load_image(str(source))
            )

            suggested = self.window._suggest_save_path()

            self.assertEqual(
                suggested,
                Path(directory) / "photo_edited.jpg",
            )

    def test_suggests_jpg_copy_for_raw_image(self) -> None:
        self.window.canvas.document.file_path = Path(
            "/tmp/photo.nef"
        )

        suggested = self.window._suggest_save_path()

        self.assertEqual(
            suggested,
            Path("/tmp/photo_edited.jpg"),
        )

    def test_cancel_keeps_unsaved_document(self) -> None:
        self.window.canvas.document.modified = True

        with patch.object(
            QMessageBox,
            "warning",
            return_value=QMessageBox.StandardButton.Cancel,
        ):
            result = self.window._confirm_discard_changes()

        self.assertFalse(result)

    def test_discard_allows_operation(self) -> None:
        self.window.canvas.document.modified = True

        with patch.object(
            QMessageBox,
            "warning",
            return_value=QMessageBox.StandardButton.Discard,
        ):
            result = self.window._confirm_discard_changes()

        self.assertTrue(result)

    def test_save_choice_uses_save_method(self) -> None:
        self.window.canvas.document.modified = True

        with (
            patch.object(
                QMessageBox,
                "warning",
                return_value=QMessageBox.StandardButton.Save,
            ),
            patch.object(
                self.window,
                "_save_image",
                return_value=True,
            ) as save_mock,
        ):
            result = self.window._confirm_discard_changes()

        self.assertTrue(result)
        save_mock.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()