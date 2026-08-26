#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass

import numpy as np

from PySide6.QtGui import QImage

from core.adjustment_settings import AdjustmentSettings
from core.tone_mapping import ToneMapping

@dataclass
class Adjustments:
    exposure:    float = 0.0
    contrast:    float = 0.0
    highlights:  float = 0.0
    shadows:     float = 0.0
    whites:      float = 0.0
    blacks:      float = 0.0
    temperature: float = 0.0
    tint:        float = 0.0
    saturation:  float = 0.0
    vibrance:    float = 0.0
    sharpness:   float = 0.0
    clarity:     float = 0.0
    tone_curve:  list[tuple[int, int]] | None = None
    shadows_color: tuple[int, int, int] | None = None
    midtones_color: tuple[int, int, int] | None = None
    highlights_color: tuple[int, int, int] | None = None
    hsl_shadows: dict[str, float] | None = None
    hsl_midtones: dict[str, float] | None = None
    hsl_highlights: dict[str, float] | None = None
    bw_mix: dict[str, float] | None = None
    bw_grain: float = 0.0
    bw_vignette: float = 0.0
    split_shadows_hue: float = 0.0
    split_shadows_sat: float = 0.0
    split_highlights_hue: float = 0.0
    split_highlights_sat: float = 0.0
    split_balance: float = 0.0
    lens_distortion: float = 0.0
    lens_vignette: float = 0.0
    lens_ca: float = 0.0
    lens_scale: float = 1.0
    lens_auto_scale: bool = True
    lens_vertical_distortion: bool = False

    def copy(self):
        return Adjustments(**self.to_dict())

    @classmethod
    def from_dict(cls, data):
        """Build Adjustments from a dict, ignoring unknown keys."""

        known = {
            k: v for k, v in data.items() if k in cls.__dataclass_fields__
        }
        return cls(**known)

    def to_dict(self):
        return {
            "exposure": self.exposure, "contrast": self.contrast,
            "highlights": self.highlights, "shadows": self.shadows,
            "whites": self.whites, "blacks": self.blacks,
            "temperature": self.temperature, "tint": self.tint,
            "saturation": self.saturation, "vibrance": self.vibrance,
            "sharpness": self.sharpness, "clarity": self.clarity,
            "tone_curve": self.tone_curve,
            "shadows_color": self.shadows_color,
            "midtones_color": self.midtones_color,
            "highlights_color": self.highlights_color,
            "hsl_shadows": self.hsl_shadows,
            "hsl_midtones": self.hsl_midtones,
            "hsl_highlights": self.hsl_highlights,
            "bw_mix": self.bw_mix,
            "bw_grain": self.bw_grain,
            "bw_vignette": self.bw_vignette,
            "split_shadows_hue": self.split_shadows_hue,
            "split_shadows_sat": self.split_shadows_sat,
            "split_highlights_hue": self.split_highlights_hue,
            "split_highlights_sat": self.split_highlights_sat,
            "split_balance": self.split_balance,
            "lens_distortion": self.lens_distortion,
            "lens_vignette": self.lens_vignette,
            "lens_ca": self.lens_ca,
            "lens_scale": self.lens_scale,
            "lens_auto_scale": self.lens_auto_scale,
            "lens_vertical_distortion": self.lens_vertical_distortion,
        }

    def reset(self):
        self.exposure = self.contrast = self.highlights = self.shadows = 0.0
        self.whites = self.blacks = self.temperature = self.tint = 0.0
        self.saturation = self.vibrance = self.sharpness = self.clarity = 0.0
        self.tone_curve = None
        self.shadows_color = self.midtones_color = self.highlights_color = None
        self.hsl_shadows = self.hsl_midtones = self.hsl_highlights = None
        self.bw_mix = None
        self.bw_grain = self.bw_vignette = 0.0
        self.split_shadows_hue = self.split_shadows_sat = 0.0
        self.split_highlights_hue = self.split_highlights_sat = 0.0
        self.split_balance = 0.0
        self.lens_distortion = self.lens_vignette = self.lens_ca = 0.0
        self.lens_scale = 1.0
        self.lens_auto_scale = True
        self.lens_vertical_distortion = False


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
            gamma=settings.gamma,
            highlights=settings.highlights,
            shadows=settings.shadows,
            whites=settings.whites,
            blacks=settings.blacks,
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
        gamma: int = 0,
        highlights: int = 0,
        shadows: int = 0,
        whites: int = 0,
        blacks: int = 0,
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
        shadows = max(-100, min(100, shadows))
        whites = max(-100, min(100, whites))
        blacks = max(-100, min(100, blacks))
        brightness = max(-100, min(100, brightness))
        contrast = max(-100, min(100, contrast))
        saturation = max(-100, min(100, saturation))
        temperature = max(-100, min(100, temperature))
        tint = max(-100, min(100, tint))

        settings = AdjustmentSettings(
            exposure=exposure,
            gamma=gamma,
            highlights=highlights,
            shadows=shadows,
            whites=whites,
            blacks=blacks,
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
