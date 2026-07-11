#!/usr/bin/env python3
"""Application dialogs."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QSpinBox,
    QVBoxLayout,
)


class ResizeImageDialog(QDialog):
    """Dialog for selecting a new image size."""

    MAX_IMAGE_SIZE = 100_000

    def __init__(
        self,
        width: int,
        height: int,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self._original_width = width
        self._original_height = height
        self._updating = False

        self.setWindowTitle("Zmień rozmiar obrazu")
        self.setModal(True)

        self.width_spin = QSpinBox(self)
        self.width_spin.setRange(1, self.MAX_IMAGE_SIZE)
        self.width_spin.setValue(width)
        self.width_spin.setSuffix(" px")

        self.height_spin = QSpinBox(self)
        self.height_spin.setRange(1, self.MAX_IMAGE_SIZE)
        self.height_spin.setValue(height)
        self.height_spin.setSuffix(" px")

        self.keep_aspect = QCheckBox(
            "Zachowaj proporcje",
            self,
        )
        self.keep_aspect.setChecked(True)

        form_layout = QFormLayout()
        form_layout.addRow(
            "Szerokość:",
            self.width_spin,
        )
        form_layout.addRow(
            "Wysokość:",
            self.height_spin,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(self.keep_aspect)
        layout.addWidget(buttons)

        self.width_spin.valueChanged.connect(
            self._width_changed
        )
        self.height_spin.valueChanged.connect(
            self._height_changed
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    @property
    def image_width(self) -> int:
        """Return the selected image width."""

        return self.width_spin.value()

    @property
    def image_height(self) -> int:
        """Return the selected image height."""

        return self.height_spin.value()

    def _width_changed(self, width: int) -> None:
        """Update height when aspect ratio is locked."""

        if (
            self._updating
            or not self.keep_aspect.isChecked()
            or self._original_width <= 0
        ):
            return

        self._updating = True

        height = round(
            width
            * self._original_height
            / self._original_width
        )

        self.height_spin.setValue(max(1, height))
        self._updating = False

    def _height_changed(self, height: int) -> None:
        """Update width when aspect ratio is locked."""

        if (
            self._updating
            or not self.keep_aspect.isChecked()
            or self._original_height <= 0
        ):
            return

        self._updating = True

        width = round(
            height
            * self._original_width
            / self._original_height
        )

        self.width_spin.setValue(max(1, width))
        self._updating = False