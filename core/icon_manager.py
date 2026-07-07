#!/usr/bin/env python3
"""
Photo Editor 2.0

Icon Manager
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QIcon


class IconManager:
    """
    Loads SVG icons.
    """

    def __init__(self):

        self.icon_dir = (
            Path(__file__).resolve().parent.parent
            / "resources"
            / "icons"
            / "svg"
        )

    def icon(self, name: str) -> QIcon:

        file = self.icon_dir / f"{name}.svg"

        if file.exists():

            return QIcon(str(file))

        return QIcon()