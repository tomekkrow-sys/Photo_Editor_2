from __future__ import annotations


from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLabel,
)

from core.metadata.image_metadata import ImageMetadata


class MetadataPanel(QWidget):
    """Panel wyświetlający podstawowe informacje o zdjęciu."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout(self)

        self.filename = QLabel("-")
        self.path = QLabel("-")
        self.size = QLabel("-")
        self.resolution = QLabel("-")
        self.filetype = QLabel("-")
        self.modified = QLabel("-")

        layout.addRow("Nazwa:", self.filename)
        layout.addRow("Ścieżka:", self.path)
        layout.addRow("Rozmiar:", self.size)
        layout.addRow("Rozdzielczość:", self.resolution)
        layout.addRow("Typ:", self.filetype)
        layout.addRow("Zmodyfikowano:", self.modified)

    def set_photo(self, photo) -> None:
        self.filename.setText(photo.filename)
        self.path.setText(str(photo.full_path))

        try:
            meta = ImageMetadata.from_path(photo.full_path)

            self.size.setText(
                f"{meta.size_bytes/1024/1024:.1f} MB"
            )

            self.filetype.setText(meta.filetype)

            self.modified.setText(
                meta.modified.strftime("%Y-%m-%d %H:%M")
            )

            self.resolution.setText(
                f"{meta.width} × {meta.height}"
            )

        except Exception:
            self.size.setText("-")
            self.resolution.setText("-")
            self.filetype.setText("-")
            self.modified.setText("-")
