#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QSlider, QVBoxLayout, QWidget,
)
from core.adjustments import Adjustments
from config.i18n import t, I18n

class SliderRow(QWidget):
    value_changed = Signal(str, float)
    def __init__(self, name, key, mn, mx, df=0.0, st=1.0):
        super().__init__()
        self.key = key
        self._name = name
        self._st = st
        self._df = df
        lay = QVBoxLayout(self)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(2)
        self.lab = QLabel(f"{name}: {df:.1f}")
        self.lab.setStyleSheet("font-size: 15px; font-weight: 700;")
        lay.addWidget(self.lab)
        self.sli = QSlider(Qt.Orientation.Horizontal)
        self.sli.setRange(int(mn/st), int(mx/st))
        self.sli.setValue(int(df/st))
        self.sli.valueChanged.connect(self._on)
        lay.addWidget(self.sli)
        b = QPushButton("R")
        b.setMaximumWidth(28)
        b.setMinimumHeight(20)
        b.clicked.connect(self._reset)
        lay.addWidget(b)
    def _on(self, v):
        val = v * self._st
        self.lab.setText(f"{self._name}: {val:.1f}")
        self.value_changed.emit(self.key, val)
    def _reset(self):
        self.sli.setValue(int(self._df / self._st))

class RightPanel(QScrollArea):
    adjustments_changed = Signal(Adjustments)
    reset_requested = Signal()
    export_requested = Signal()
    preset_save_requested = Signal(str, object)
    preset_load_requested = Signal(str)
    preset_delete_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._adj = Adjustments()
        self._blk = False
        self.setWidgetResizable(True)
        self.setMaximumWidth(280)
        self.setMinimumWidth(240)
        self._build_content()
        I18n.get().on_change(self._rebuild)

    def _rebuild(self, lang=None):
        self._build_content()

    def _build_content(self):
        # Clear existing content
        old = self.widget()
        if old:
            old.deleteLater()

        c = QWidget()
        lay = QVBoxLayout(c)
        lay.setSpacing(6)

        pres = QGroupBox(t("presets"))
        pl = QVBoxLayout(pres)
        self.preset_combo = QComboBox()
        self.preset_combo.addItem(t("select_preset"))
        pl.addWidget(self.preset_combo)
        self.preset_name = QLineEdit()
        self.preset_name.setPlaceholderText(t("preset_name_placeholder"))
        pl.addWidget(self.preset_name)
        row = QWidget()
        rl = QHBoxLayout(row)
        sb = QPushButton(t("preset_save"))
        lb = QPushButton(t("preset_load"))
        db = QPushButton(t("preset_delete"))
        sb.clicked.connect(self._on_preset_save)
        lb.clicked.connect(self._on_preset_load)
        db.clicked.connect(self._on_preset_delete)
        rl.addWidget(sb)
        rl.addWidget(lb)
        rl.addWidget(db)
        pl.addWidget(row)
        lay.addWidget(pres)

        basic = QGroupBox(t("basic"))
        bl = QFormLayout(basic)
        bl.setSpacing(4)
        self.exp = self._mk(t("exposure"), "exposure", -5.0, 5.0, 0.0, 0.1)
        self.con = self._mk(t("contrast"), "contrast", -100, 100, 0, 1)
        bl.addRow(self.exp)
        bl.addRow(self.con)
        lay.addWidget(basic)

        tone = QGroupBox(t("tone"))
        tl = QFormLayout(tone)
        tl.setSpacing(4)
        self.hi = self._mk(t("highlights"), "highlights", -100, 100, 0, 1)
        self.sh = self._mk(t("shadows"), "shadows", -100, 100, 0, 1)
        self.wh = self._mk(t("whites"), "whites", -100, 100, 0, 1)
        self.bl = self._mk(t("blacks"), "blacks", -100, 100, 0, 1)
        tl.addRow(self.hi)
        tl.addRow(self.sh)
        tl.addRow(self.wh)
        tl.addRow(self.bl)
        lay.addWidget(tone)

        col = QGroupBox(t("color"))
        cl = QFormLayout(col)
        cl.setSpacing(4)
        self.tmp = self._mk(t("temperature"), "temperature", -100, 100, 0, 1)
        self.tnt = self._mk(t("tint"), "tint", -100, 100, 0, 1)
        self.sat = self._mk(t("saturation"), "saturation", -100, 100, 0, 1)
        self.vib = self._mk(t("vibrance"), "vibrance", -100, 100, 0, 1)
        cl.addRow(self.tmp)
        cl.addRow(self.tnt)
        cl.addRow(self.sat)
        cl.addRow(self.vib)
        lay.addWidget(col)

        det = QGroupBox(t("detail"))
        dl = QFormLayout(det)
        dl.setSpacing(4)
        self.shp = self._mk(t("sharpness"), "sharpness", 0, 150, 0, 1)
        self.clr = self._mk(t("clarity"), "clarity", -100, 100, 0, 1)
        dl.addRow(self.shp)
        dl.addRow(self.clr)
        lay.addWidget(det)

        rb = QPushButton(t("reset_all"))
        rb.clicked.connect(self._reset_all)
        lay.addWidget(rb)

        eb = QPushButton(t("export_btn"))
        eb.setProperty("accent", "success")
        eb.clicked.connect(self.export_requested.emit)
        lay.addWidget(eb)
        lay.addStretch()

        self.setWidget(c)

    def _mk(self, name, key, mn, mx, df, st):
        r = SliderRow(name, key, mn, mx, df, st)
        r.value_changed.connect(self._on_val)
        return r

    def _on_val(self, key, val):
        if self._blk:
            return
        setattr(self._adj, key, val)
        self.adjustments_changed.emit(self._adj.copy())

    def _reset_all(self):
        self._block(True)
        self._adj.reset()
        for r in [self.exp, self.con, self.hi, self.sh, self.wh, self.bl,
                  self.tmp, self.tnt, self.sat, self.vib, self.shp, self.clr]:
            r._reset()
        self._block(False)
        self.adjustments_changed.emit(self._adj.copy())
        self.reset_requested.emit()

    def _block(self, b):
        self._blk = b

    def _on_preset_save(self):
        n = self.preset_name.text().strip()
        if n:
            self.preset_save_requested.emit(n, self._adj.copy())

    def _on_preset_load(self):
        n = self.preset_combo.currentText()
        if n and n != "-- wybierz --":
            self.preset_load_requested.emit(n)

    def _on_preset_delete(self):
        n = self.preset_combo.currentText()
        if n and n != "-- wybierz --":
            self.preset_delete_requested.emit(n)

    def set_preset_list(self, names):
        self.preset_combo.clear()
        self.preset_combo.addItem("-- wybierz --")
        for n in names:
            self.preset_combo.addItem(n)

    def set_adjustments(self, adj):
        self._block(True)
        self._adj = adj.copy()
        mapping = [
            (self.exp, "exposure", 0.1), (self.con, "contrast", 1),
            (self.hi, "highlights", 1), (self.sh, "shadows", 1),
            (self.wh, "whites", 1), (self.bl, "blacks", 1),
            (self.tmp, "temperature", 1), (self.tnt, "tint", 1),
            (self.sat, "saturation", 1), (self.vib, "vibrance", 1),
            (self.shp, "sharpness", 1), (self.clr, "clarity", 1),
        ]
        for row, key, step in mapping:
            val = getattr(adj, key)
            row.sli.setValue(int(val / step))
            row.lab.setText(f"{row._name}: {val:.1f}")
        self._block(False)
