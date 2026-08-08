#!/usr/bin/env python3
from __future__ import annotations
import logging
import rawpy
from pathlib import Path
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QSplitter, QVBoxLayout, QWidget
from config.defaults import DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH
from config.version import WINDOW_TITLE
from core.adjustments import Adjustments
from core.filters import pencil_sketch
from core.image_loader import SUPPORTED_FORMATS
from core.pipeline import prepare_preview, pil_to_cv, pil_to_qpixmap, apply_adjustments_arr, arr_to_pil
from core.preset_manager import save_preset, load_preset, list_presets
from core.worker import PipelineWorker
from ui.actions import ActionManager
from ui.canvas import Canvas
from ui.export_dialog import ExportDialog
from ui.histogram import HistogramWidget
from ui.menubar import MenuBar
from ui.panels.right_panel import RightPanel
from ui.statusbar import StatusBar
from ui.toolbar import ToolBar

class MainWindow(QMainWindow):
    def __init__(self, catalog=None):
        super().__init__()
        self.setStyleSheet("""
            QMainWindow { background: #1E1E1E; }
            QSplitter::handle { background: #333333; }
        """)
        self.actions = ActionManager(self)
        self._orig = None
        self._path = None
        self._preview_arr = None
        self._adj = Adjustments()
        self._worker = PipelineWorker(self)
        self._worker.finished.connect(self._on_preview_ready)
        self._ba_active = False
        self._build_ui()
        self._connect_actions()
        self.setAcceptDrops(True)

    def _build_ui(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.setMenuBar(MenuBar(self, self.actions))
        self.addToolBar(ToolBar(self, actions=self.actions))
        self.setStatusBar(StatusBar(self))
        splitter = QSplitter(Qt.Orientation.Horizontal)
        center = QWidget()
        center.setStyleSheet("background: #141414;")
        cl = QVBoxLayout(center)
        cl.setContentsMargins(0, 0, 0, 0)
        self.canvas = Canvas(self)
        cl.addWidget(self.canvas, stretch=1)
        self.histogram = HistogramWidget(self)
        cl.addWidget(self.histogram)
        splitter.addWidget(center)
        self.right_panel = RightPanel(self)
        self.right_panel.adjustments_changed.connect(self._on_adj)
        self.right_panel.reset_requested.connect(self._on_reset)
        self.right_panel.export_requested.connect(self._on_export)
        self.right_panel.preset_save_requested.connect(self._on_preset_save)
        self.right_panel.preset_load_requested.connect(self._on_preset_load)
        self.right_panel.preset_delete_requested.connect(self._on_preset_delete)
        splitter.addWidget(self.right_panel)
        splitter.setSizes([1200, 280])
        self.setCentralWidget(splitter)
        self._refresh_presets()
        self.statusBar().showMessage("Gotowy. Otworz zdjecie (Ctrl+O).")

    def _connect_actions(self):
        self.actions.open.triggered.connect(self._on_open)
        self.actions.exit.triggered.connect(self.close)
        self.actions.crop.triggered.connect(self._on_crop)
        self.actions.rotate_left.triggered.connect(lambda: self._on_rotate(90))
        self.actions.rotate_right.triggered.connect(lambda: self._on_rotate(-90))
        self.actions.flip_h.triggered.connect(lambda: self._on_flip(True, False))
        self.actions.flip_v.triggered.connect(lambda: self._on_flip(False, True))
        self.actions.before_after.triggered.connect(self._on_before_after)
        self.actions.pencil.triggered.connect(self._on_pencil)
        self.actions.batch.triggered.connect(self._on_batch_export)
        self.actions.zoom_in.triggered.connect(self._on_zin)
        self.actions.zoom_out.triggered.connect(self._on_zout)
        self.actions.actual_size.triggered.connect(self._on_z100)
        self.actions.fit.triggered.connect(self._on_fit)

    def _on_open(self):
        f = "Obrazy (" + " ".join("*" + e for e in SUPPORTED_FORMATS) + ")"
        p, _ = QFileDialog.getOpenFileName(self, "Otworz obraz", "", f)
        if p:
            self._load(Path(p))

    def _load(self, path):
        try:
            ext = path.suffix.lower()
            raw_exts = {".nef", ".cr2", ".cr3", ".arw", ".dng", ".orf", ".rw2", ".raf", ".pef"}
            
            # Pobierz EXIF orientation z pliku (dziala dla RAW i JPG)
            orientation = 1
            try:
                with Image.open(path) as tmp:
                    exif = tmp.getexif()
                    if exif:
                        orientation = exif.get(274, 1)
            except Exception:
                pass
            
            if ext in raw_exts:
                with rawpy.imread(str(path)) as raw:
                    rgb = raw.postprocess(use_camera_wb=True, no_auto_bright=False, output_bps=8)
                    self._orig = Image.fromarray(rgb)
            else:
                self._orig = Image.open(path)
            
            # Zastosuj EXIF orientation
            if orientation == 3:
                self._orig = self._orig.rotate(180, expand=True)
            elif orientation == 6:
                self._orig = self._orig.rotate(270, expand=True)
            elif orientation == 8:
                self._orig = self._orig.rotate(90, expand=True)
            
            # Konwertuj do RGB
            if self._orig.mode in ("RGBA", "P"):
                self._orig = self._orig.convert("RGBA")
                self._orig = self._orig.convert("RGB")
            elif self._orig.mode != "RGB":
                self._orig = self._orig.convert("RGB")
                
        except Exception as e:
            logging.error("Blad otwierania %s: %s", path, e)
            QMessageBox.critical(self, "Blad", "Nie mozna otworzyc: " + path.name)
            return
        preview = prepare_preview(self._orig, max_dim=800)
        self._preview_arr = pil_to_cv(preview)
        self._path = path
        self._adj.reset()
        self.right_panel._reset_all()
        self._ba_active = False
        self._render_now()
        self.statusBar().showMessage("Otwarto: " + path.name)
        sb = self.statusBar()
        if hasattr(sb, 'size_label'):
            sb.size_label.setText(str(self._orig.width) + " x " + str(self._orig.height))
        if hasattr(sb, 'format_label'):
            sb.format_label.setText(path.suffix.upper().replace(".", ""))

    def _on_crop(self):
        if self._orig is None:
            QMessageBox.warning(self, "Kadrowanie", "Najpierw otworz zdjecie.")
            return
        if self._ba_active:
            self._on_before_after()
        if self.canvas._crop_mode:
            rect = self.canvas.get_crop_rect()
            if rect:
                x1, y1, x2, y2 = rect
                # Przelicz wspolrzedne z podgladu (preview) na oryginal
                orig_w, orig_h = self._orig.width, self._orig.height
                preview_h, preview_w = self._preview_arr.shape[:2]
                scale_x = orig_w / preview_w
                scale_y = orig_h / preview_h
                x1 = int(x1 * scale_x)
                y1 = int(y1 * scale_y)
                x2 = int(x2 * scale_x)
                y2 = int(y2 * scale_y)
                # Clamp do wymiarow oryginalu
                x1 = max(0, min(x1, orig_w))
                y1 = max(0, min(y1, orig_h))
                x2 = max(0, min(x2, orig_w))
                y2 = max(0, min(y2, orig_h))
                if x2 - x1 < 2 or y2 - y1 < 2:
                    self.statusBar().showMessage("Zaznaczenie za male — anulowano.")
                else:
                    self._orig = self._orig.crop((x1, y1, x2, y2))
                    preview = prepare_preview(self._orig, max_dim=800)
                    self._preview_arr = pil_to_cv(preview)
                    self._render_now()
                    self.statusBar().showMessage(f"Przycieto: {self._orig.width} x {self._orig.height}")
                    sb = self.statusBar()
                    if hasattr(sb, 'size_label'):
                        sb.size_label.setText(str(self._orig.width) + " x " + str(self._orig.height))
            self.canvas.cancel_crop()
        else:
            self.canvas.start_crop()
            self.statusBar().showMessage("Tryb kadrowania: zaznacz prostokat, potem kliknij Kadruj.")

    def _on_rotate(self, angle):
        if self._orig is None:
            return
        self._orig = self._orig.rotate(angle, expand=True)
        preview = prepare_preview(self._orig, max_dim=800)
        self._preview_arr = pil_to_cv(preview)
        self._render_now()
        self.statusBar().showMessage(f"Obrocono: {self._orig.width} x {self._orig.height}")
        if hasattr(self, 'canvas'):
            self.canvas.update()

    def _on_flip(self, h, v):
        if self._orig is None:
            return
        if h:
            self._orig = self._orig.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if v:
            self._orig = self._orig.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        preview = prepare_preview(self._orig, max_dim=800)
        self._preview_arr = pil_to_cv(preview)
        self._render_now()
        self.statusBar().showMessage("Odbito obraz.")

    def _on_before_after(self):
        if self._orig is None:
            QMessageBox.warning(self, "Przed/Po", "Najpierw otworz zdjecie.")
            return
        if self._ba_active:
            self._ba_active = False
            self.canvas.cancel_before_after()
            self._render_now()
            self.statusBar().showMessage("Tryb normalny")
        else:
            self._ba_active = True
            self.canvas.cancel_crop()
            before = arr_to_pil(apply_adjustments_arr(self._preview_arr, Adjustments()))
            after = arr_to_pil(apply_adjustments_arr(self._preview_arr, self._adj))
            self.canvas.set_before_after(pil_to_qpixmap(before), pil_to_qpixmap(after))
            self.statusBar().showMessage("Przed/Po: przeciagaj linie podzialu")

    def _on_pencil(self):
        if self._orig is None:
            QMessageBox.warning(self, "Olowek", "Najpierw otworz zdjecie.")
            return
        if self._ba_active:
            self._on_before_after()
        self.canvas.cancel_crop()
        sketch = pencil_sketch(self._orig)
        preview = prepare_preview(sketch, max_dim=800)
        self.canvas.set_pixmap(pil_to_qpixmap(preview))
        self.statusBar().showMessage("Podglad: wersja olowkowa")
        answer = QMessageBox.question(
            self,
            "Olowek",
            "Zapisac wersje olowkowa jako nowy plik?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.Yes:
            suggested = "olowek.png"
            if self._path is not None:
                suggested = str(self._path.with_name(self._path.stem + "_olowek.png"))
            p, _ = QFileDialog.getSaveFileName(
                self,
                "Zapisz wersje olowkowa",
                suggested,
                "PNG (*.png);;JPEG (*.jpg *.jpeg)",
            )
            if p:
                try:
                    sketch.save(p)
                    self.statusBar().showMessage("Zapisano: " + Path(p).name)
                except Exception as e:
                    logging.error("Blad zapisu olowka: %s", e)
                    QMessageBox.critical(self, "Blad", "Nie mozna zapisac pliku.")
        self._render_now()

    def _on_batch_export(self):
        import numpy as np
        from ui.batch_dialog import BatchDialog
        dlg = BatchDialog(self)
        if dlg.exec() != BatchDialog.DialogCode.Accepted:
            return
        in_dir = Path(dlg.get_input_dir())
        out_dir = Path(dlg.get_output_dir())
        if not in_dir.exists() or not out_dir.exists():
            QMessageBox.warning(self, "Batch", "Wybierz poprawne foldery.")
            return
        exts = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp", ".gif", ".nef", ".cr2", ".arw", ".dng"}
        files = [f for f in in_dir.iterdir() if f.suffix.lower() in exts]
        if not files:
            QMessageBox.warning(self, "Batch", "Brak zdjec w folderze wejsciowym.")
            return
        fmt = dlg.get_format()
        quality = dlg.get_quality()
        scale = dlg.get_scale()
        suffix = dlg.get_suffix()
        total = len(files)
        for i, f in enumerate(files, 1):
            try:
                dlg.set_progress(i, total)
                img = Image.open(f)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGBA")
                else:
                    img = img.convert("RGB")
                arr = np.array(img, dtype=np.float32) / 255.0
                out_arr = apply_adjustments_arr(arr, self._adj)
                out_pil = arr_to_pil(out_arr)
                if scale != 1.0:
                    new_w = int(out_pil.width * scale)
                    new_h = int(out_pil.height * scale)
                    out_pil = out_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
                ext = {"JPEG": ".jpg", "PNG": ".png", "TIFF": ".tiff"}[fmt]
                out_path = out_dir / (f.stem + suffix + ext)
                if fmt == "JPEG":
                    out_pil = out_pil.convert("RGB")
                    out_pil.save(str(out_path), "JPEG", quality=quality, optimize=True)
                elif fmt == "PNG":
                    out_pil.save(str(out_path), "PNG")
                else:
                    out_pil.save(str(out_path), "TIFF")
            except Exception as e:
                logging.error("Blad %s: %s", f.name, e)
        self.statusBar().showMessage(f"Batch zakonczony: {total} plikow.")
        QMessageBox.information(self, "Batch", f"Wyeksportowano {total} zdjec.")

    def _on_adj(self, adj):
        self._adj = adj
        if self._ba_active:
            after = arr_to_pil(apply_adjustments_arr(self._preview_arr, self._adj))
            before = arr_to_pil(apply_adjustments_arr(self._preview_arr, Adjustments()))
            self.canvas.set_before_after(pil_to_qpixmap(before), pil_to_qpixmap(after))
            return
        if self._worker.isRunning():
            self._worker.wait(10)
        self._worker.set_job(self._preview_arr, self._adj.copy())
        self._worker.start()

    def _on_preview_ready(self, pil_img):
        if pil_img is None:
            return
        self.histogram.set_image(pil_img)
        self.canvas.set_pixmap(pil_to_qpixmap(pil_img))

    def _render_now(self):
        if self._preview_arr is None:
            return
        self._worker.set_job(self._preview_arr, self._adj.copy())
        self._worker.start()

    def _on_reset(self):
        self._adj.reset()
        self._render_now()

    def _on_export(self):
        if self._orig is None:
            QMessageBox.warning(self, "Eksport", "Najpierw otworz zdjecie.")
            return
        dlg = ExportDialog(self, self._orig.width, self._orig.height)
        if dlg.exec() != ExportDialog.DialogCode.Accepted:
            return
        path = dlg.get_path()
        if not path:
            return
        fmt = dlg.get_format()
        quality = dlg.get_quality()
        scale = dlg.get_scale()
        try:
            full = pil_to_cv(self._orig)
            out = apply_adjustments_arr(full, self._adj)
            pil_out = arr_to_pil(out)
            if scale != 1.0:
                new_w = int(pil_out.width * scale)
                new_h = int(pil_out.height * scale)
                pil_out = pil_out.resize((new_w, new_h), Image.Resampling.LANCZOS)
            if fmt == "PNG":
                pil_out.save(path, "PNG")
            elif fmt == "JPEG":
                pil_out = pil_out.convert("RGB")
                pil_out.save(path, "JPEG", quality=quality, optimize=True)
            elif fmt == "TIFF":
                pil_out.save(path, "TIFF")
            self.statusBar().showMessage("Wyeksportowano: " + Path(path).name)
        except Exception as e:
            QMessageBox.critical(self, "Blad eksportu", str(e))

    def _on_preset_save(self, name, adj):
        save_preset(name, adj)
        self._refresh_presets()
        self.statusBar().showMessage("Zapisano preset: " + name)

    def _on_preset_load(self, name):
        adj = load_preset(name)
        if adj:
            self.right_panel.set_adjustments(adj)
            self._adj = adj.copy()
            self._render_now()
            self.statusBar().showMessage("Wczytano preset: " + name)

    def _on_preset_delete(self, name):
        import os
        p = Path(__file__).resolve().parent.parent / "presets" / (name + ".json")
        if p.exists():
            os.remove(p)
            self._refresh_presets()
            self.statusBar().showMessage("Usunieto preset: " + name)

    def _refresh_presets(self):
        self.right_panel.set_preset_list(list_presets())

    def _on_zin(self):
        self.canvas._zoom = min(self.canvas._zoom * 1.25, 32.0)
        self.canvas.update()
        self.statusBar().showMessage("Zoom: " + str(int(self.canvas._zoom * 100)) + "%")

    def _on_zout(self):
        self.canvas._zoom = max(self.canvas._zoom / 1.25, 0.05)
        self.canvas.update()
        self.statusBar().showMessage("Zoom: " + str(int(self.canvas._zoom * 100)) + "%")

    def _on_z100(self):
        self.canvas._zoom = 1.0
        self.canvas.update()
        self.statusBar().showMessage("Zoom: 100%")

    def _on_fit(self):
        if self.canvas._pixmap and not self.canvas._pixmap.isNull():
            sw = self.canvas.width() / self.canvas._pixmap.width()
            sh = self.canvas.height() / self.canvas._pixmap.height()
            self.canvas._zoom = min(sw, sh) * 0.95
            self.canvas.update()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            p = Path(url.toLocalFile())
            if p.suffix.lower() in SUPPORTED_FORMATS:
                self._load(p)
                break
