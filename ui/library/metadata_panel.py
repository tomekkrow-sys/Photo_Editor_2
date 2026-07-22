from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLabel,
)


class MetadataPanel(QWidget):
    """Panel wyświetlający podstawowe informacje o zdjęciu."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QFormLayout(self)

        self.filename = QLabel("-")
        self.path = QLabel("-")
        self.size = QLabel("-")

        layout.addRow("Nazwa:", self.filename)
        layout.addRow("Ścieżka:", self.path)
        layout.addRow("Rozmiar:", self.size)

    def set_photo(self, photo) -> None:
        self.filename.setText(photo.filename)
        self.path.setText(str(photo.full_path))

        try:
            size = Path(photo.full_path).stat().st_size
            self.size.setText(f"{size/1024/1024:.1f} MB")
        except OSError:
            self.size.setText("-")
