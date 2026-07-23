from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

from core.catalog.photo import Photo
from core.thumbnails.thumbnail_manager import thumbnail_manager


class PhotoListModel(QAbstractListModel):
    """Model zdjęć dla widoku biblioteki."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._photos: list[Photo] = []
        self._thumbnail_manager = thumbnail_manager
        self._thumbnail_manager.thumbnail_ready.connect(
            self._thumbnail_ready
        )


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
            return self._thumbnail_manager.get(photo.full_path)

        if role == Qt.UserRole:
            return photo

        return None

    def photo(self, row: int) -> Photo:
        return self._photos[row]


    def _thumbnail_ready(self, filename: str, icon) -> None:
        for row, photo in enumerate(self._photos):
            if str(photo.full_path) == filename:
                index = self.index(row, 0)
                self.dataChanged.emit(
                    index,
                    index,
                    [Qt.DecorationRole],
                )
                break
