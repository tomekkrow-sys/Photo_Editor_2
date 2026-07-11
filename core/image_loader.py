#!/usr/bin/env python3
"""
Photo Editor 2.0

Image Loader

Version: 0.1.0
"""

from __future__ import annotations

from pathlib import Path

import rawpy

from PySide6.QtGui import QImage

from core.image_document import ImageDocument


class ImageLoader:
    """
    Loads images into ImageDocument.
    """

    STANDARD_EXTENSIONS = {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tif",
        ".tiff",
        ".webp",
    }

    RAW_EXTENSIONS = {
        ".nef",
        ".cr2",
        ".cr3",
        ".arw",
        ".dng",
        ".orf",
        ".rw2",
        ".raf",
        ".pef",
    }

    SUPPORTED_EXTENSIONS = STANDARD_EXTENSIONS | RAW_EXTENSIONS

    @classmethod
    def is_supported(cls, file_path: str | Path) -> bool:
        """Return whether a file extension is supported."""

        return Path(file_path).suffix.lower() in cls.SUPPORTED_EXTENSIONS

    @classmethod
    def can_load(cls, file_path: str | Path) -> bool:
        """Return whether a local, supported image file can be loaded."""

        path = Path(file_path)
        return path.is_file() and cls.is_supported(path)

    @classmethod
    def file_dialog_filter(cls) -> str:
        """Return the image filter used by open-file dialogs."""

        standard = " ".join(
            f"*{extension}"
            for extension in sorted(cls.STANDARD_EXTENSIONS)
        )
        raw = " ".join(
            f"*{extension}"
            for extension in sorted(cls.RAW_EXTENSIONS)
        )

        return (
            f"Wszystkie obsługiwane obrazy ({standard} {raw});;"
            f"Obrazy ({standard});;"
            f"RAW ({raw})"
        )

    @classmethod
    def load(cls, file_path: str | Path) -> ImageDocument:

        path = Path(file_path)

        if not path.is_file():
            raise FileNotFoundError(path)

        extension = path.suffix.lower()

        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported format: {path.suffix}"
            )

        if extension in cls.RAW_EXTENSIONS:
            image = cls._load_raw_image(path)
        else:
            image = QImage(str(path))

        if image.isNull():
            raise ValueError(
                f"Cannot load image: {path}"
            )

        document = ImageDocument()

        document.load(
            image=image,
            file_path=path,
        )

        return document

    @staticmethod
    def _load_raw_image(path: Path) -> QImage:
        """Decode a RAW image and convert it to an RGB QImage."""

        try:
            with rawpy.imread(str(path)) as raw:
                rgb = raw.postprocess(
                    use_camera_wb=True,
                    no_auto_bright=False,
                    output_bps=8,
                )

            height, width, channels = rgb.shape

            if channels != 3:
                return QImage()

            image = QImage(
                rgb.data,
                width,
                height,
                width * channels,
                QImage.Format.Format_RGB888,
            )

            return image.copy()

        except (
            rawpy.LibRawError,
            OSError,
            ValueError,
        ):
            return QImage()
