#!/usr/bin/env python3
"""Fast image brightness, contrast, and saturation adjustments."""

from __future__ import annotations

import numpy as np

from PySide6.QtGui import QImage

from core.adjustment_settings import AdjustmentSettings
from core.tone_mapping import ToneMapping


class ImageAdjustments:
    """Apply fast pixel adjustments using NumPy."""


    @staticmethod
    def apply_settings(
        image: QImage,
        settings: AdjustmentSettings,
    ) -> QImage:
        """Apply adjustments from AdjustmentSettings."""

        return ImageAdjustments.apply(
            image=image,
            exposure=settings.exposure,
            brightness=settings.brightness,
            contrast=settings.contrast,
            saturation=settings.saturation,
            temperature=settings.temperature,
            tint=settings.tint,
        )

    @staticmethod
    def apply(
        image: QImage,
        exposure: int = 0,
        brightness: int = 0,
        contrast: int = 0,
        saturation: int = 0,
        temperature: int = 0,
        tint: int = 0,
    ) -> QImage:
        """Apply image adjustments in a single operation."""

        if image.isNull():
            return QImage()

        exposure = max(-100, min(100, exposure))
        brightness = max(-100, min(100, brightness))
        contrast = max(-100, min(100, contrast))
        saturation = max(-100, min(100, saturation))
        temperature = max(-100, min(100, temperature))
        tint = max(-100, min(100, tint))

        settings = AdjustmentSettings(
            exposure=exposure,
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
            temperature=temperature,
            tint=tint,
        )

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

        rgb = ToneMapping.apply(
            rgb,
            settings,
        )

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

        if temperature != 0:
            temperature_offset = temperature * 1.2

            rgb[:, :, 0] += temperature_offset
            rgb[:, :, 2] -= temperature_offset

        if tint != 0:
            tint_offset = tint * 1.2

            rgb[:, :, 1] += tint_offset
            rgb[:, :, 0] -= tint_offset * 0.5
            rgb[:, :, 2] -= tint_offset * 0.5

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
    def tint(
        image: QImage,
        value: int,
    ) -> QImage:
        """Adjust image tint."""

        return ImageAdjustments.apply(
            image,
            tint=value,
        )

    @staticmethod
    def temperature(
        image: QImage,
        value: int,
    ) -> QImage:
        """Adjust image color temperature."""

        return ImageAdjustments.apply(
            image,
            temperature=value,
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
