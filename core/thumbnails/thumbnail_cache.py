from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QImageReader, QPixmap

from core.catalog.photo import Photo


class ThumbnailCache:
    """Cache miniaturek."""

    WIDTH = 96
    HEIGHT = 64

    def __init__(self):
        self._cache: dict[str, QIcon] = {}

    def icon(self, photo: Photo) -> QIcon | None:
        key = str(photo.full_path)

        if key in self._cache:
            return self._cache[key]

        reader = QImageReader(key)
        reader.setScaledSize(QSize(self.WIDTH, self.HEIGHT))

        image = reader.read()

        if image.isNull():
            return None

        icon = QIcon(QPixmap.fromImage(image))
        self._cache[key] = icon

        return icon
