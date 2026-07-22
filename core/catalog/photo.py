#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Photo:
    """Represents one photo in the catalog."""

    id: int

    filename: str

    full_path: Path

    rating: int = 0

    flag: int = 0

    @property
    def stem(self) -> str:
        return self.full_path.stem

    @property
    def extension(self) -> str:
        return self.full_path.suffix.lower()
