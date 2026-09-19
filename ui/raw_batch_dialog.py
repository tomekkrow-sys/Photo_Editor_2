#!/usr/bin/env python3
"""RAW Batch Development dialog — develop RAW files with adjustments."""
from __future__ import annotations
import os
import time
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog,
    QFormLayout, QHBoxLayout, QLabel, QLineEdit, QProgressBar,
    QPushButton, QSlider, QVBoxLayout, QGroupBox, QSpinBox,
)
from config.i18n import t

RAW_EXTS = {".nef", ".cr2", ".cr3", ".arw", ".dng", ".orf", ".rw2", ".raf", ".pef", ".rwz", ".srw"}


class _RawBatchWorker(QThread):
    """Background thread for RAW development."""
    progress = Signal(int, int, str)  # current, total, filename
    finished = Signal(int, int, float)  # ok, errors, elapsed_seconds
    log = Signal(str)

    def __init__(self, tasks, parent=None):
        super().__init__(parent)
        self._tasks = tasks
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        import rawpy
        import numpy as np
        from PIL import Image

        ok = 0
        errors = 0
        total = len(self._tasks)
        t0 = time.time()

        for i, task in enumerate(self._tasks, 1):
            if self._cancel:
                self.log.emit("Anulowano.")
                break
            try:
                src = task["src"]
                dst = task["dst"]
                wb = task.get("wb", "camera")
                exposure = task.get("exposure", 0.0)
                denoise = task.get("denoise", 0)
                fmt = task.get("format", "JPEG")
                quality = task.get("quality", 95)
                resize = task.get("resize", 100)

                self.progress.emit(i, total, src.name)

                with rawpy.imread(str(src)) as raw:
                    # White balance
                    if wb == "camera":
                        wb_args = {"use_camera_wb": True}
                    elif wb == "auto":
                        wb_args = {"use_auto_wb": True}
                    elif wb == "daylight":
                        wb_args = {"use_camera_wb": False, "daylight": [2.0, 1.0, 1.2, 1.0]}
                    else:
                        wb_args = {"use_camera_wb": True}

                    rgb = raw.postprocess(
                        **wb_args,
                        no_auto_bright=False,
                        output_bps=16,
                    )

                img_arr = rgb.astype(np.float32) / 65535.0

                # Exposure adjustment
                if exposure != 0.0:
                    factor = 2.0 ** exposure
                    img_arr = np.clip(img_arr * factor, 0, 1)

                # Convert to 8-bit PIL
                img8 = (img_arr * 255).astype(np.uint8)
                pil_img = Image.fromarray(img8)

                # Denoise
                if denoise > 0:
                    import cv2
                    arr = np.array(pil_img)
                    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
                    bgr = cv2.fastNlMeansDenoisingColored(bgr, None, denoise, denoise, 7, 21)
                    pil_img = Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))

                # Resize
                if resize < 100:
                    factor = resize / 100.0
                    nw = int(pil_img.width * factor)
                    nh = int(pil_img.height * factor)
                    pil_img = pil_img.resize((nw, nh), Image.Resampling.LANCZOS)

                # Save
                dst.parent.mkdir(parents=True, exist_ok=True)
                if fmt == "JPEG":
                    pil_img = pil_img.convert("RGB")
                    pil_img.save(str(dst), "JPEG", quality=quality, optimize=True)
                elif fmt == "TIFF":
                    pil_img.save(str(dst), "TIFF")
                elif fmt == "PNG":
                    pil_img.save(str(dst), "PNG")
                elif fmt == "WebP":
                    pil_img.save(str(dst), "WebP", quality=quality)

                ok += 1
                self.log.emit(f"OK: {src.name} -> {dst.name}")
            except Exception as e:
                errors += 1
                self.log.emit(f"BLAD: {task['src'].name}: {e}")

        elapsed = time.time() - t0
        self.finished.emit(ok, errors, elapsed)


class RawBatchDialog(QDialog):
    """RAW batch development dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RAW Batch Development")
        self.setMinimumSize(600, 600)
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        # --- Input / Output ---
        io_group = QGroupBox("Foldery")
        io_lay = QFormLayout(io_group)

        in_row = QHBoxLayout()
        self.in_edit = QLineEdit()
        self.in_edit.setPlaceholderText("Folder z plikami RAW...")
        in_row.addWidget(self.in_edit)
        btn_in = QPushButton("...")
        btn_in.setFixedWidth(40)
        btn_in.clicked.connect(lambda: self._browse(self.in_edit, True))
        in_row.addWidget(btn_in)
        io_lay.addRow("Wejscie:", in_row)

        out_row = QHBoxLayout()
        self.out_edit = QLineEdit()
        self.out_edit.setPlaceholderText("Folder wynikowy...")
        out_row.addWidget(self.out_edit)
        btn_out = QPushButton("...")
        btn_out.setFixedWidth(40)
        btn_out.clicked.connect(lambda: self._browse(self.out_edit, True))
        out_row.addWidget(btn_out)
        io_lay.addRow("Wyjscie:", out_row)

        self.file_info = QLabel("")
        self.file_info.setStyleSheet("color: #aaa; font-size: 11px;")
        io_lay.addRow("", self.file_info)
        lay.addWidget(io_group)

        # --- RAW Development Settings ---
        dev_group = QGroupBox("Ustawienia wywolania RAW")
        dev_lay = QFormLayout(dev_group)

        # White balance
        self.wb_combo = QComboBox()
        self.wb_combo.addItems(["Auto (kamera)", "Auto (program)", "Dzienny"])
        dev_lay.addRow("Balance bieli:", self.wb_combo)

        # Exposure
        exp_row = QHBoxLayout()
        self.exp_slider = QSlider(Qt.Orientation.Horizontal)
        self.exp_slider.setRange(-30, 30)
        self.exp_slider.setValue(0)
        self.exp_label = QLabel("0 EV")
        self.exp_slider.valueChanged.connect(
            lambda v: self.exp_label.setText(f"{v/10:.1f} EV")
        )
        exp_row.addWidget(self.exp_slider)
        exp_row.addWidget(self.exp_label)
        dev_lay.addRow("Ekspozycja:", exp_row)

        # Denoise
        denoise_row = QHBoxLayout()
        self.denoise_slider = QSlider(Qt.Orientation.Horizontal)
        self.denoise_slider.setRange(0, 30)
        self.denoise_slider.setValue(0)
        self.denoise_label = QLabel("0 (wyl.)")
        self.denoise_slider.valueChanged.connect(
            lambda v: self.denoise_label.setText(str(v) if v > 0 else "0 (wyl.)")
        )
        denoise_row.addWidget(self.denoise_slider)
        denoise_row.addWidget(self.denoise_label)
        dev_lay.addRow("Redukcja szumu:", denoise_row)

        lay.addWidget(dev_group)

        # --- Output Settings ---
        out_group = QGroupBox("Ustawienia wyjscia")
        out_lay = QFormLayout(out_group)

        # Format
        self.fmt_combo = QComboBox()
        self.fmt_combo.addItems(["JPEG", "TIFF", "PNG", "WebP"])
        out_lay.addRow("Format:", self.fmt_combo)

        # Quality
        qual_row = QHBoxLayout()
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(95)
        self.quality_label = QLabel("95")
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_label.setText(str(v))
        )
        qual_row.addWidget(self.quality_slider)
        qual_row.addWidget(self.quality_label)
        out_lay.addRow("Jakosc:", qual_row)

        # Resize
        resize_row = QHBoxLayout()
        self.resize_slider = QSlider(Qt.Orientation.Horizontal)
        self.resize_slider.setRange(10, 100)
        self.resize_slider.setValue(100)
        self.resize_label = QLabel("100%")
        self.resize_slider.valueChanged.connect(
            lambda v: self.resize_label.setText(f"{v}%")
        )
        resize_row.addWidget(self.resize_slider)
        resize_row.addWidget(self.resize_label)
        out_lay.addRow("Rozmiar:", resize_row)

        # Subfolder
        self.subfolder_check = QCheckBox("Podfolder: wywolane/")
        self.subfolder_check.setChecked(True)
        out_lay.addRow("", self.subfolder_check)

        lay.addWidget(out_group)

        # --- Progress ---
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        lay.addWidget(self.progress)

        self.status_label = QLabel("Gotowy")
        lay.addWidget(self.status_label)

        # Log
        self.log_label = QLabel("")
        self.log_label.setStyleSheet("color: #888; font-size: 11px; max-height: 80px;")
        self.log_label.setWordWrap(True)
        lay.addWidget(self.log_label)

        # Buttons
        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.clicked.connect(self._on_start)
        self.cancel_btn = QPushButton(t("cancel"))
        self.cancel_btn.clicked.connect(self._on_cancel)
        self.cancel_btn.setEnabled(False)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.cancel_btn)
        lay.addLayout(btn_row)

        # Connect folder change
        self.in_edit.textChanged.connect(self._update_file_info)

    def _browse(self, edit, is_dir):
        if is_dir:
            folder = QFileDialog.getExistingDirectory(self, "Wybierz folder")
            if folder:
                edit.setText(folder)

    def _update_file_info(self):
        folder = self.in_edit.text()
        if not folder or not os.path.isdir(folder):
            self.file_info.setText("")
            return
        count = sum(
            1 for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in RAW_EXTS
        )
        self.file_info.setText(f"Znaleziono {count} plikow RAW")

    def _on_start(self):
        in_folder = self.in_edit.text()
        out_folder = self.out_edit.text()
        if not in_folder or not os.path.isdir(in_folder):
            return
        if not out_folder:
            return

        # Collect RAW files
        files = sorted([
            f for f in os.listdir(in_folder)
            if os.path.splitext(f)[1].lower() in RAW_EXTS
        ])
        if not files:
            self.status_label.setText("Brak plikow RAW w folderze wejściowym")
            return

        # Build tasks
        wb_map = {"Auto (kamera)": "camera", "Auto (program)": "auto", "Dzienny": "daylight"}
        wb = wb_map.get(self.wb_combo.currentText(), "camera")
        exposure = self.exp_slider.value() / 10.0
        denoise = self.denoise_slider.value()
        fmt = self.fmt_combo.currentText()
        quality = self.quality_slider.value()
        resize = self.resize_slider.value()
        subfolder = self.subfolder_check.isChecked()

        ext_map = {"JPEG": ".jpg", "TIFF": ".tiff", "PNG": ".png", "WebP": ".webp"}
        out_ext = ext_map.get(fmt, ".jpg")

        tasks = []
        for f in files:
            src = Path(in_folder) / f
            stem = Path(f).stem
            if subfolder:
                dst = Path(out_folder) / "wywolane" / (stem + out_ext)
            else:
                dst = Path(out_folder) / (stem + out_ext)
            tasks.append({
                "src": src,
                "dst": dst,
                "wb": wb,
                "exposure": exposure,
                "denoise": denoise,
                "format": fmt,
                "quality": quality,
                "resize": resize,
            })

        self.start_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress.setRange(0, len(tasks))
        self.status_label.setText(f"Przetwarzanie {len(tasks)} plikow...")

        self._worker = _RawBatchWorker(tasks)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.log.connect(self._on_log)
        self._worker.start()

    def _on_cancel(self):
        if self._worker:
            self._worker.cancel()

    def _on_progress(self, current, total, filename):
        self.progress.setValue(current)
        self.status_label.setText(f"[{current}/{total}] {filename}")

    def _on_finished(self, ok, errors, elapsed):
        self.start_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        mins = int(elapsed // 60)
        secs = int(elapsed % 60)
        self.status_label.setText(
            f"Gotowe: {ok} OK, {errors} bledow ({mins}m {secs}s)"
        )
        self.log_label.setText(f"Zakonczono: {ok} OK, {errors} bledow")

    def _on_log(self, msg):
        self.log_label.setText(msg)
