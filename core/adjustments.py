#!/usr/bin/env python3
"""Fast image brightness, contrast, and saturation adjustments."""

from __future__ import annotations

import numpy as np

from PySide6.QtGui import QImage


class ImageAdjustments:
    """Apply fast pixel adjustments using NumPy."""

    @staticmethod
    def apply(
        image: QImage,
        brightness: int = 0,
        contrast: int = 0,
        saturation: int = 0,
    ) -> QImage:
        """Apply image adjustments in a single operation."""

        if image.isNull():
            return QImage()

        brightness = max(-100, min(100, brightness))
        contrast = max(-100, min(100, contrast))
        saturation = max(-100, min(100, saturation))

        result = image.convertToFormat(
            QImage.Format.Format_RGBA8888
        )

        width = result.width()
        height = result.height()
        bytes_per_line = result.bytesPerLine()

        buffer = result.bits()
        array = np.frombuffer(
            buffer,
            dtype=np.uint8,
            count=height * bytes_per_line,
        ).reshape(
            height,
            bytes_per_line,
        )

        pixels = array[:, : width * 4].reshape(
            height,
            width,
            4,
        )

        rgb = pixels[:, :, :3].astype(np.float32)

        if brightness != 0:
            rgb += brightness * 2.55

        if contrast != 0:
            factor = (
                259.0 * (contrast + 255.0)
                / (255.0 * (259.0 - contrast))
            )
            rgb = factor * (rgb - 128.0) + 128.0

        if saturation != 0:
            saturation_factor = 1.0 + saturation / 100.0

            luminance = (
                rgb[:, :, 0:1] * 0.2126
                + rgb[:, :, 1:2] * 0.7152
                + rgb[:, :, 2:3] * 0.0722
            )

            rgb = (
                luminance
                + saturation_factor * (rgb - luminance)
            )

        pixels[:, :, :3] = np.clip(
            rgb,
            0,
            255,
        ).astype(np.uint8)

        return result

    @staticmethod
    def brightness(
        image: QImage,
        value: int,
    ) -> QImage:
        """Adjust image brightness."""

        return ImageAdjustments.apply(
            image,
            brightness=value,
        )

    @staticmethod
    def contrast(
        image: QImage,
        value: int,
    ) -> QImage:
        """Adjust image contrast."""

        return ImageAdjustments.apply(
            image,
            contrast=value,
        )

    @staticmethod
    def saturation(
        image: QImage,
        value: int,
    ) -> QImage:
        """Adjust image saturation."""

        return ImageAdjustments.apply(
            image,
            saturation=value,
        )
