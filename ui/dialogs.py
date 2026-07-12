#!/usr/bin/env python3
"""Application dialogs."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
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


class AdjustmentsDialog(QDialog):
    """Dialog for brightness and contrast adjustments."""

    values_changed = Signal(int, int, int, int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Jasność i kontrast")
        self.setModal(False)
        self.setMinimumWidth(420)

        self.brightness_slider = self._create_slider()
        self.brightness_value = QLabel("0", self)

        self.contrast_slider = self._create_slider()
        self.contrast_value = QLabel("0", self)

        self.saturation_slider = self._create_slider()
        self.saturation_value = QLabel("0", self)

        self.temperature_slider = self._create_slider()
        self.temperature_value = QLabel("0", self)

        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(
            self.brightness_slider
        )
        brightness_layout.addWidget(
            self.brightness_value
        )

        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(
            self.contrast_slider
        )
        contrast_layout.addWidget(
            self.contrast_value
        )

        saturation_layout = QHBoxLayout()
        saturation_layout.addWidget(
            self.saturation_slider
        )
        saturation_layout.addWidget(
            self.saturation_value
        )

        temperature_layout = QHBoxLayout()
        temperature_layout.addWidget(
            self.temperature_slider
        )
        temperature_layout.addWidget(
            self.temperature_value
        )

        form_layout = QFormLayout()
        form_layout.addRow(
            "Jasność:",
            brightness_layout,
        )
        form_layout.addRow(
            "Kontrast:",
            contrast_layout,
        )
        form_layout.addRow(
            "Nasycenie:",
            saturation_layout,
        )
        form_layout.addRow(
            "Temperatura:",
            temperature_layout,
        )

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Reset,
            parent=self,
        )

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
        layout.addWidget(buttons)

        self.brightness_slider.valueChanged.connect(
            self._update_brightness_value
        )
        self.contrast_slider.valueChanged.connect(
            self._update_contrast_value
        )
        self.saturation_slider.valueChanged.connect(
            self._update_saturation_value
        )
        self.temperature_slider.valueChanged.connect(
            self._update_temperature_value
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        reset_button = buttons.button(
            QDialogButtonBox.StandardButton.Reset
        )
        reset_button.clicked.connect(self.reset_values)

    @staticmethod
    def _create_slider() -> QSlider:
        """Create an adjustment slider."""

        slider = QSlider(
            Qt.Orientation.Horizontal
        )
        slider.setRange(-100, 100)
        slider.setValue(0)
        slider.setTickInterval(10)

        return slider

    @property
    def brightness(self) -> int:
        """Return the selected brightness value."""

        return self.brightness_slider.value()

    @property
    def contrast(self) -> int:
        """Return the selected contrast value."""

        return self.contrast_slider.value()

    @property
    def saturation(self) -> int:
        """Return the selected saturation value."""

        return self.saturation_slider.value()

    @property
    def temperature(self) -> int:
        """Return the selected temperature value."""

        return self.temperature_slider.value()

    def _update_brightness_value(
        self,
        value: int,
    ) -> None:
        """Update the brightness value label."""

        self.brightness_value.setText(str(value))
        self.values_changed.emit(
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
        )

    def _update_contrast_value(
        self,
        value: int,
    ) -> None:
        """Update the contrast value label."""

        self.contrast_value.setText(str(value))
        self.values_changed.emit(
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
        )

    def _update_saturation_value(
        self,
        value: int,
    ) -> None:
        """Update the saturation value label."""

        self.saturation_value.setText(str(value))
        self.values_changed.emit(
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
        )

    def _update_temperature_value(
        self,
        value: int,
    ) -> None:
        """Update the temperature value label."""

        self.temperature_value.setText(str(value))
        self.values_changed.emit(
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
        )

    def reset_values(self) -> None:
        """Reset all adjustments to zero."""

        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.saturation_slider.setValue(0)
        self.temperature_slider.setValue(0)
