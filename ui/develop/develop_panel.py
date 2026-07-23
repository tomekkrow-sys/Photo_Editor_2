from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ui.develop.histogram_widget import HistogramWidget
from ui.view.image_view import ImageView
from core.models.photo import Photo


class DevelopPanel(QWidget):
    """Panel edycji zdjęcia."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)

        # ===================================
        # Podgląd zdjęcia
        # ===================================
        self.preview = ImageView()
        self.preview.setMinimumSize(700, 500)

        layout.addWidget(self.preview, 1)

        # ===================================
        # Prawy panel
        # ===================================
        tools = QVBoxLayout()

        tools.addWidget(HistogramWidget())

        sliders = [
            "Exposure",
            "Contrast",
            "Highlights",
            "Shadows",
            "Whites",
            "Blacks",
            "Saturation",
            "Vibrance",
        ]

        self.controls = {}

        for name in sliders:
            tools.addWidget(QLabel(name))

            slider = QSlider(Qt.Horizontal)
            slider.setRange(-100, 100)
            slider.setValue(0)

            tools.addWidget(slider)

            self.controls[name] = slider

        tools.addStretch()

        right = QWidget()
        right.setLayout(tools)
        right.setMaximumWidth(320)

        layout.addWidget(right)


    def load_photo(self, photo: Photo):
        pixmap = QPixmap(str(photo.full_path))

        if pixmap.isNull():
            return

        self.preview.set_pixmap(pixmap)
