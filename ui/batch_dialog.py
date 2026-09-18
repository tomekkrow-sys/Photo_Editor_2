#!/usr/bin/env python3
"""Enhanced Batch Processing Dialog for Photo Editor 2."""
from __future__ import annotations
import json
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QProgressBar, QPushButton, QSlider, QSpinBox,
    QVBoxLayout, QWidget, QMessageBox, QGroupBox,
)
from config.i18n import t

FILTER_LIST = [
    ("resize", "resize"),
    ("blur", "blur"),
    ("sharpen", "sharpen"),
    ("black_white", "black_white"),
    ("sepia", "sepia"),
    ("negative", "negative"),
    ("vignette", "vignette"),
    ("emboss", "emboss"),
    ("hdr", "hdr"),
    ("cartoon", "cartoon"),
    ("pixelate", "pixelate"),
    ("denoise", "denoise"),
]

PRESETS_DIR = Path(__file__).resolve().parent.parent / "data" / "batch_presets"


class _BatchWorker(QThread):
    progress = Signal(int, int)  # current, total
    finished = Signal(int, int)  # success, errors
    log = Signal(str)

    def __init__(self, tasks, parent=None):
        super().__init__(parent)
        self._tasks = tasks
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        from PIL import Image, ImageEnhance, ImageFilter
        import core.filters as F

        ok = 0
        errors = 0
        total = len(self._tasks)
        for i, task in enumerate(self._tasks, 1):
            if self._cancel:
                self.log.emit("Anulowano.")
                break
            try:
                src = task["src"]
                dst = task["dst"]
                filters = task["filters"]
                fmt = task["format"]
                quality = task["quality"]
                scale = task.get("scale", 1.0)

                img = Image.open(str(src))
                if img.mode == "RGBA" and fmt == "JPEG":
                    img = img.convert("RGB")

                for filt_key, params in filters:
                    if self._cancel:
                        break
                    if filt_key == "resize" and scale != 1.0:
                        nw = int(img.width * scale)
                        nh = int(img.height * scale)
                        img = img.resize((nw, nh), Image.Resampling.LANCZOS)
                    elif filt_key == "blur":
                        k = params.get("kernel", 5)
                        img = F.gaussian_blur(img, kernel_size=k)
                    elif filt_key == "sharpen":
                        img = F.sharpen(img)
                    elif filt_key == "black_white":
                        img = F.black_and_white(img)
                    elif filt_key == "sepia":
                        img = F.sepia(img)
                    elif filt_key == "negative":
                        img = F.negative(img)
                    elif filt_key == "vignette":
                        img = F.vignette(img)
                    elif filt_key == "emboss":
                        img = F.emboss(img)
                    elif filt_key == "hdr":
                        img = F.hdr_tone_map(img)
                    elif filt_key == "cartoon":
                        img = F.cartoon(img)
                    elif filt_key == "pixelate":
                        img = F.pixelate(img, block_size=params.get("block", 8))
                    elif filt_key == "denoise":
                        img = F.denoise(img, strength=params.get("strength", 10))

                dst.parent.mkdir(parents=True, exist_ok=True)
                if fmt == "JPEG":
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    img.save(str(dst), "JPEG", quality=quality, optimize=True)
                elif fmt == "PNG":
                    img.save(str(dst), "PNG")
                elif fmt == "TIFF":
                    img.save(str(dst), "TIFF")
                elif fmt == "WebP":
                    img.save(str(dst), "WebP", quality=quality)

                ok += 1
                self.log.emit(f"OK: {src.name} -> {dst.name}")
            except Exception as e:
                errors += 1
                self.log.emit(f"BLAD: {task['src'].name}: {e}")
            self.progress.emit(i, total)

        self.finished.emit(ok, errors)


class BatchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("batch"))
        self.setMinimumSize(550, 520)
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        # --- Input / Output ---
        dirs_lay = QFormLayout()
        dirs_lay.setSpacing(6)

        in_row = QHBoxLayout()
        self.in_edit = QLineEdit()
        self.in_edit.setPlaceholderText(t("batch_input_hint") if t("batch_input_hint") != "batch_input_hint" else "Folder ze zdjeciami...")
        in_row.addWidget(self.in_edit)
        btn_in = QPushButton("...")
        btn_in.setFixedWidth(40)
        btn_in.clicked.connect(lambda: self._browse(self.in_edit, True))
        in_row.addWidget(btn_in)
        dirs_lay.addRow(t("batch_input") if t("batch_input") != "batch_input" else "Wejscie:", in_row)

        out_row = QHBoxLayout()
        self.out_edit = QLineEdit()
        self.out_edit.setPlaceholderText(t("batch_output_hint") if t("batch_output_hint") != "batch_output_hint" else "Folder wynikowy...")
        out_row.addWidget(self.out_edit)
        btn_out = QPushButton("...")
        btn_out.setFixedWidth(40)
        btn_out.clicked.connect(lambda: self._browse(self.out_edit, True))
        out_row.addWidget(btn_out)
        dirs_lay.addRow(t("batch_output") if t("batch_output") != "batch_output" else "Wyjscie:", out_row)

        lay.addLayout(dirs_lay)

        # --- Filters ---
        filt_group = QGroupBox(t("batch_filters") if t("batch_filters") != "batch_filters" else "Filtry do zastosowania")
        filt_lay = QVBoxLayout(filt_group)

        self.filter_list = QListWidget()
        self.filter_list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        for key, label_key in FILTER_LIST:
            item = QListWidgetItem(t(label_key))
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, key)
            self.filter_list.addItem(item)
        filt_lay.addWidget(self.filter_list)

        # Filter params row
        params_row = QHBoxLayout()
        params_row.addWidget(QLabel(t("batch_blur_kernel") if t("batch_blur_kernel") != "batch_blur_kernel" else "Rozmiar rozmycia:"))
        self.blur_spin = QSpinBox()
        self.blur_spin.setRange(1, 31)
        self.blur_spin.setSingleStep(2)
        self.blur_spin.setValue(5)
        params_row.addWidget(self.blur_spin)

        params_row.addWidget(QLabel(t("batch_pixel_block") if t("batch_pixel_block") != "batch_pixel_block" else "Blok pikseli:"))
        self.pixel_spin = QSpinBox()
        self.pixel_spin.setRange(2, 64)
        self.pixel_spin.setValue(8)
        params_row.addWidget(self.pixel_spin)
        filt_lay.addLayout(params_row)

        lay.addWidget(filt_group)

        # --- Export options ---
        export_group = QGroupBox(t("batch_export") if t("batch_export") != "batch_export" else "Eksport")
        exp_lay = QFormLayout(export_group)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["JPEG", "PNG", "WebP", "TIFF"])
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        exp_lay.addRow("Format:", self.format_combo)

        q_row = QHBoxLayout()
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(92)
        self.quality_label = QLabel("92")
        self.quality_slider.valueChanged.connect(lambda v: self.quality_label.setText(str(v)))
        q_row.addWidget(self.quality_slider)
        q_row.addWidget(self.quality_label)
        exp_lay.addRow("Jakosc:", q_row)

        self.scale_spin = QSpinBox()
        self.scale_spin.setRange(10, 200)
        self.scale_spin.setValue(100)
        self.scale_spin.setSuffix("%")
        exp_lay.addRow("Skalowanie:", self.scale_spin)

        self.suffix_edit = QLineEdit("_edited")
        exp_lay.addRow("Sufiks:", self.suffix_edit)

        lay.addWidget(export_group)

        # --- Presets ---
        preset_row = QHBoxLayout()
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(150)
        self._refresh_presets()
        preset_row.addWidget(self.preset_combo)

        load_btn = QPushButton(t("preset_load"))
        load_btn.clicked.connect(self._load_preset)
        preset_row.addWidget(load_btn)

        save_btn = QPushButton(t("preset_save"))
        save_btn.clicked.connect(self._save_preset)
        preset_row.addWidget(save_btn)

        del_btn = QPushButton(t("preset_delete"))
        del_btn.clicked.connect(self._delete_preset)
        preset_row.addWidget(del_btn)
        preset_row.addStretch()
        lay.addLayout(preset_row)

        # --- Progress ---
        self.progress = QProgressBar()
        self.progress.setValue(0)
        lay.addWidget(self.progress)

        self.status_label = QLabel("Gotowy")
        lay.addWidget(self.status_label)

        self.log_label = QLabel("")
        self.log_label.setStyleSheet("color: #888; font-size: 10px;")
        self.log_label.setWordWrap(True)
        lay.addWidget(self.log_label)

        # --- Buttons ---
        btns = QHBoxLayout()
        self._cancel_btn = QPushButton(t("cancel"))
        self._cancel_btn.setEnabled(False)
        self._cancel_btn.clicked.connect(self._on_cancel)
        btns.addWidget(self._cancel_btn)
        btns.addStretch()

        self._ok_btn = QPushButton(t("batch_start") if t("batch_start") != "batch_start" else "Start")
        self._ok_btn.setStyleSheet("background: #2E7D32; color: white; font-weight: bold;")
        self._ok_btn.clicked.connect(self._on_start)
        btns.addWidget(self._ok_btn)

        cancel_all = QPushButton(t("cancel"))
        cancel_all.clicked.connect(self.reject)
        btns.addWidget(cancel_all)

        lay.addLayout(btns)

    def _browse(self, edit, is_dir):
        p = QFileDialog.getExistingDirectory(self, "Wybierz folder")
        if p:
            edit.setText(p)

    def _on_format_changed(self, fmt):
        self.quality_slider.setEnabled(fmt in ("JPEG", "WebP"))

    def _get_selected_filters(self):
        filters = []
        for i in range(self.filter_list.count()):
            item = self.filter_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                key = item.data(Qt.ItemDataRole.UserRole)
                params = {}
                if key == "blur":
                    params["kernel"] = self.blur_spin.value()
                elif key == "pixelate":
                    params["block"] = self.pixel_spin.value()
                filters.append((key, params))
        return filters

    def _on_start(self):
        in_dir = Path(self.in_edit.text())
        out_dir = Path(self.out_edit.text())
        if not in_dir.exists() or not out_dir.exists():
            QMessageBox.warning(self, t("batch"), "Wybierz poprawne foldery.")
            return

        ext_map = {"JPEG": ".jpg", "PNG": ".png", "WebP": ".webp", "TIFF": ".tiff"}
        fmt = self.format_combo.currentText()
        quality = self.quality_slider.value()
        scale = self.scale_spin.value() / 100.0
        suffix = self.suffix_edit.text().strip()
        filters = self._get_selected_filters()

        ext = ext_map[fmt]
        supported = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
        files = [f for f in in_dir.iterdir() if f.suffix.lower() in supported]
        if not files:
            QMessageBox.warning(self, t("batch"), "Brak zdjec w folderze.")
            return

        tasks = []
        for f in files:
            out_name = f.stem + suffix + ext
            tasks.append({
                "src": f,
                "dst": out_dir / out_name,
                "filters": filters,
                "format": fmt,
                "quality": quality,
                "scale": scale,
            })

        self._ok_btn.setEnabled(False)
        self._cancel_btn.setEnabled(True)
        self.progress.setMaximum(len(tasks))
        self.progress.setValue(0)
        self.status_label.setText("Przetwarzanie...")

        self._worker = _BatchWorker(tasks)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.log.connect(self._on_log)
        self._worker.start()

    def _on_progress(self, cur, total):
        self.progress.setValue(cur)
        self.status_label.setText(f"{cur}/{total}")

    def _on_finished(self, ok, errors):
        self._ok_btn.setEnabled(True)
        self._cancel_btn.setEnabled(False)
        msg = f"Gotowe: {ok} OK, {errors} bledow."
        self.status_label.setText(msg)
        QMessageBox.information(self, t("batch"), msg)

    def _on_log(self, msg):
        self.log_label.setText(msg)

    def _on_cancel(self):
        if self._worker:
            self._worker.cancel()

    # --- Presets ---
    def _refresh_presets(self):
        self.preset_combo.clear()
        PRESETS_DIR.mkdir(parents=True, exist_ok=True)
        for p in sorted(PRESETS_DIR.glob("*.json")):
            self.preset_combo.addItem(p.stem)

    def _save_preset(self):
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, t("preset_save"), t("preset_name_placeholder"))
        if not ok or not name.strip():
            return
        data = {
            "filters": [item.data(Qt.ItemDataRole.UserRole)
                        for i in range(self.filter_list.count())
                        if (item := self.filter_list.item(i)).checkState() == Qt.CheckState.Checked],
            "format": self.format_combo.currentText(),
            "quality": self.quality_slider.value(),
            "scale": self.scale_spin.value(),
            "suffix": self.suffix_edit.text(),
            "blur_kernel": self.blur_spin.value(),
            "pixel_block": self.pixel_spin.value(),
        }
        path = PRESETS_DIR / f"{name.strip()}.json"
        path.write_text(json.dumps(data, indent=2))
        self._refresh_presets()
        self.preset_combo.setCurrentText(name.strip())

    def _load_preset(self):
        name = self.preset_combo.currentText()
        if not name:
            return
        path = PRESETS_DIR / f"{name}.json"
        if not path.exists():
            return
        data = json.loads(path.read_text())

        # Reset all
        for i in range(self.filter_list.count()):
            item = self.filter_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)

        active = data.get("filters", [])
        for i in range(self.filter_list.count()):
            item = self.filter_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) in active:
                item.setCheckState(Qt.CheckState.Checked)

        if "format" in data:
            idx = self.format_combo.findText(data["format"])
            if idx >= 0:
                self.format_combo.setCurrentIndex(idx)
        if "quality" in data:
            self.quality_slider.setValue(data["quality"])
        if "scale" in data:
            self.scale_spin.setValue(data["scale"])
        if "suffix" in data:
            self.suffix_edit.setText(data["suffix"])
        if "blur_kernel" in data:
            self.blur_spin.setValue(data["blur_kernel"])
        if "pixel_block" in data:
            self.pixel_spin.setValue(data["pixel_block"])

    def _delete_preset(self):
        name = self.preset_combo.currentText()
        if not name:
            return
        path = PRESETS_DIR / f"{name}.json"
        if path.exists():
            path.unlink()
        self._refresh_presets()
