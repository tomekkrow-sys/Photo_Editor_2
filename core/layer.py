#!/usr/bin/env python3
"""
Photo Editor 2.0

Layer
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4

from PySide6.QtGui import QImage


class BlendMode(Enum):
    """Supported blend modes."""

    NORMAL = "normal"


@dataclass(slots=True)
class Layer:
    """Represents a single image layer."""

    name: str
    image: QImage

    visible: bool = True
    opacity: float = 1.0
    locked: bool = False

    blend_mode: BlendMode = BlendMode.NORMAL

    id: UUID = field(default_factory=uuid4)
