#!/usr/bin/env python3
"""Tests for ImageSaver."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PySide6.QtGui import QImage

from core.image_saver import ImageSaver


class ImageSaverTests(unittest.TestCase):
    """Tests for supported image saving."""

    def test_recognizes_supported_extensions(self) -> None:
        supported = (
            "image.jpg",
            "image.jpeg",
            "image.png",
            "image.webp",
            "image.bmp",
            "image.tif",
            "image.tiff",
        )

        for file_name in supported:
            with self.subTest(file_name=file_name):
                self.assertTrue(
                    ImageSaver.can_save(file_name)
                )

    def test_rejects_raw_and_unsupported_extensions(self) -> None:
        unsupported = (
            "image.nef",
            "image.cr2",
            "image.arw",
            "image.raw",
            "image.txt",
        )

        for file_name in unsupported:
            with self.subTest(file_name=file_name):
                self.assertFalse(
                    ImageSaver.can_save(file_name)
                )

    def test_saves_valid_png(self) -> None:
        image = QImage(
            20,
            10,
            QImage.Format.Format_RGB32,
        )
        image.fill(0xFFFFFFFF)

        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "test.png"

            result = ImageSaver.save(
                image,
                file_path,
            )

            self.assertTrue(result)
            self.assertTrue(file_path.exists())

            saved_image = QImage(str(file_path))

            self.assertFalse(saved_image.isNull())
            self.assertEqual(saved_image.width(), 20)
            self.assertEqual(saved_image.height(), 10)

    def test_rejects_null_image(self) -> None:
        image = QImage()

        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "test.png"

            self.assertFalse(
                ImageSaver.save(image, file_path)
            )

    def test_rejects_unsupported_output_format(self) -> None:
        image = QImage(
            10,
            10,
            QImage.Format.Format_RGB32,
        )

        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "test.nef"

            self.assertFalse(
                ImageSaver.save(image, file_path)
            )


if __name__ == "__main__":
    unittest.main()