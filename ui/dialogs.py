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


class NewDocumentDialog(QDialog):
    """Dialog for creating a new document."""

    MAX_IMAGE_SIZE = 100_000

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Nowy dokument")
        self.setModal(True)

        self.width_spin = QSpinBox(self)
        self.width_spin.setRange(1, self.MAX_IMAGE_SIZE)
        self.width_spin.setValue(1920)
        self.width_spin.setSuffix(" px")

        self.height_spin = QSpinBox(self)
        self.height_spin.setRange(1, self.MAX_IMAGE_SIZE)
        self.height_spin.setValue(1080)
        self.height_spin.setSuffix(" px")

        self.transparent = QCheckBox(
            "Przezroczyste tło",
            self,
        )

        form = QFormLayout()
        form.addRow("Szerokość:", self.width_spin)
        form.addRow("Wysokość:", self.height_spin)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.transparent)
        layout.addWidget(buttons)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

    @property
    def image_width(self) -> int:
        return self.width_spin.value()

    @property
    def image_height(self) -> int:
        return self.height_spin.value()

    @property
    def transparent_background(self) -> bool:
        return self.transparent.isChecked()


class AdjustmentsDialog(QDialog):
    """Dialog for brightness and contrast adjustments."""

    values_changed = Signal(int, int, int, int, int, int, int, int, int, int, int)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Jasność i kontrast")
        self.setModal(False)
        self.setMinimumWidth(420)

        self.exposure_slider = self._create_slider()
        self.exposure_value = QLabel("0", self)

        self.gamma_slider = self._create_slider()
        self.gamma_value = QLabel("0", self)

        self.highlights_slider = self._create_slider()
        self.highlights_value = QLabel("0", self)

        self.shadows_slider = self._create_slider()
        self.shadows_value = QLabel("0", self)

        self.whites_slider = self._create_slider()
        self.whites_value = QLabel("0", self)

        self.blacks_slider = self._create_slider()
        self.blacks_value = QLabel("0", self)

        self.brightness_slider = self._create_slider()
        self.brightness_value = QLabel("0", self)

        self.contrast_slider = self._create_slider()
        self.contrast_value = QLabel("0", self)

        self.saturation_slider = self._create_slider()
        self.saturation_value = QLabel("0", self)

        self.temperature_slider = self._create_slider()
        self.temperature_value = QLabel("0", self)

        self.tint_slider = self._create_slider()
        self.tint_value = QLabel("0", self)

        exposure_layout = QHBoxLayout()
        exposure_layout.addWidget(
            self.exposure_slider
        )
        exposure_layout.addWidget(
            self.exposure_value
        )

        gamma_layout = QHBoxLayout()
        gamma_layout.addWidget(
            self.gamma_slider
        )
        gamma_layout.addWidget(
            self.gamma_value
        )

        highlights_layout = QHBoxLayout()
        highlights_layout.addWidget(
            self.highlights_slider
        )
        highlights_layout.addWidget(
            self.highlights_value
        )

        shadows_layout = QHBoxLayout()
        shadows_layout.addWidget(
            self.shadows_slider
        )
        shadows_layout.addWidget(
            self.shadows_value
        )

        whites_layout = QHBoxLayout()
        whites_layout.addWidget(
            self.whites_slider
        )
        whites_layout.addWidget(
            self.whites_value
        )

        blacks_layout = QHBoxLayout()
        blacks_layout.addWidget(
            self.blacks_slider
        )
        blacks_layout.addWidget(
            self.blacks_value
        )

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

        tint_layout = QHBoxLayout()
        tint_layout.addWidget(
            self.tint_slider
        )
        tint_layout.addWidget(
            self.tint_value
        )

        form_layout = QFormLayout()
        form_layout.addRow(
            "Ekspozycja:",
            exposure_layout,
        )
        form_layout.addRow(
            "Gamma:",
            gamma_layout,
        )
        form_layout.addRow(
            "Światła:",
            highlights_layout,
        )
        form_layout.addRow(
            "Cienie:",
            shadows_layout,
        )
        form_layout.addRow(
            "Biele:",
            whites_layout,
        )
        form_layout.addRow(
            "Czernie:",
            blacks_layout,
        )
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
        form_layout.addRow(
            "Odcień:",
            tint_layout,
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

        self.exposure_slider.valueChanged.connect(
            self._update_exposure_value
        )

        self.gamma_slider.valueChanged.connect(
            self._update_gamma_value
        )

        self.highlights_slider.valueChanged.connect(
            self._update_highlights_value
        )

        self.shadows_slider.valueChanged.connect(
            self._update_shadows_value
        )

        self.whites_slider.valueChanged.connect(
            self._update_whites_value
        )

        self.blacks_slider.valueChanged.connect(
            self._update_blacks_value
        )

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
        self.tint_slider.valueChanged.connect(
            self._update_tint_value
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
    def exposure(self) -> int:
        """Return the selected exposure value."""

        return self.exposure_slider.value()

    @property
    def gamma(self) -> int:
        """Return the selected gamma value."""

        return self.gamma_slider.value()

    @property
    def highlights(self) -> int:
        """Return the selected highlights value."""

        return self.highlights_slider.value()

    @property
    def shadows(self) -> int:
        """Return the selected shadows value."""

        return self.shadows_slider.value()

    @property
    def whites(self) -> int:
        """Return the selected whites value."""

        return self.whites_slider.value()
    @property
    def blacks(self) -> int:
        """Return the selected blacks value."""

        return self.blacks_slider.value()

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


    @property
    def tint(self) -> int:
        """Return the selected tint value."""

        return self.tint_slider.value()

    def _update_gamma_value(
        self,
        value: int,
    ) -> None:
        """Update the gamma value label."""

        self.gamma_value.setText(str(value))
        self.values_changed.emit(
            self.exposure,
            self.gamma,
            self.highlights,
            self.shadows,
            self.whites,
            self.blacks,
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
            self.tint,
        )

    def _update_exposure_value(
        self,
        value: int,
    ) -> None:
        """Update the exposure value label."""

        self.exposure_value.setText(str(value))
        self.values_changed.emit(
            self.exposure,
            self.gamma,
            self.highlights,
            self.shadows,
            self.whites,
            self.blacks,
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
            self.tint,
        )

    def _update_highlights_value(
        self,
        value: int,
    ) -> None:
        """Update the highlights value label."""

        self.highlights_value.setText(str(value))
        self.values_changed.emit(
            self.exposure,
            self.gamma,
            self.highlights,
            self.shadows,
            self.whites,
            self.blacks,
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
            self.tint,
        )

    def _update_shadows_value(
        self,
        value: int,
    ) -> None:
        """Update the shadows value label."""

        self.shadows_value.setText(str(value))
        self.values_changed.emit(
            self.exposure,
            self.gamma,
            self.highlights,
            self.shadows,
            self.whites,
            self.blacks,
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
            self.tint,
        )

    def _update_whites_value(
        self,
        value: int,
    ) -> None:
        """Update the whites value label."""

        self.whites_value.setText(str(value))
        self.values_changed.emit(
            self.exposure,
            self.gamma,
            self.highlights,
            self.shadows,
            self.whites,
            self.blacks,
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
            self.tint,
        )

    def _update_blacks_value(
        self,
        value: int,
    ) -> None:
        """Update the blacks value label."""

        self.blacks_value.setText(str(value))
        self.values_changed.emit(
            self.exposure,
            self.gamma,
            self.highlights,
            self.shadows,
            self.whites,
            self.blacks,
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
            self.tint,
        )

    def _update_brightness_value(
        self,
        value: int,
    ) -> None:
        """Update the brightness value label."""

        self.brightness_value.setText(str(value))
        self.values_changed.emit(
            self.exposure,
            self.gamma,
            self.highlights,
            self.shadows,
            self.whites,
            self.blacks,
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
            self.tint,
        )

    def _update_contrast_value(
        self,
        value: int,
    ) -> None:
        """Update the contrast value label."""

        self.contrast_value.setText(str(value))
        self.values_changed.emit(
            self.exposure,
            self.gamma,
            self.highlights,
            self.shadows,
            self.whites,
            self.blacks,
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
            self.tint,
        )

    def _update_saturation_value(
        self,
        value: int,
    ) -> None:
        """Update the saturation value label."""

        self.saturation_value.setText(str(value))
        self.values_changed.emit(
            self.exposure,
            self.gamma,
            self.highlights,
            self.shadows,
            self.whites,
            self.blacks,
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
            self.tint,
        )

    def _update_temperature_value(
        self,
        value: int,
    ) -> None:
        """Update the temperature value label."""

        self.temperature_value.setText(str(value))
        self.values_changed.emit(
            self.exposure,
            self.gamma,
            self.highlights,
            self.shadows,
            self.whites,
            self.blacks,
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
            self.tint,
        )


    def _update_tint_value(
        self,
        value: int,
    ) -> None:
        """Update the tint value label."""

        self.tint_value.setText(str(value))
        self.values_changed.emit(
            self.exposure,
            self.gamma,
            self.highlights,
            self.shadows,
            self.whites,
            self.blacks,
            self.brightness,
            self.contrast,
            self.saturation,
            self.temperature,
            self.tint,
        )

    def reset_values(self) -> None:
        """Reset all adjustments to zero."""

        self.exposure_slider.setValue(0)
        self.gamma_slider.setValue(0)
        self.highlights_slider.setValue(0)
        self.shadows_slider.setValue(0)
        self.whites_slider.setValue(0)
        self.blacks_slider.setValue(0)
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.saturation_slider.setValue(0)
        self.temperature_slider.setValue(0)
        self.tint_slider.setValue(0)
