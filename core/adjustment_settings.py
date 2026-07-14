#!/usr/bin/env python3
"""Adjustment settings data model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class AdjustmentSettings:
    """Stores all image adjustment parameters."""

    brightness: int = 0
    contrast: int = 0
    saturation: int = 0
    temperature: int = 0

    def is_identity(self) -> bool:
        """Return True if no adjustment changes the image."""

        return (
            self.brightness == 0
            and self.contrast == 0
            and self.saturation == 0
            and self.temperature == 0
        )

    def copy(self) -> "AdjustmentSettings":
        """Return a copy of these settings."""

        return AdjustmentSettings(
            brightness=self.brightness,
            contrast=self.contrast,
            saturation=self.saturation,
            temperature=self.temperature,
        )