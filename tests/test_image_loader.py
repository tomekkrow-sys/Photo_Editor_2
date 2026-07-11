"""Unit tests for image loading."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PySide6.QtGui import QImage

from core.image_loader import ImageLoader


class ImageLoaderTests(unittest.TestCase):
    """Verify supported formats and image loading errors."""

    def test_recognizes_supported_extensions(self) -> None:
        for extension in (".jpg", ".jpeg", ".png", ".webp", ".nef"):
            with self.subTest(extension=extension):
                self.assertTrue(
                    ImageLoader.is_supported(f"image{extension}")
                )

    def test_rejects_unsupported_extension(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "image.gif"
            path.write_text("not an image", encoding="utf-8")

            self.assertFalse(ImageLoader.is_supported(path))

            with self.assertRaises(ValueError):
                ImageLoader.load(path)

    def test_loads_valid_temporary_png(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "image.png"
            image = QImage(4, 3, QImage.Format.Format_RGB32)
            image.fill(0)

            self.assertTrue(image.save(str(path)))

            document = ImageLoader.load(path)

            self.assertTrue(document.is_loaded)
            self.assertEqual((document.width, document.height), (4, 3))
            self.assertEqual(document.format, "png")
            self.assertEqual(document.file_path, path)
            self.assertFalse(document.modified)

    def test_raises_for_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing-image.png"

            with self.assertRaises(FileNotFoundError):
                ImageLoader.load(path)

    def test_rejects_invalid_image_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "damaged.png"
            path.write_text("this is not a PNG file", encoding="utf-8")

            with self.assertRaises(ValueError):
                ImageLoader.load(path)


if __name__ == "__main__":
    unittest.main()
