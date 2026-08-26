#!/usr/bin/env python3
"""Photo Editor 2.0 — Lens Corrections with Profile support."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class LensProfile:
    """Represents a lens profile (LCP-like)."""

    def __init__(
        self,
        name: str,
        vendor: str,
        model: str,
        distortion: float = 0.0,
        vignette: float = 0.0,
        chromatic_aberration: float = 0.0,
        scale: float = 1.0,
        crop_factor: float = 1.0,
    ):
        self.name = name
        self.vendor = vendor
        self.model = model
        self.distortion = distortion
        self.vignette = vignette
        self.chromatic_aberration = chromatic_aberration
        self.scale = scale
        self.crop_factor = crop_factor

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "vendor": self.vendor,
            "model": self.model,
            "distortion": self.distortion,
            "vignette": self.vignette,
            "chromatic_aberration": self.chromatic_aberration,
            "scale": self.scale,
            "crop_factor": self.crop_factor,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LensProfile":
        return cls(
            name=data.get("name", ""),
            vendor=data.get("vendor", ""),
            model=data.get("model", ""),
            distortion=data.get("distortion", 0.0),
            vignette=data.get("vignette", 0.0),
            chromatic_aberration=data.get("chromatic_aberration", 0.0),
            scale=data.get("scale", 1.0),
            crop_factor=data.get("crop_factor", 1.0),
        )


class LensPanel(QWidget):
    """Lens corrections panel with profile support."""

    valuesChanged = Signal(dict)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._profiles: list[LensProfile] = []
        self._selected_profile: LensProfile | None = None
        self._manual_distortion_slider = QSlider(Qt.Orientation.Horizontal)
        self._manual_vignette_slider = QSlider(Qt.Orientation.Horizontal)
        self._manual_ca_slider = QSlider(Qt.Orientation.Horizontal)
        self._scale_slider = QSlider(Qt.Orientation.Horizontal)
        self._auto_scale_check = QCheckBox("Automatyczne skalowanie")
        self._vertical_distortion_check = QCheckBox("Pionowa dystorsja")

        self._manual_distortion_slider.setRange(-100, 100)
        self._manual_distortion_slider.setValue(0)
        self._manual_vignette_slider.setRange(-50, 50)
        self._manual_vignette_slider.setValue(0)
        self._manual_ca_slider.setRange(-50, 50)
        self._manual_ca_slider.setValue(0)
        self._scale_slider.setRange(80, 120)
        self._scale_slider.setValue(100)

        self._manual_distortion_slider.valueChanged.connect(self._emit_change)
        self._manual_vignette_slider.valueChanged.connect(self._emit_change)
        self._manual_ca_slider.valueChanged.connect(self._emit_change)
        self._scale_slider.valueChanged.connect(self._emit_change)
        self._auto_scale_check.stateChanged.connect(self._emit_change)
        self._vertical_distortion_check.stateChanged.connect(self._emit_change)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        title = QLabel("<b>Korekcja obiektywu</b>")
        title.setStyleSheet("color: #FFFFFF; font-size: 13px; padding-bottom: 4px;")
        layout.addWidget(title)

        profile_layout = QHBoxLayout()
        profile_layout.addWidget(QLabel("Profil"))
        self._profile_combo = QLabel("--")
        profile_layout.addWidget(self._profile_combo)
        self._profile_apply_btn = QPushButton("Zastosuj")
        self._profile_apply_btn.clicked.connect(self._on_apply_profile)
        profile_layout.addWidget(self._profile_apply_btn)
        layout.addLayout(profile_layout)

        distortion_layout = QHBoxLayout()
        distortion_layout.addWidget(QLabel("Dystorsja"))
        self._distortion_label = QLabel("0")
        self._manual_distortion_slider.valueChanged.connect(
            lambda v: self._distortion_label.setText(str(v))
        )
        distortion_layout.addWidget(self._manual_distortion_slider)
        distortion_layout.addWidget(self._distortion_label)
        layout.addLayout(distortion_layout)

        vignette_layout = QHBoxLayout()
        vignette_layout.addWidget(QLabel("Winietowanie"))
        self._vignette_label = QLabel("0")
        self._manual_vignette_slider.valueChanged.connect(
            lambda v: self._vignette_label.setText(str(v))
        )
        vignette_layout.addWidget(self._manual_vignette_slider)
        vignette_layout.addWidget(self._vignette_label)
        layout.addLayout(vignette_layout)

        ca_layout = QHBoxLayout()
        ca_layout.addWidget(QLabel("Aberracja chromat."))
        self._ca_label = QLabel("0")
        self._manual_ca_slider.valueChanged.connect(
            lambda v: self._ca_label.setText(str(v))
        )
        ca_layout.addWidget(self._manual_ca_slider)
        ca_layout.addWidget(self._ca_label)
        layout.addLayout(ca_layout)

        scale_layout = QHBoxLayout()
        scale_layout.addWidget(QLabel("Skala"))
        self._scale_label = QLabel("100%")
        self._scale_slider.valueChanged.connect(
            lambda v: self._scale_label.setText(f"{v}%")
        )
        scale_layout.addWidget(self._scale_slider)
        scale_layout.addWidget(self._scale_label)
        layout.addLayout(scale_layout)

        layout.addWidget(self._auto_scale_check)
        layout.addWidget(self._vertical_distortion_check)

        reset_btn = QPushButton("Resetuj korekcje")
        reset_btn.clicked.connect(self.reset)
        layout.addWidget(reset_btn)
        layout.addStretch()

        self._style_widget()

    def _emit_change(self) -> None:
        self.valuesChanged.emit(self.get_values())

    def get_values(self) -> dict:
        return {
            "profile": self._selected_profile.to_dict() if self._selected_profile else None,
            "manual_distortion": self._manual_distortion_slider.value(),
            "manual_vignette": self._manual_vignette_slider.value(),
            "manual_ca": self._manual_ca_slider.value(),
            "scale": self._scale_slider.value() / 100.0,
            "auto_scale": self._auto_scale_check.isChecked(),
            "vertical_distortion": self._vertical_distortion_check.isChecked(),
        }

    def set_values(self, values: dict) -> None:
        if "manual_distortion" in values:
            self._manual_distortion_slider.setValue(values["manual_distortion"])
        if "manual_vignette" in values:
            self._manual_vignette_slider.setValue(values["manual_vignette"])
        if "manual_ca" in values:
            self._manual_ca_slider.setValue(values["manual_ca"])
        if "scale" in values:
            self._scale_slider.setValue(int(values["scale"] * 100))
        if "auto_scale" in values:
            self._auto_scale_check.setChecked(values["auto_scale"])
        if "vertical_distortion" in values:
            self._vertical_distortion_check.setChecked(values["vertical_distortion"])
        if "profile" in values and values["profile"]:
            self._selected_profile = LensProfile.from_dict(values["profile"])
            self._profile_combo.setText(self._selected_profile.name or "--")

    def load_profiles(self, profiles: list[LensProfile]) -> None:
        self._profiles = profiles

    def _on_apply_profile(self) -> None:
        if self._selected_profile:
            self._manual_distortion_slider.setValue(int(self._selected_profile.distortion))
            self._manual_vignette_slider.setValue(int(self._selected_profile.vignette))
            self._manual_ca_slider.setValue(int(self._selected_profile.chromatic_aberration))
            self._scale_slider.setValue(int(self._selected_profile.scale * 100))
            self._emit_change()

    def reset(self) -> None:
        self._manual_distortion_slider.setValue(0)
        self._manual_vignette_slider.setValue(0)
        self._manual_ca_slider.setValue(0)
        self._scale_slider.setValue(100)
        self._auto_scale_check.setChecked(False)
        self._vertical_distortion_check.setChecked(False)
        self._selected_profile = None
        self._profile_combo.setText("--")
        self._emit_change()

    def _style_widget(self):
        self.setStyleSheet("""
            QWidget {
                background: #1E1E1E;
                color: #CCCCCC;
                font-family: "Segoe UI", "Ubuntu", sans-serif;
                font-size: 12px;
            }
            QLabel {
                color: #AAAAAA;
                padding: 2px 0px;
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: #333333;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                height: 14px;
                margin: -5px 0;
                background: #2196F3;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #42A5F5;
            }
            QSlider::sub-page:horizontal {
                background: #2196F3;
                border-radius: 2px;
            }
            QCheckBox {
                color: #AAAAAA;
            }
            QPushButton {
                background: #333333;
                border: 1px solid #444444;
                padding: 4px 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background: #444444;
            }
        """)
