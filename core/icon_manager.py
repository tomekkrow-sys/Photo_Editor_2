#!/usr/bin/env python3
"""
Photo Editor 2.0

Icon Manager — loads SVG icons and optionally tints them to a theme color.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer


class IconManager:
    """
    Loads SVG icons (with optional color tinting for theme support).
    """

    def __init__(self):

        self.icon_dir = (
            Path(__file__).resolve().parent.parent
            / "resources"
            / "icons"
            / "svg"
        )
        self._cache: dict[tuple[str, str | None], QIcon] = {}

    def icon(self, name: str, color: str | None = None) -> QIcon:
        """Return QIcon for *name*; if *color* given, tint white strokes to it."""
        key = (name, color)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        file = self.icon_dir / f"{name}.svg"
        if not file.exists():
            return QIcon()

        if color is None:
            icon = QIcon(str(file))
        else:
            icon = self._tinted(file, color)

        self._cache[key] = icon
        return icon

    @staticmethod
    def _tinted(file: Path, color: str) -> QIcon:
        """Render an SVG and recolor its opaque pixels to *color*."""
        renderer = QSvgRenderer(str(file))
        if not renderer.isValid():
            return QIcon(str(file))

        size = renderer.defaultSize()
        if size.isEmpty():
            size = Qt.QSize(24, 24)

        src = QImage(size, QImage.Format.Format_ARGB32_Premultiplied)
        src.fill(Qt.GlobalColor.transparent)
        painter = QPainter(src)
        renderer.render(painter)
        painter.end()

        # Replace color, keep alpha (SVG strokes are white on transparent)
        tinted = QImage(src.size(), QImage.Format.Format_ARGB32_Premultiplied)
        tinted.fill(Qt.GlobalColor.transparent)
        painter = QPainter(tinted)
        painter.drawImage(0, 0, src)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        painter.fillRect(QRectF(tinted.rect()), QColor(color))
        painter.end()

        return QIcon(QPixmap.fromImage(tinted))
