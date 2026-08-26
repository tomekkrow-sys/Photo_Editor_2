#!/usr/bin/env python3
"""Photo Editor 2.0 — Detail Panel with Masking."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class DetailPanel(QWidget):
    """Detail panel with sharpening, noise reduction, and masking."""

    valuesChanged = Signal(dict)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        layout.addWidget(self._create_sharpening_section())
        layout.addWidget(self._create_noise_reduction_section())
        layout.addWidget(self._create_masking_section())

        reset_btn = self._create_reset_button()
        layout.addWidget(reset_btn)
        layout.addStretch()

        self._style_widget()

    def _create_sharpening_section(self) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)

        layout.addWidget(self._create_slider("Wyostrzanie", 75, 0, 150))
        layout.addWidget(self._create_slider("Promień", 1.0, 0.5, 5.0, 0.1))
        layout.addWidget(self._create_slider("Przeloczenie", 50, 0, 200))
        layout.addWidget(self._create_slider("Chromiu", 25, 0, 100))

        return section

    def _create_noise_reduction_section(self) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)

        layout.addWidget(self._create_slider("Szum jasności", 25, 0, 100))
        layout.addWidget(self._create_slider("Szum koloru", 25, 0, 100))
        layout.addWidget(self._create_slider("Detale szumu", 50, 0, 100))
        layout.addWidget(self._create_slider("Czystość", 50, 0, 100))

        return section

    def _create_masking_section(self) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)

        layout.addWidget(self._create_slider("Maska wywołania", 0, 0, 100))
        layout.addWidget(self._create_slider("Maska szumu", 0, 0, 100))

        self._sharpen_mask_check = QCheckBox("Pokaż maskę wywołania")
        self._sharpen_mask_check.stateChanged.connect(lambda: self.valuesChanged.emit(self.get_values()))
        layout.addWidget(self._sharpen_mask_check)

        self._noise_mask_check = QCheckBox("Pokaż maskę szumu")
        self._noise_mask_check.stateChanged.connect(lambda: self.valuesChanged.emit(self.get_values()))
        layout.addWidget(self._noise_mask_check)

        return section

    def _create_slider(self, label: str) -> QSlider:
        from PySide6.QtWidgets import QSlider
        slider = QSlider()
        slider.setOrientation(1)
        slider.setValue(50)
        return slider

    def get_values(self) -> dict:
        return {
            "sharpen_mask": self._sharpen_mask_check.isChecked(),
            "noise_mask": self._noise_mask_check.isChecked(),
        }

    def _create_reset_button(self) -> QPushButton:
        from PySide6.QtWidgets import QPushButton
        button = QPushButton("Resetuj")
        button.clicked.connect(lambda: self.valuesChanged.emit(self.get_values()))
        return button

    def _style_widget(self) -> None:
        self.setStyleSheet(
            """
            QWidget {
                background: #1E1E1E;
                color: #CCCCCC;
                font-family: "Segoe UI", "Ubuntu", sans-serif;
                font-size: 12px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 6px;
                background: #2A2A2A;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #4A9EFF;
                border: 1px solid #2A6BCF;
                width: 14px;
                height: 14px;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #4A9EFF;
                border-radius: 3px;
            }
            """
        )

    def _on_value_changed(self) -> None:
        self.valuesChanged.emit(self.get_values())

