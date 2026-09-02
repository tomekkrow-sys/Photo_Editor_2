#!/usr/bin/env python3
from __future__ import annotations
import logging
import time
import rawpy
from pathlib import Path
from PIL import Image
from PySide6.QtCore import Qt, QPointF, QSettings
from PySide6.QtGui import QColor, QGuiApplication, QPixmap
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QSplitter, QVBoxLayout, QWidget
from config.defaults import DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH
from config.version import WINDOW_TITLE
from core.adjustments import Adjustments
from core.filters import (
    auto_enhance,
    black_and_white,
    composite,
    emboss,
    frame,
    gaussian_blur,
    negative,
    pencil_sketch,
    sepia,
    sharpen,
    straighten,
    vignette,
    watermark,
)
from core.history import EditHistory
from core.image_loader import SUPPORTED_FORMATS
from core.pipeline import prepare_preview, pil_to_cv, pil_to_qpixmap, pil_to_qimage, qimage_to_pil, apply_adjustments_arr, arr_to_pil
from core.preset_manager import save_preset, load_preset, list_presets
from core.tools.brush_tool import BrushMode, BrushTool
from core.tools.spot_tool import SpotTool
from core.worker import PipelineWorker
from ui.actions import ActionManager
from ui.canvas import Canvas
from ui.export_dialog import ExportDialog
from ui.histogram import HistogramWidget
from ui.menubar import MenuBar
from ui.panels.right_panel import RightPanel
from ui.statusbar import StatusBar
from ui.toolbar import ToolBar

RAW_EXTS = {".nef", ".cr2", ".cr3", ".arw", ".dng", ".orf", ".rw2", ".raf", ".pef"}

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
        self._history = EditHistory()
        self._adj_history = EditHistory(limit=30)
        self._adj_last_push = 0.0
        self._suppress_adj_push = False
        self._spot = SpotTool()
        self._spot_size = None
        self._brush = BrushTool()
        self._brush_size = None
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
        self._refresh_recent_menu()
        self.statusBar().showMessage("Gotowy. Otworz zdjecie (Ctrl+O).")

    def _connect_actions(self):
        self.actions.new.triggered.connect(self._on_new)
        self.actions.open.triggered.connect(self._on_open)
        self.actions.save.triggered.connect(self._on_save)
        self.actions.save_as.triggered.connect(self._on_save_as)
        self.actions.export.triggered.connect(self._on_export)
        self.actions.undo.triggered.connect(self._on_undo)
        self.actions.redo.triggered.connect(self._on_redo)
        self.actions.cut.triggered.connect(self._on_cut)
        self.actions.copy.triggered.connect(self._on_copy)
        self.actions.paste.triggered.connect(self._on_paste)
        self.actions.delete.triggered.connect(self._on_delete)
        self.actions.exit.triggered.connect(self.close)
        self.actions.crop.triggered.connect(self._on_crop)
        self.actions.spot.triggered.connect(self._on_spot_toggle)
        self.canvas.spot_clicked.connect(self._on_spot_click)
        self.canvas.spot_wheel.connect(self._on_spot_wheel)
        self.actions.brush.triggered.connect(self._on_brush_toggle)
        self.canvas.brush_stroke.connect(self._on_brush_stroke)
        self.canvas.brush_wheel.connect(self._on_brush_wheel)
        self.actions.frame.triggered.connect(self._on_frame)
        self.actions.info.triggered.connect(self._on_info)
        self.actions.compare.triggered.connect(self._on_compare)
        self.actions.overlay.triggered.connect(self._on_overlay)
        self.actions.straighten.triggered.connect(self._on_straighten)
        self.actions.watermark.triggered.connect(self._on_watermark)
        self.actions.rotate_left.triggered.connect(lambda: self._on_rotate(90))
        self.actions.rotate_right.triggered.connect(lambda: self._on_rotate(-90))
        self.actions.flip_h.triggered.connect(lambda: self._on_flip(True, False))
        self.actions.flip_v.triggered.connect(lambda: self._on_flip(False, True))
        self.actions.before_after.triggered.connect(self._on_before_after)
        self.actions.pencil.triggered.connect(self._on_pencil)
        self.actions.black_white.triggered.connect(self._on_black_white)
        self.actions.sepia.triggered.connect(self._on_sepia)
        self.actions.negative.triggered.connect(self._on_negative)
        self.actions.gaussian_blur.triggered.connect(self._on_gaussian_blur)
        self.actions.sharpen.triggered.connect(self._on_sharpen)
        self.actions.emboss.triggered.connect(self._on_emboss)
        self.actions.vignette.triggered.connect(self._on_vignette)
        self.actions.auto_enhance.triggered.connect(self._on_auto_enhance)

        self.actions.resize_image.triggered.connect(self._on_resize)
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

    def _recent_list(self) -> list:
        value = QSettings("PhotoEditor2", "PhotoEditor2").value(
            "recentFiles", []
        )
        if isinstance(value, str):
            return [value] if value else []
        return list(value or [])

    def _add_recent(self, path) -> None:
        entries = self._recent_list()
        p = str(path)
        if p in entries:
            entries.remove(p)
        entries.insert(0, p)
        QSettings("PhotoEditor2", "PhotoEditor2").setValue(
            "recentFiles", entries[:8]
        )
        self._refresh_recent_menu()

    def _refresh_recent_menu(self) -> None:
        menu = getattr(self.menuBar(), "recent_menu", None)
        if menu is None:
            return
        menu.clear()
        entries = self._recent_list()
        if not entries:
            menu.addAction("(pusto)").setEnabled(False)
            return
        for p in entries:
            action = menu.addAction(Path(p).name)
            action.setToolTip(p)
            action.triggered.connect(
                lambda checked=False, path=p: self._open_recent(path)
            )

    def _open_recent(self, path_str: str) -> None:
        path = Path(path_str)
        if path.is_file():
            self._load(path)
        else:
            entries = self._recent_list()
            if path_str in entries:
                entries.remove(path_str)
                QSettings("PhotoEditor2", "PhotoEditor2").setValue(
                    "recentFiles", entries
                )
            self._refresh_recent_menu()
            self.statusBar().showMessage("Plik nie istnieje: " + path.name)

    def _open_image(self, path):
        """Open an image file (including RAW) as an RGB PIL image.

        Applies EXIF orientation. Returns None on failure.
        """

        try:
            orientation = 1
            try:
                with Image.open(path) as tmp:
                    exif = tmp.getexif()
                    if exif:
                        orientation = exif.get(274, 1)
            except Exception:
                pass

            if path.suffix.lower() in RAW_EXTS:
                with rawpy.imread(str(path)) as raw:
                    rgb = raw.postprocess(
                        use_camera_wb=True,
                        no_auto_bright=False,
                        output_bps=8,
                    )
                img = Image.fromarray(rgb)
            else:
                img = Image.open(path)
                img.load()

            if orientation == 3:
                img = img.rotate(180, expand=True)
            elif orientation == 6:
                img = img.rotate(270, expand=True)
            elif orientation == 8:
                img = img.rotate(90, expand=True)

            if img.mode in ("RGBA", "P"):
                img = img.convert("RGBA").convert("RGB")
            elif img.mode != "RGB":
                img = img.convert("RGB")
            return img
        except Exception as e:
            logging.error("Blad otwierania %s: %s", path, e)
            return None

    def _load(self, path):
        self._orig = self._open_image(path)
        if self._orig is None:
            QMessageBox.critical(self, "Blad", "Nie mozna otworzyc: " + path.name)
            return
        preview = prepare_preview(self._orig, max_dim=800)
        self._preview_arr = pil_to_cv(preview)
        self._path = path
        self._history.clear()
        self._spot_size = None
        self._brush_size = None
        self._reset_adjustment_state()
        self._ba_active = False
        self._render_now()
        self._add_recent(path)
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
        self.canvas.cancel_spot()
        self.canvas.cancel_brush()
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
                    self._history.push(self._orig)
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

    def _on_spot_toggle(self):
        if self._orig is None:
            QMessageBox.warning(self, "Usun obiekt", "Najpierw otworz zdjecie.")
            return
        if self._ba_active:
            self._on_before_after()
        if self.canvas._spot_mode:
            self.canvas.cancel_spot()
            self.statusBar().showMessage("Tryb retuszu wylaczony.")
        else:
            self.canvas.cancel_crop()
            self.canvas.cancel_brush()
            self.canvas.start_spot()
            self.statusBar().showMessage(
                "Retusz: kliknij element do usuniecia. "
                "Kolko myszy zmienia rozmiar. "
                "Ponowne klikniecie przycisku wylacza tryb."
            )

    def _spot_auto_size(self) -> int:
        return max(24, min(300, max(self._orig.width, self._orig.height) // 20))

    def _on_spot_wheel(self, delta: int):
        if self._orig is None:
            return
        if self._spot_size is None:
            self._spot_size = self._spot_auto_size()
        factor = 1.2 if delta > 0 else 1 / 1.2
        self._spot_size = int(max(8, min(500, self._spot_size * factor)))
        self.statusBar().showMessage(f"Retusz: rozmiar {self._spot_size}px")

    def _on_spot_click(self, preview_pos):
        if self._orig is None or self._preview_arr is None:
            return
        preview_h, preview_w = self._preview_arr.shape[:2]
        scale_x = self._orig.width / preview_w
        scale_y = self._orig.height / preview_h
        x = preview_pos.x() * scale_x
        y = preview_pos.y() * scale_y
        size = self._spot_size if self._spot_size is not None else self._spot_auto_size()
        r = size / 2
        qimg = pil_to_qimage(self._orig)
        sx = x + size * 2
        if sx + r > qimg.width():
            sx = x - size * 2
        sx = max(r, min(sx, qimg.width() - r))
        sy = max(r, min(y, qimg.height() - r))
        self._spot.settings.size = size
        self._spot.set_sample_source(QPointF(sx, sy), qimg)
        self._spot.begin_paint(QPointF(x, y), qimg)
        self._spot.finish_paint()
        self._history.push(self._orig)
        self._orig = qimage_to_pil(qimg)
        self._refresh_after_edit()
        self.statusBar().showMessage("Usunieto element (Ctrl+Z cofa).")

    def _on_rotate(self, angle):
        if self._orig is None:
            return
        self._history.push(self._orig)
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
        self._history.push(self._orig)
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
        self._run_filter(pencil_sketch, "Olowek", "_olowek.png")

    def _on_black_white(self):
        self._run_filter(black_and_white, "Czarno-biale", "_bw.png")

    def _on_sepia(self):
        self._run_filter(sepia, "Sepia", "_sepia.png")

    def _on_negative(self):
        self._run_filter(negative, "Negatyw", "_negatyw.png")



    def _on_gaussian_blur(self):
        self._run_filter(gaussian_blur, "Rozmycie Gaussa", "_gaussian.png")

    def _on_sharpen(self):
        self._run_filter(sharpen, "Ostrzenie", "_sharpen.png")

    def _on_emboss(self):
        self._run_filter(emboss, "Wydrążenie", "_emboss.png")

    def _on_vignette(self):
        self._run_filter(vignette, "Winieta", "_winieta.png")

    def _on_frame(self):
        self._run_filter(frame, "Ramka", "_ramka.png")

    def _on_brush_toggle(self):
        if self._orig is None:
            QMessageBox.warning(self, "Pedzel korekt", "Najpierw otworz zdjecie.")
            return
        if self._ba_active:
            self._on_before_after()
        if self.canvas._brush_mode:
            self.canvas.cancel_brush()
            self.statusBar().showMessage("Pedzel wylaczony.")
        else:
            self.canvas.cancel_crop()
            self.canvas.cancel_spot()
            self.canvas.start_brush()
            self.statusBar().showMessage(
                "Pedzel: lewy przycisk rozjasnia, prawy przyciemnia, "
                "kolko myszy zmienia rozmiar."
            )

    def _on_brush_wheel(self, delta: int):
        if self._orig is None:
            return
        if self._brush_size is None:
            self._brush_size = 40
        factor = 1.2 if delta > 0 else 1 / 1.2
        self._brush_size = int(max(4, min(300, self._brush_size * factor)))
        self.statusBar().showMessage(f"Pedzel: rozmiar {self._brush_size}px")

    def _on_brush_stroke(self, points, button):
        if self._orig is None or self._preview_arr is None or not points:
            return
        preview_h, preview_w = self._preview_arr.shape[:2]
        scale_x = self._orig.width / preview_w
        scale_y = self._orig.height / preview_h
        size = (self._brush_size or 40) * scale_x
        dodge = button != Qt.MouseButton.RightButton
        qimg = pil_to_qimage(self._orig)
        self._brush.settings.size = size
        self._brush.settings.opacity = 0.25
        self._brush.settings.flow = 1.0
        self._brush.settings.mode = (
            BrushMode.DODGE if dodge else BrushMode.BURN
        )
        self._brush.settings.color = (
            QColor("white") if dodge else QColor("black")
        )
        orig_points = [
            QPointF(p.x() * scale_x, p.y() * scale_y) for p in points
        ]
        self._history.push(self._orig)
        self._brush.begin(orig_points[0], qimg)
        for p in orig_points[1:]:
            self._brush.update(p, qimg)
        self._brush.finish()
        self._orig = qimage_to_pil(qimg)
        self._refresh_after_edit()
        self.statusBar().showMessage(
            "Pedzel: rozjasniono." if dodge else "Pedzel: przyciemniono."
        )

    def _on_info(self):
        if self._orig is None:
            QMessageBox.warning(self, "Informacje", "Najpierw otworz zdjecie.")
            return
        QMessageBox.information(
            self, "Informacje o zdjeciu", self._build_info_text()
        )

    def _build_info_text(self) -> str:
        lines = [f"Wymiary: {self._orig.width} x {self._orig.height} px"]
        if self._path is not None:
            lines.append(f"Plik: {self._path.name}")
            lines.append(f"Folder: {self._path.parent}")
            try:
                stat = self._path.stat()
                lines.append(f"Rozmiar: {stat.st_size / 1024 / 1024:.1f} MB")
                with Image.open(self._path) as im:
                    exif = im.getexif()
                tags = {
                    272: "Aparat", 271: "Producent", 305: "Program",
                    42036: "Obiektyw", 34855: "ISO", 33434: "Czas [s]",
                    33437: "Przyslona", 37386: "Ogniskowa [mm]",
                    36867: "Data wykonania",
                }
                for tag, label in tags.items():
                    value = exif.get(tag) if exif else None
                    if value:
                        lines.append(f"{label}: {value}")
            except Exception as e:
                logging.debug("Brak EXIF dla %s: %s", self._path, e)
        return "\n".join(lines)

    def _on_overlay(self):
        if self._orig is None:
            QMessageBox.warning(self, "Warstwa", "Najpierw otworz zdjecie.")
            return
        f = "Obrazy (" + " ".join("*" + e for e in SUPPORTED_FORMATS) + ")"
        p, _ = QFileDialog.getOpenFileName(self, "Naloz warstwe z pliku", "", f)
        if not p:
            return
        layer = self._open_image(Path(p))
        if layer is None:
            QMessageBox.critical(self, "Blad", "Nie mozna otworzyc: " + Path(p).name)
            return
        from ui.overlay_dialog import OverlayDialog
        dlg = OverlayDialog(self, Path(p).name)
        if dlg.exec() != OverlayDialog.DialogCode.Accepted:
            return
        self.apply_overlay(layer, dlg.get_opacity(), dlg.get_mode())

    def apply_overlay(self, layer, opacity: float, mode: str) -> bool:
        """Composite an overlay layer onto the current image (undoable)."""

        if self._orig is None or layer is None:
            return False
        self._history.push(self._orig)
        self._orig = composite(self._orig, layer, opacity, mode)
        self._refresh_after_edit()
        self.statusBar().showMessage(
            f"Nalozono warstwe ({mode}, {int(opacity * 100)}%)."
        )
        return True

    def _on_straighten(self):
        if self._orig is None:
            QMessageBox.warning(self, "Wyprostuj", "Najpierw otworz zdjecie.")
            return
        from ui.straighten_dialog import StraightenDialog
        dlg = StraightenDialog(self)
        if dlg.exec() != StraightenDialog.DialogCode.Accepted:
            return
        self.apply_straighten(dlg.get_angle())

    def apply_straighten(self, angle: float) -> bool:
        """Rotate by an arbitrary angle with auto-crop (undoable)."""

        if self._orig is None:
            return False
        self._history.push(self._orig)
        self._orig = straighten(self._orig, angle)
        self._refresh_after_edit()
        self.statusBar().showMessage(
            f"Wyprostowano ({angle:+.1f}°). Ctrl+Z cofa."
        )
        return True

    def _on_watermark(self):
        if self._orig is None:
            QMessageBox.warning(self, "Znak wodny", "Najpierw otworz zdjecie.")
            return
        from ui.watermark_dialog import WatermarkDialog
        dlg = WatermarkDialog(self)
        if dlg.exec() != WatermarkDialog.DialogCode.Accepted:
            return
        if not dlg.get_text():
            self.statusBar().showMessage("Znak wodny: pusty tekst — anulowano.")
            return
        self.apply_watermark(dlg.get_text(), dlg.get_position(), dlg.get_opacity())

    def apply_watermark(self, text: str, position: str, opacity: float) -> bool:
        """Draw a text watermark on the current image (undoable)."""

        if self._orig is None or not text:
            return False
        self._history.push(self._orig)
        self._orig = watermark(self._orig, text, position, opacity)
        self._refresh_after_edit()
        self.statusBar().showMessage("Dodano znak wodny. Ctrl+Z cofa.")
        return True

    def _on_compare(self):
        if self._orig is None:
            QMessageBox.warning(self, "Porownaj", "Najpierw otworz zdjecie.")
            return
        if self._ba_active:
            self._on_before_after()
            return
        f = "Obrazy (" + " ".join("*" + e for e in SUPPORTED_FORMATS) + ")"
        p, _ = QFileDialog.getOpenFileName(self, "Porownaj z plikiem", "", f)
        if not p:
            return
        other = self._open_image(Path(p))
        if other is None:
            QMessageBox.critical(self, "Blad", "Nie mozna otworzyc: " + Path(p).name)
            return
        self.canvas.cancel_crop()
        self._ba_active = True
        before = arr_to_pil(apply_adjustments_arr(self._preview_arr, self._adj))
        other_preview = prepare_preview(other, max_dim=800)
        self.canvas.set_before_after(
            pil_to_qpixmap(before), pil_to_qpixmap(other_preview)
        )
        self.statusBar().showMessage(
            "Porownanie: lewo = biezace zdjecie, prawo = " + Path(p).name
            + ". Przeciagaj linie podzialu."
        )

    def _on_auto_enhance(self):
        if self._orig is None:
            QMessageBox.warning(self, "Auto-korekta", "Najpierw otworz zdjecie.")
            return
        self._history.push(self._orig)
        self._orig = auto_enhance(self._orig)
        self._refresh_after_edit()
        self.statusBar().showMessage("Zastosowano auto-korekte (Ctrl+Z cofa).")

    def _on_resize(self):
        if self._orig is None:
            QMessageBox.warning(self, "Zmien rozmiar", "Najpierw otworz zdjecie.")
            return
        from ui.resize_dialog import ResizeDialog
        dlg = ResizeDialog(self, self._orig.width, self._orig.height)
        if dlg.exec() != ResizeDialog.DialogCode.Accepted:
            return
        w, h = dlg.get_size()
        self._resize_image(w, h)

    def _resize_image(self, width: int, height: int) -> bool:
        if self._orig is None or width <= 0 or height <= 0:
            return False
        self._history.push(self._orig)
        self._orig = self._orig.resize(
            (width, height), Image.Resampling.LANCZOS
        )
        self._refresh_after_edit()
        self.statusBar().showMessage(f"Zmieniono rozmiar: {width} x {height}")
        return True

    def _run_filter(self, func, name, suffix):
        """Preview a filter on the full image, offer save-as-new-file."""

        if self._orig is None:
            QMessageBox.warning(self, name, "Najpierw otworz zdjecie.")
            return
        if self._ba_active:
            self._on_before_after()
        self.canvas.cancel_crop()
        result = func(self._orig)
        preview = prepare_preview(result, max_dim=800)
        self.canvas.set_pixmap(pil_to_qpixmap(preview))
        self.statusBar().showMessage("Podglad: " + name)
        answer = QMessageBox.question(
            self,
            name,
            "Zapisac wersje '" + name + "' jako nowy plik?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer == QMessageBox.StandardButton.Yes:
            suggested = "filtr.png"
            if self._path is not None:
                suggested = str(self._path.with_name(self._path.stem + suffix))
            p, _ = QFileDialog.getSaveFileName(
                self,
                "Zapisz: " + name,
                suggested,
                "PNG (*.png);;JPEG (*.jpg *.jpeg)",
            )
            if p:
                try:
                    result.save(p)
                    logging.info("Zapisano filtr %s: %s", name, p)
                    self.statusBar().showMessage("Zapisano: " + Path(p).name)
                except Exception as e:
                    logging.error("Blad zapisu filtra %s: %s", name, e)
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
            QMessageBox.warning(self, "Konwerter folderu", "Wybierz poprawne foldery.")
            return
        files = [f for f in in_dir.iterdir() if f.suffix.lower() in SUPPORTED_FORMATS]
        if not files:
            QMessageBox.warning(self, "Konwerter folderu", "Brak zdjec w folderze wejsciowym.")
            return
        fmt = dlg.get_format()
        quality = dlg.get_quality()
        scale = dlg.get_scale()
        suffix = dlg.get_suffix()
        total = len(files)
        for i, f in enumerate(files, 1):
            try:
                dlg.set_progress(i, total)
                img = self._open_image(f)
                if img is None:
                    continue
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
        self.statusBar().showMessage(f"Konwersja zakonczona: {total} plikow.")
        QMessageBox.information(self, "Konwerter folderu", f"Wyeksportowano {total} zdjec.")

    def _reset_adjustment_state(self):
        """Reset adjustments and their history without a history push."""

        self._adj.reset()
        self._adj_history.clear()
        self._adj_last_push = 0.0
        self._suppress_adj_push = True
        self.right_panel._reset_all()
        self._suppress_adj_push = False

    def _on_adj(self, adj):
        now = time.monotonic()
        if not self._suppress_adj_push and now - self._adj_last_push > 0.8:
            self._adj_history.push(self._adj)
        if not self._suppress_adj_push:
            self._adj_last_push = now
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

    def _on_new(self):
        self._orig = Image.new("RGB", (1920, 1080), (255, 255, 255))
        self._path = None
        self._history.clear()
        self._reset_adjustment_state()
        preview = prepare_preview(self._orig, max_dim=800)
        self._preview_arr = pil_to_cv(preview)
        self._render_now()
        self.statusBar().showMessage("Nowy obraz 1920 x 1080")

    def _on_save(self):
        if self._orig is None:
            QMessageBox.warning(self, "Zapisz", "Najpierw otworz zdjecie.")
            return
        if self._path is None or self._path.suffix.lower() in RAW_EXTS:
            self._on_save_as()
            return
        answer = QMessageBox.question(
            self,
            "Zapisz",
            "Nadpisac oryginalny plik " + self._path.name + "?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes and self._save_to(str(self._path)):
            self.statusBar().showMessage("Zapisano: " + self._path.name)

    def _on_save_as(self):
        if self._orig is None:
            QMessageBox.warning(self, "Zapisz jako", "Najpierw otworz zdjecie.")
            return
        suggested = "obraz.png"
        if self._path is not None:
            suggested = str(self._path.with_name(self._path.stem + "_edytowane.png"))
        p, _ = QFileDialog.getSaveFileName(
            self,
            "Zapisz jako",
            suggested,
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;TIFF (*.tif *.tiff)",
        )
        if p and self._save_to(p):
            self._path = Path(p)
            self.statusBar().showMessage("Zapisano: " + Path(p).name)

    def _save_to(self, path):
        """Render full-resolution image with adjustments and save it."""

        try:
            full = pil_to_cv(self._orig)
            out = apply_adjustments_arr(full, self._adj)
            pil_out = arr_to_pil(out)
            ext = Path(path).suffix.lower()
            if ext in (".jpg", ".jpeg"):
                pil_out.convert("RGB").save(path, "JPEG", quality=95, optimize=True)
            elif ext in (".tif", ".tiff"):
                pil_out.save(path, "TIFF")
            else:
                pil_out.save(path, "PNG")
            logging.info("Zapisano: %s", path)
            return True
        except Exception as e:
            logging.error("Blad zapisu %s: %s", path, e)
            QMessageBox.critical(self, "Blad", "Nie mozna zapisac pliku.")
            return False

    def _on_undo(self):
        if self._orig is None:
            return
        img_ok = self._history.can_undo
        adj_ok = self._adj_history.can_undo
        if not img_ok and not adj_ok:
            self.statusBar().showMessage("Nic do cofniecia.")
            return
        if adj_ok and (
            not img_ok
            or self._adj_history.last_change > self._history.last_change
        ):
            prev = self._adj_history.undo(self._adj)
            if prev is not None:
                self._adj = prev
                self.right_panel.set_adjustments(prev)
                self._render_now()
                self.statusBar().showMessage("Cofnieto korekte.")
            return
        prev = self._history.undo(self._orig)
        if prev is None:
            self.statusBar().showMessage("Nic do cofniecia.")
            return
        self._orig = prev
        self._refresh_after_edit()
        self.statusBar().showMessage(f"Cofnieto. {self._orig.width} x {self._orig.height}")

    def _on_redo(self):
        if self._orig is None:
            return
        img_ok = self._history.can_redo
        adj_ok = self._adj_history.can_redo
        if not img_ok and not adj_ok:
            self.statusBar().showMessage("Nic do ponowienia.")
            return
        if adj_ok and (
            not img_ok
            or self._adj_history.last_change > self._history.last_change
        ):
            nxt = self._adj_history.redo(self._adj)
            if nxt is not None:
                self._adj = nxt
                self.right_panel.set_adjustments(nxt)
                self._render_now()
                self.statusBar().showMessage("Ponowiono korekte.")
            return
        nxt = self._history.redo(self._orig)
        if nxt is None:
            self.statusBar().showMessage("Nic do ponowienia.")
            return
        self._orig = nxt
        self._refresh_after_edit()
        self.statusBar().showMessage(f"Ponowiono. {self._orig.width} x {self._orig.height}")

    def _refresh_after_edit(self):
        preview = prepare_preview(self._orig, max_dim=800)
        self._preview_arr = pil_to_cv(preview)
        self._render_now()
        sb = self.statusBar()
        if hasattr(sb, 'size_label'):
            sb.size_label.setText(str(self._orig.width) + " x " + str(self._orig.height))

    def _on_copy(self):
        if self._orig is None:
            self.statusBar().showMessage("Brak obrazu do skopiowania.")
            return
        full = pil_to_cv(self._orig)
        out = apply_adjustments_arr(full, self._adj)
        pixmap = pil_to_qpixmap(arr_to_pil(out))
        QGuiApplication.clipboard().setImage(pixmap.toImage())
        self.statusBar().showMessage("Skopiowano obraz do schowka.")

    def _on_paste(self):
        img = QGuiApplication.clipboard().image()
        if img.isNull():
            self.statusBar().showMessage("Schowek nie zawiera obrazu.")
            return
        w, h = img.width(), img.height()
        self._orig = qimage_to_pil(img)
        self._path = None
        self._history.clear()
        self._reset_adjustment_state()
        preview = prepare_preview(self._orig, max_dim=800)
        self._preview_arr = pil_to_cv(preview)
        self._render_now()
        self.statusBar().showMessage(
            f"Wklejono obraz ze schowka ({w} x {h})"
        )

    def _on_cut(self):
        if self._orig is None:
            return
        self._on_copy()
        self._clear_image()
        self.statusBar().showMessage("Wyjeto obraz do schowka.")

    def _on_delete(self):
        if self._orig is None:
            return
        self._clear_image()
        self.statusBar().showMessage(
            "Usunieto obraz z edytora (plik na dysku bez zmian)."
        )

    def _clear_image(self):
        self._orig = None
        self._path = None
        self._history.clear()
        self._preview_arr = None
        self.canvas.set_pixmap(QPixmap())
        self.histogram.set_image(None)

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
