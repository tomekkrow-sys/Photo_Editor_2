#!/usr/bin/env python3
"""Develop settings for RAW/image processing pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Self


@dataclass(slots=True)
class DevelopSettings:
    """
    Complete develop settings for photo editing.
    Combines tone, color, detail and effects adjustments.
    """

    # Tone
    exposure: float = 0.0
    contrast: float = 0.0
    highlights: float = 0.0
    shadows: float = 0.0
    whites: float = 0.0
    blacks: float = 0.0
    brightness: float = 0.0
    gamma: float = 1.0

    # Color
    temperature: float = 0.0
    tint: float = 0.0
    saturation: float = 0.0
    vibrance: float = 0.0

    # Detail
    sharpness: float = 0.0
    clarity: float = 0.0
    noise_reduction: float = 0.0

    # Effects
    vignette: float = 0.0
    dehaze: float = 0.0
    grain: float = 0.0

    def is_identity(self) -> bool:
        """Return True if all values are at default (no effect)."""
        return all(
            getattr(self, field.name) == field.default
            for field in self.__dataclass_fields__.values()
        )

    def reset(self) -> None:
        """Reset all settings to defaults."""
        for field in self.__dataclass_fields__.values():
            setattr(self, field.name, field.default)

    def to_dict(self) -> dict[str, float]:
        """Serialize to dictionary."""
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
        }

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> Self:
        """Deserialize from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def copy(self) -> Self:
        """Return a deep copy."""
        return self.__class__(**self.to_dict())
