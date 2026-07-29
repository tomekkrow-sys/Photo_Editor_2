#!/usr/bin/env python3
"""Photo Editor 2.0 — Export Job model."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Self

from core.image.develop_settings import DevelopSettings


class ExportFormat(Enum):
    """Supported export formats."""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"


class ExportState(Enum):
    """Job lifecycle states."""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class ExportJob:
    """
    Represents a single export task.
    """

    # Input
    source_path: Path
    image: object = None  # QImage or PIL Image

    # Output
    destination_path: Path = field(default_factory=lambda: Path(""))
    format: ExportFormat = ExportFormat.JPEG

    # Settings
    quality: int = 95           # 1-100 (JPEG/WebP)
    max_width: int = 0          # 0 = original size
    max_height: int = 0         # 0 = original size
    keep_exif: bool = True
    apply_develop: bool = True
    develop_settings: DevelopSettings = field(default_factory=DevelopSettings)

    # State
    state: ExportState = ExportState.PENDING
    progress: int = 0           # 0-100
    error_message: str = ""

    @property
    def is_pending(self) -> bool:
        return self.state == ExportState.PENDING

    @property
    def is_running(self) -> bool:
        return self.state == ExportState.RUNNING

    @property
    def is_completed(self) -> bool:
        return self.state == ExportState.COMPLETED

    @property
    def is_failed(self) -> bool:
        return self.state == ExportState.FAILED

    @property
    def is_finished(self) -> bool:
        return self.state in (ExportState.COMPLETED, ExportState.FAILED, ExportState.CANCELLED)

    @property
    def file_extension(self) -> str:
        mapping = {
            ExportFormat.JPEG: ".jpg",
            ExportFormat.PNG: ".png",
            ExportFormat.WEBP: ".webp",
            ExportFormat.TIFF: ".tif",
            ExportFormat.BMP: ".bmp",
        }
        return mapping.get(self.format, ".jpg")

    def reset(self) -> None:
        """Reset job to pending state."""
        self.state = ExportState.PENDING
        self.progress = 0
        self.error_message = ""

    def set_progress(self, value: int) -> None:
        """Update progress (clamped 0-100)."""
        self.progress = max(0, min(100, value))

    def mark_completed(self) -> None:
        """Mark job as successfully finished."""
        self.state = ExportState.COMPLETED
        self.progress = 100
        self.error_message = ""

    def mark_failed(self, message: str) -> None:
        """Mark job as failed with error message."""
        self.state = ExportState.FAILED
        self.error_message = message

    def mark_cancelled(self) -> None:
        """Mark job as cancelled."""
        self.state = ExportState.CANCELLED
        self.progress = 0

    def clone(self) -> Self:
        """Return a shallow copy of the job."""
        return self.__class__(
            source_path=self.source_path,
            image=self.image,
            destination_path=self.destination_path,
            format=self.format,
            quality=self.quality,
            max_width=self.max_width,
            max_height=self.max_height,
            keep_exif=self.keep_exif,
            apply_develop=self.apply_develop,
            develop_settings=self.develop_settings.copy(),
        )
