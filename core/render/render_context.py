#!/usr/bin/env python3
"""Photo Editor 2.0 — Render Context."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Self

from PySide6.QtGui import QImage

from core.image.develop_settings import DevelopSettings


class RenderQuality(Enum):
    """Rendering quality presets."""
    DRAFT = auto()      # Fast, for UI preview
    NORMAL = auto()     # Standard quality
    HIGH = auto()       # Best quality, slower
    EXPORT = auto()     # Export-optimized


@dataclass(slots=True)
class RenderContext:
    """
    Holds all state required for a single render pass.
    Passed through every RenderStage.
    """

    # Target dimensions
    width: int = 0
    height: int = 0

    # Output format
    format: QImage.Format = QImage.Format.Format_ARGB32

    # Quality preset
    quality: RenderQuality = RenderQuality.NORMAL

    # Develop settings to apply
    develop_settings: DevelopSettings = field(default_factory=DevelopSettings)

    # Flags
    apply_adjustments: bool = True
    apply_effects: bool = True
    apply_sharpening: bool = True
    apply_noise_reduction: bool = False

    # Optional crop rect (None = full image)
    crop_rect: tuple[int, int, int, int] | None = None

    # Zoom level for UI preview (1.0 = 100%)
    preview_zoom: float = 1.0

    # Hash of the source state for cache invalidation
    state_hash: str = ""

    def copy(self) -> Self:
        """Return a shallow copy of the context."""
        return self.__class__(
            width=self.width,
            height=self.height,
            format=self.format,
            quality=self.quality,
            develop_settings=self.develop_settings.copy(),
            apply_adjustments=self.apply_adjustments,
            apply_effects=self.apply_effects,
            apply_sharpening=self.apply_sharpening,
            apply_noise_reduction=self.apply_noise_reduction,
            crop_rect=self.crop_rect,
            preview_zoom=self.preview_zoom,
            state_hash=self.state_hash,
        )

    def is_valid(self) -> bool:
        """Check if context has valid dimensions."""
        return self.width > 0 and self.height > 0
