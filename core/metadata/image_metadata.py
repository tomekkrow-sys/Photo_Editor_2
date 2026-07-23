from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PIL import Image


@dataclass(slots=True)
class ImageMetadata:
    """Podstawowe metadane obrazu."""

    filename: str
    full_path: Path
    size_bytes: int
    width: int
    height: int
    filetype: str
    modified: datetime

    @classmethod
    def from_path(cls, path: Path) -> "ImageMetadata":
        stat = path.stat()

        with Image.open(path) as img:
            width, height = img.size

        return cls(
            filename=path.name,
            full_path=path,
            size_bytes=stat.st_size,
            width=width,
            height=height,
            filetype=path.suffix.upper().lstrip("."),
            modified=datetime.fromtimestamp(stat.st_mtime),
        )
