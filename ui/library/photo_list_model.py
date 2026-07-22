from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

from core.catalog.photo import Photo
from core.catalog.thumbnail_cache import ThumbnailCache


class PhotoListModel(QAbstractListModel):
    """Model zdjęć dla widoku biblioteki."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._photos: list[Photo] = []
        self._thumbnail_cache = ThumbnailCache()

    def set_photos(self, photos: list[Photo]) -> None:
        self.beginResetModel()
        self._photos = photos
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._photos)

    def data(self, index: QModelIndex, role: int):
        if not index.isValid():
            return None

        photo = self._photos[index.row()]

        if role == Qt.DisplayRole:
            return photo.stem

        if role == Qt.DecorationRole:
            return self._thumbnail_cache.icon(photo)

        if role == Qt.UserRole:
            return photo

        return None

    def photo(self, row: int) -> Photo:
        return self._photos[row]
