#!/usr/bin/env python3
from __future__ import annotations
import logging
import time
import re
import os
import platform
import urllib.request
import json
import tempfile
import shutil
import zipfile
import tarfile
import numpy as np
import rawpy
from pathlib import Path
from PIL import Image
from PySide6.QtCore import Qt, QPointF, QSettings
from PySide6.QtGui import QColor, QGuiApplication, QPixmap
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QSplitter, QVBoxLayout, QWidget, QApplication, QToolBar
from config.defaults import DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH
from config.version import WINDOW_TITLE, APP_VERSION as _APP_VERSION
from config.i18n import t
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
    hdr_tone_map,
    cartoon,
    glitch_art,
    thermal,
    pixelate,
    duotone,
    denoise,
    perspective,
    lens_correction,
    add_text_overlay,
)
from core.history import EditHistory
from core.image_loader import SUPPORTED_FORMATS
from core.pipeline import prepare_preview, pil_to_cv, pil_to_qpixmap, pil_to_qimage, qimage_to_pil, apply_adjustments_arr, arr_to_pil
from core.preset_manager import save_preset, load_preset, list_presets
from core.tools.brush_tool import BrushMode, BrushTool
from core.tools.draw_tool import DrawTool
from core.tab_manager import TabManager, TabData
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
        from ui.theme import build_stylesheet, DARK_THEME
        self.setStyleSheet(build_stylesheet(DARK_THEME))
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
        self._draw_tool = DrawTool()
        self._draw_size = None
        self._preview_arr = None
        self._adj = Adjustments()
        self._tab_mgr = TabManager()
        self._tab_mgr.add_tab()
        self._worker = PipelineWorker(self)
        self._worker.finished.connect(self._on_preview_ready)
        self._ba_active = False
        # Load saved language
        from config.i18n import I18n
        saved_lang = QSettings("PhotoEditor2", "PhotoEditor2").value("language", "pl")
        if saved_lang and saved_lang != "pl":
            I18n.get().set_language(saved_lang)
        # Load saved theme
        saved_theme = QSettings("PhotoEditor2", "PhotoEditor2").value("theme", "dark")
        if saved_theme == "light":
            from ui.theme import build_stylesheet, LIGHT_THEME
            self.setStyleSheet(build_stylesheet(LIGHT_THEME))
        self._build_ui()
        self._connect_actions()
        self.setAcceptDrops(True)
        self._drop_highlight_style = "QMainWindow { border: 3px dashed #5B9EF4; }"

    def _build_ui(self):
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        self.setMenuBar(MenuBar(self, self.actions))
        self.addToolBar(ToolBar(self, actions=self.actions))
        self.setStatusBar(StatusBar(self))
        splitter = QSplitter(Qt.Orientation.Horizontal)
        center = QWidget()
        cl = QVBoxLayout(center)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)
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
        self.statusBar().showMessage(t("status_ready"))

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
        self.canvas.draw_stroke.connect(self._on_draw_stroke)
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
        self.actions.check_updates.triggered.connect(self._on_check_updates)
        self.actions.about.triggered.connect(self._on_about)
        self.actions.hdr.triggered.connect(self._on_hdr)
        self.actions.cartoon.triggered.connect(self._on_cartoon)
        self.actions.glitch.triggered.connect(self._on_glitch)
        self.actions.thermal.triggered.connect(self._on_thermal)
        self.actions.pixelate.triggered.connect(self._on_pixelate)
        self.actions.duotone.triggered.connect(self._on_duotone)
        self.actions.theme_toggle.triggered.connect(self._on_theme_toggle)
        self.actions.lang_pl.triggered.connect(lambda: self._on_lang_change("pl"))
        self.actions.lang_en.triggered.connect(lambda: self._on_lang_change("en"))
        self.actions.lang_es.triggered.connect(lambda: self._on_lang_change("es"))
        self.actions.shortcuts.triggered.connect(self._on_shortcuts)
        self.actions.layers.triggered.connect(self._on_layers)
        self.actions.face_detect.triggered.connect(self._on_face_detect)
        self.actions.history_timeline.triggered.connect(self._on_history_timeline)

        self.actions.resize_image.triggered.connect(self._on_resize)
        self.actions.batch.triggered.connect(self._on_batch_export)
        self.actions.zoom_in.triggered.connect(self._on_zin)
        self.actions.zoom_out.triggered.connect(self._on_zout)
        self.actions.actual_size.triggered.connect(self._on_z100)
        self.actions.fit.triggered.connect(self._on_fit)

        self.actions.text_tool.triggered.connect(self._on_text_tool)
        self.actions.draw_tool.triggered.connect(self._on_draw_tool_toggle)
        self.actions.denoise.triggered.connect(self._on_denoise)
        self.actions.perspective.triggered.connect(self._on_perspective)
        self.actions.lens_correction.triggered.connect(self._on_lens_correction)
        self.actions.adjust.triggered.connect(self._on_adjust)
        self.actions.rotate_custom.triggered.connect(self._on_rotate_custom)
        self.actions.eyedropper.triggered.connect(self._on_eyedropper_toggle)
        self.actions.histogram.triggered.connect(self._on_histogram)
        self.actions.select_edit.triggered.connect(self._on_select_edit)
        self.canvas.color_picked.connect(self._on_color_picked)
        self.canvas.selection_made.connect(self._on_selection_made)

        # Tab navigation shortcuts
        from PySide6.QtGui import QShortcut, QKeySequence
        QShortcut(QKeySequence("Ctrl+Tab"), self, self._on_next_tab)
        QShortcut(QKeySequence("Ctrl+Shift+Tab"), self, self._on_prev_tab)
        QShortcut(QKeySequence("Ctrl+T"), self, self._on_new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, self._on_close_tab)
        QShortcut(QKeySequence("F11"), self, self._toggle_fullscreen)
        QShortcut(QKeySequence("I"), self, self._on_info)
        QShortcut(QKeySequence("Ctrl+Shift+R"), self, self._on_crop_ratio)

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
        self._draw_size = None
        self._reset_adjustment_state()
        self._ba_active = False
        self._render_now()
        self._add_recent(path)
        # Update current tab
        tab = self._tab_mgr.current
        if tab:
            tab.orig = self._orig
            tab.path = path
            tab.preview_arr = self._preview_arr
            tab.title = path.name
            tab.history = self._history
            tab.adj_history = self._adj_history
        self._update_tab_title()
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
                    self._history.push(self._orig, "Kadrowanie")
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

    def _on_crop_ratio(self):
        if self._orig is None:
            QMessageBox.warning(self, t("crop_ratio"), t("status_no_image"))
            return
        from ui.crop_ratio_dialog import CropRatioDialog
        dlg = CropRatioDialog(self._orig.width, self._orig.height, self)
        if dlg.exec() != CropRatioDialog.DialogCode.Accepted:
            return
        w, h = dlg.get_size()
        self._history.push(self._orig, t("crop_ratio"))
        self._orig = self._orig.resize((w, h), Image.Resampling.LANCZOS)
        self._refresh_after_edit()
        self.statusBar().showMessage(f"{t('crop_ratio')}: {w} x {h}")

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
        self._history.push(self._orig, "Retusz")
        self._orig = qimage_to_pil(qimg)
        self._refresh_after_edit()
        self.statusBar().showMessage("Usunieto element (Ctrl+Z cofa).")

    def _on_rotate(self, angle):
        if self._orig is None:
            return
        self._history.push(self._orig, f"Obrot {angle}\u00b0")
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
        self._history.push(self._orig, "Odbicie")
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

    def _run_filter_with_dialog(self, func, name):
        """Show strength dialog, then apply filter with blending."""
        from ui.filter_strength_dialog import FilterStrengthDialog
        dlg = FilterStrengthDialog(name, self)
        if dlg.exec() != FilterStrengthDialog.DialogCode.Accepted:
            return
        strength = dlg.get_strength()
        self._run_filter(func, name, "", strength)

    def _on_pencil(self):
        self._run_filter_with_dialog(pencil_sketch, t("pencil"))

    def _on_black_white(self):
        self._run_filter_with_dialog(black_and_white, t("black_white"))

    def _on_sepia(self):
        self._run_filter_with_dialog(sepia, t("sepia"))

    def _on_negative(self):
        self._run_filter_with_dialog(negative, t("negative"))



    def _on_gaussian_blur(self):
        self._run_filter_with_dialog(gaussian_blur, t("blur"))

    def _on_sharpen(self):
        self._run_filter_with_dialog(sharpen, t("sharpen"))

    def _on_emboss(self):
        self._run_filter_with_dialog(emboss, t("emboss"))

    def _on_vignette(self):
        self._run_filter_with_dialog(vignette, t("vignette"))

    def _on_frame(self):
        self._run_filter_with_dialog(frame, t("frame"))

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
        self._history.push(self._orig, "Pedzel")
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
        self._history.push(self._orig, "Naloz warstwe")
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
        self._history.push(self._orig, "Wyprostuj")
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
        self._history.push(self._orig, "Znak wodny")
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
        self._history.push(self._orig, "Auto-korekta")
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
        self._history.push(self._orig, "Zmien rozmiar")
        self._orig = self._orig.resize(
            (width, height), Image.Resampling.LANCZOS
        )
        self._refresh_after_edit()
        self.statusBar().showMessage(f"Zmieniono rozmiar: {width} x {height}")
        return True

    def _run_filter(self, func, name, suffix, strength=1.0):
        """Apply a filter with strength blending, undoable."""

        if self._orig is None:
            QMessageBox.warning(self, name, "Najpierw otworz zdjecie.")
            return
        if self._ba_active:
            self._on_before_after()
        self.canvas.cancel_crop()
        self._history.push(self._orig, name)
        result = func(self._orig)
        # Blend original with filtered based on strength
        if strength < 1.0 and result.size == self._orig.size and result.mode == self._orig.mode:
            result = Image.blend(self._orig, result, strength)
        elif strength < 1.0:
            # Fallback: resize result to match original if sizes differ
            result = result.resize(self._orig.size, Image.Resampling.LANCZOS)
            if result.mode != self._orig.mode:
                result = result.convert(self._orig.mode)
            result = Image.blend(self._orig, result, strength)
        self._orig = result
        self._refresh_after_edit()
        self.statusBar().showMessage(f"{name}: {int(strength * 100)}%")

    def _on_batch_export(self):
        from ui.batch_dialog import BatchDialog
        dlg = BatchDialog(self)
        dlg.exec()

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
        try:
            qimg = pil_to_qpixmap(pil_img).toImage()
            self.histogram.set_image(qimg)
        except Exception:
            pass
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
        # Update current tab
        tab = self._tab_mgr.current
        if tab:
            tab.orig = self._orig
            tab.path = None
            tab.preview_arr = self._preview_arr
            tab.title = "Nowy"
            tab.history = self._history
        self._update_tab_title()
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

    def _on_check_updates(self):
        from PySide6.QtCore import QThread, Signal

        class UpdateChecker(QThread):
            finished = Signal(dict)

            def run(self):
                try:
                    import urllib.request
                    import json
                    config_path = Path(__file__).resolve().parent.parent / "config" / "updater_config.json"
                    cfg = json.loads(config_path.read_text()) if config_path.exists() else {}
                    gh = cfg.get("github", {})
                    url = f"{gh.get('api_url', 'https://api.github.com')}/repos/{gh.get('owner', 'tomekkrow-sys')}/{gh.get('repo', 'Photo_Editor_2')}/releases/latest"
                    req = urllib.request.Request(url, headers={"User-Agent": "Photo-Editor-2"})
                    resp = urllib.request.urlopen(req, timeout=10)
                    data = json.loads(resp.read().decode())
                    self.finished.emit({"status": "ok", "data": data})
                except Exception as e:
                    self.finished.emit({"status": "error", "message": str(e)})

        self.statusBar().showMessage("Sprawdzam aktualizacje...")
        self._update_checker = UpdateChecker()
        self._update_checker.finished.connect(self._on_update_result)
        self._update_checker.start()

    def _on_update_result(self, result):
        if result["status"] == "error":
            QMessageBox.warning(self, "Aktualizacje", f"Blad sprawdzania:\n{result['message']}")
            self.statusBar().showMessage("Blad sprawdzania aktualizacji.")
            return

        data = result["data"]
        latest_tag = data.get("tag_name", "unknown")
        from config.version import APP_VERSION as _ver
        current = _ver

        cur_parts = [int(x) for x in re.sub(r'^v', '', current).split('.')]
        lat_parts = [int(x) for x in re.sub(r'^v', '', latest_tag).split('.')]

        newer = False
        for i in range(min(len(cur_parts), len(lat_parts))):
            if lat_parts[i] > cur_parts[i]:
                newer = True
                break
            elif lat_parts[i] < cur_parts[i]:
                break
        if not newer and len(lat_parts) > len(cur_parts):
            newer = True

        if newer:
            reply = QMessageBox.information(
                self, "Aktualizacja",
                f"Dostepna nowa wersja: {latest_tag}\n\n"
                f"Biezaca: {current}\nNowa: {latest_tag}\n\n"
                "Pobrac i zainstalowac automatycznie?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._auto_update(data, latest_tag)
            else:
                import webbrowser
                webbrowser.open(data.get("html_url", "https://github.com/tomekkrow-sys/Photo_Editor_2/releases"))
        else:
            QMessageBox.information(self, "Aktualizacje", f"Masz najnowsza wersje ({current}).")
        self.statusBar().showMessage("Sprawdzono aktualizacje.")

    def _auto_update(self, release_data, latest_tag):
        """Download and install update with animated progress dialog."""
        from PySide6.QtCore import QTimer, QCoreApplication
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar

        assets = release_data.get("assets", [])
        if not assets:
            QMessageBox.warning(self, "Aktualizacja", "Brak plikow do pobrania.")
            return

        # Detect platform
        sys_name = platform.system().lower()
        asset = None
        for a in assets:
            name = a.get("name", "").lower()
            if sys_name == "windows" and "windows" in name:
                asset = a
            elif sys_name == "linux" and ("tar.gz" in name or "deb" in name or "appimage" in name):
                asset = a
                break
            elif sys_name == "darwin" and "macos" in name:
                asset = a
        if not asset:
            asset = assets[0]

        url = asset.get("browser_download_url", "")
        filename = asset.get("name", "update.zip")
        total_size = asset.get("size", 0)

        # Create progress dialog
        dlg = QDialog(self)
        dlg.setWindowTitle("Aktualizacja Photo Editor 2")
        dlg.setFixedSize(480, 220)
        dlg.setWindowFlags(dlg.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        dlg.setModal(True)

        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        status_label = QLabel(f"Przygotowywanie aktualizacji do {latest_tag}...")
        status_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(status_label)

        detail_label = QLabel("")
        detail_label.setStyleSheet("font-size: 12px; color: #A0A0AB;")
        layout.addWidget(detail_label)

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(0)
        progress.setFixedHeight(10)
        progress.setTextVisible(False)
        layout.addWidget(progress)

        speed_label = QLabel("")
        speed_label.setStyleSheet("font-size: 11px; color: #6B6B76;")
        layout.addWidget(speed_label)

        layout.addStretch()

        dlg.show()
        QCoreApplication.processEvents()

        def set_status(text):
            status_label.setText(text)
            QCoreApplication.processEvents()

        def set_detail(text):
            detail_label.setText(text)
            QCoreApplication.processEvents()

        def set_progress(val):
            progress.setValue(int(val))
            QCoreApplication.processEvents()

        def set_speed(text):
            speed_label.setText(text)
            QCoreApplication.processEvents()

        try:
            import time
            temp_dir = tempfile.mkdtemp(prefix="pe2_update_")
            download_path = str(Path(temp_dir) / filename)

            # Step 1: Download
            set_status(f"Pobieranie {filename}...")
            set_detail(f"Rozmiar: {total_size / 1024 / 1024:.1f} MB")

            start_time = time.time()
            downloaded = 0

            req = urllib.request.Request(url, headers={"User-Agent": "Photo-Editor-2"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                with open(download_path, "wb") as f:
                    while True:
                        chunk = resp.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        elapsed = time.time() - start_time
                        if elapsed > 0:
                            speed = downloaded / elapsed / 1024 / 1024
                            set_speed(f"{speed:.1f} MB/s")
                        if total_size > 0:
                            pct = (downloaded / total_size) * 60
                            set_progress(pct)
                            mb_done = downloaded / 1024 / 1024
                            mb_total = total_size / 1024 / 1024
                            set_detail(f"{mb_done:.1f} / {mb_total:.1f} MB")

            set_progress(60)
            set_speed("")

            # Step 2: Extract
            set_status("Rozpakowywanie...")
            set_detail("Analiza archiwum...")

            if download_path.endswith(".zip"):
                with zipfile.ZipFile(download_path, "r") as z:
                    names = z.namelist()
                    for i, name in enumerate(names):
                        z.extract(name, temp_dir)
                        set_progress(60 + (i / len(names)) * 20)
                        if i % 5 == 0:
                            set_detail(f"Rozpakowywanie: {Path(name).name}")
            elif download_path.endswith((".tar.gz", ".tgz")):
                with tarfile.open(download_path, "r:gz") as t:
                    members = t.getmembers()
                    for i, member in enumerate(members):
                        t.extract(member, temp_dir)
                        set_progress(60 + (i / len(members)) * 20)
                        if i % 5 == 0:
                            set_detail(f"Rozpakowywanie: {member.name}")

            set_progress(80)

            # Step 3: Install
            set_status("Instalowanie aktualizacji...")
            set_detail("Kopiowanie plikow...")

            app_dir = Path(__file__).resolve().parent.parent

            # Find extracted files
            extracted_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    src = os.path.join(root, file)
                    rel = os.path.relpath(src, temp_dir)
                    if not rel.startswith("photo-editor-2_"):
                        extracted_files.append((src, rel))

            for i, (src, rel) in enumerate(extracted_files):
                dst = app_dir / rel
                if dst.suffix in {".py", ".json", ".txt", ".md", ".desktop"} or \
                   any(p in rel for p in ["ui/", "core/", "config/", "resources/"]):
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    if len(extracted_files) > 0:
                        set_progress(80 + (i / len(extracted_files)) * 15)
                        if i % 3 == 0:
                            set_detail(f"Aktualizacja: {rel[:50]}")

            # Update version file
            ver_file = app_dir / "version.txt"
            if ver_file.exists():
                ver_file.write_text(latest_tag.lstrip("v"))

            # Step 4: Complete
            set_progress(100)
            set_status("Aktualizacja zakonczona!")
            set_detail(f"Zainstalowano wersje {latest_tag}")

            dlg.repaint()
            QCoreApplication.processEvents()

            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)

            # Wait a moment then restart
            QTimer.singleShot(1500, lambda: self._restart_app())

        except Exception as e:
            set_status("Blad aktualizacji!")
            set_detail(str(e))
            set_progress(0)
            QTimer.singleShot(3000, dlg.close)
            QMessageBox.critical(self, "Aktualizacja", f"Blad:\n{str(e)}")

    def _restart_app(self):
        """Restart the application."""
        import sys
        import os
        app = QApplication.instance()
        if app:
            app.quit()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def _on_hdr(self):
        self._run_filter_with_dialog(hdr_tone_map, t("hdr"))

    def _on_cartoon(self):
        self._run_filter_with_dialog(cartoon, t("cartoon"))

    def _on_glitch(self):
        self._run_filter_with_dialog(glitch_art, t("glitch"))

    def _on_thermal(self):
        self._run_filter_with_dialog(thermal, t("thermal"))

    def _on_pixelate(self):
        self._run_filter_with_dialog(pixelate, t("pixelate"))

    def _on_duotone(self):
        if self._orig is None:
            QMessageBox.warning(self, "Duotone", t("status_no_image"))
            return
        from ui.duotone_dialog import DuotoneDialog
        dlg = DuotoneDialog(self)
        if dlg.exec() != DuotoneDialog.DialogCode.Accepted:
            return
        c1, c2 = dlg.get_colors()
        self._history.push(self._orig, "Duotone")
        self._orig = duotone(self._orig, color1=c1, color2=c2)
        self._refresh_after_edit()
        self.statusBar().showMessage(f"Duotone: {c1} / {c2}")

    def _on_text_tool(self):
        if self._orig is None:
            QMessageBox.warning(self, t("text_tool"), t("status_no_image"))
            return
        from ui.text_dialog import TextToolDialog
        dlg = TextToolDialog(self)
        if dlg.exec() != TextToolDialog.DialogCode.Accepted:
            return
        text = dlg.get_text()
        if not text:
            return
        font = dlg.get_font()
        color = dlg.get_color()
        opacity = dlg.get_opacity()
        pos = dlg.get_position()
        anchor = dlg.get_anchor()
        self._history.push(self._orig, "Tekst")
        self._orig = add_text_overlay(
            self._orig, text,
            font_name=font.family(),
            font_size=font.pixelSize(),
            color=(color.red(), color.green(), color.blue()),
            opacity=opacity,
            position=pos,
            anchor=anchor,
            bold=font.bold(),
        )
        self._refresh_after_edit()
        self.statusBar().showMessage(t("text_tool") + ": " + text)

    def _on_draw_tool_toggle(self):
        if self._orig is None:
            QMessageBox.warning(self, t("draw_tool"), t("status_no_image"))
            return
        if self._ba_active:
            self._on_before_after()
        if self.canvas._draw_mode:
            self.canvas.cancel_draw()
            self.statusBar().showMessage(t("draw_tool") + " OFF")
        else:
            from ui.draw_dialog import DrawToolDialog
            dlg = DrawToolDialog(self)
            if dlg.exec() != DrawToolDialog.DialogCode.Accepted:
                return
            self.canvas.cancel_crop()
            self.canvas.cancel_spot()
            self.canvas.cancel_brush()
            self._draw_size = dlg.get_size()
            self._draw_tool.settings.size = dlg.get_size() * 2
            self._draw_tool.settings.color = dlg.get_color()
            self._draw_tool.settings.opacity = dlg.get_opacity()
            self.canvas.start_draw()
            self.statusBar().showMessage(t("draw_tool") + ": ON")

    def _on_draw_stroke(self, points, button):
        if self._orig is None or self._preview_arr is None or not points:
            return
        preview_h, preview_w = self._preview_arr.shape[:2]
        scale_x = self._orig.width / preview_w
        scale_y = self._orig.height / preview_h
        qimg = pil_to_qimage(self._orig)
        orig_points = [QPointF(p.x() * scale_x, p.y() * scale_y) for p in points]
        self._history.push(self._orig, "Rysowanie")
        self._draw_tool.begin(orig_points[0], qimg)
        for p in orig_points[1:]:
            self._draw_tool.update(p, qimg)
        self._draw_tool.finish()
        self._orig = qimage_to_pil(qimg)
        self._refresh_after_edit()

    def _on_denoise(self):
        if self._orig is None:
            QMessageBox.warning(self, t("denoise"), t("status_no_image"))
            return
        from PySide6.QtWidgets import QInputDialog
        strength, ok = QInputDialog.getInt(self, t("denoise"), t("denoise_strength") + " (1-30):", 10, 1, 30)
        if not ok:
            return
        self._history.push(self._orig, "Redukcja szumu")
        self._orig = denoise(self._orig, strength=strength)
        self._refresh_after_edit()
        self.statusBar().showMessage(t("denoise") + ": " + str(strength))

    def _on_perspective(self):
        if self._orig is None:
            QMessageBox.warning(self, t("perspective"), t("status_no_image"))
            return
        from ui.perspective_dialog import PerspectiveDialog
        dlg = PerspectiveDialog(self._orig.width, self._orig.height, self)
        if dlg.exec() != PerspectiveDialog.DialogCode.Accepted:
            return
        corners = dlg.get_corners()
        self._history.push(self._orig, "Perspektywa")
        self._orig = perspective(self._orig, corners=corners)
        self._refresh_after_edit()
        self.statusBar().showMessage(t("perspective"))

    def _on_lens_correction(self):
        if self._orig is None:
            QMessageBox.warning(self, t("lens_correction"), t("status_no_image"))
            return
        from ui.lens_dialog import LensCorrectionDialog
        dlg = LensCorrectionDialog(self)
        if dlg.exec() != LensCorrectionDialog.DialogCode.Accepted:
            return
        vals = dlg.get_values()
        self._history.push(self._orig, "Korekcja obiektywu")
        self._orig = lens_correction(
            self._orig,
            k1=vals["k1"], k2=vals["k2"], k3=vals["k3"],
            p1=vals["p1"], p2=vals["p2"],
        )
        self._refresh_after_edit()
        self.statusBar().showMessage(t("lens_correction"))

    def _on_theme_toggle(self):
        from ui.theme import build_stylesheet, DARK_THEME, LIGHT_THEME
        settings = QSettings("PhotoEditor2", "PhotoEditor2")
        current = settings.value("theme", "dark")
        if current == "dark":
            new_theme = "light"
            self.setStyleSheet(build_stylesheet(LIGHT_THEME))
        else:
            new_theme = "dark"
            self.setStyleSheet(build_stylesheet(DARK_THEME))
        settings.setValue("theme", new_theme)
        self.statusBar().showMessage(f"Motyw: {new_theme}")

    def _on_lang_change(self, lang):
        from config.i18n import I18n
        I18n.get().set_language(lang)
        settings = QSettings("PhotoEditor2", "PhotoEditor2")
        settings.setValue("language", lang)
        self.setWindowTitle(t("app_name") + " " + _APP_VERSION)
        self.statusBar().showMessage(t("status_ready"))

    def _on_shortcuts(self):
        from ui.shortcuts_dialog import ShortcutsDialog
        dlg = ShortcutsDialog(self)
        dlg.exec()

    def _on_layers(self):
        from ui.layers_dialog import LayersDialog
        if self._orig is None:
            QMessageBox.warning(self, "Warstwy", "Najpierw otworz zdjecie.")
            return
        dlg = LayersDialog(self, self._orig)
        if dlg.exec() == LayersDialog.DialogCode.Accepted:
            result = dlg.get_result()
            if result is not None:
                self._history.push(self._orig, "Warstwa")
                self._orig = result
                self._refresh_after_edit()
                self.statusBar().showMessage("Zastosowano warstwe.")

    def _on_face_detect(self):
        if self._orig is None:
            QMessageBox.warning(self, "Rozpoznawanie twarzy", "Najpierw otworz zdjecie.")
            return
        try:
            import cv2
            arr = np.array(self._orig.convert("RGB"))
            gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
            cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) == 0:
                QMessageBox.information(self, "Rozpoznawanie twarzy", "Nie wykryto twarzy.")
                return
            msg = f"Wykryto {len(faces)} twarz(y):\n"
            for i, (x, y, w, h) in enumerate(faces, 1):
                msg += f"  Twarz {i}: pozycja ({x}, {y}), rozmiar {w}x{h}\n"
            msg += "\nZakadrowac do pierwszej twarzy?"
            reply = QMessageBox.question(
                self, "Rozpoznawanie twarzy", msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                x, y, w, h = faces[0]
                pad = max(w, h) // 2
                orig_w, orig_h = self._orig.size
                x1 = max(0, x - pad)
                y1 = max(0, y - pad)
                x2 = min(orig_w, x + w + pad)
                y2 = min(orig_h, y + h + pad)
                self._history.push(self._orig, "Kadrowanie twarzy")
                self._orig = self._orig.crop((x1, y1, x2, y2))
                self._refresh_after_edit()
                self.statusBar().showMessage(f"Zakadrowano do twarzy ({x2-x1}x{y2-y1}).")
        except ImportError:
            QMessageBox.warning(self, "Rozpoznawanie twarzy", "Wymaga opencv-python.")
        except Exception as e:
            QMessageBox.critical(self, "Blad", str(e))

    def _on_history_timeline(self):
        from ui.history_dialog import HistoryDialog
        dlg = HistoryDialog(self._history, self)
        if dlg.exec() == HistoryDialog.DialogCode.Accepted:
            target = dlg.get_target_index()
            if target is not None and target >= 0:
                # Undo to target index
                steps_back = self._history.current_index - target
                for _ in range(steps_back):
                    prev = self._history.undo(self._orig)
                    if prev is not None:
                        self._orig = prev
                    else:
                        break
                self._refresh_after_edit()
                self.statusBar().showMessage(f"{t('history')}: cofnieto do kroku {target + 1}")

    def _on_about(self):
        from config.version import APP_NAME as _name, APP_VERSION as _ver
        QMessageBox.about(
            self, "O programie",
            f"<h3>{_name}</h3>"
            f"<p>Wersja: {_ver}</p>"
            f"<p>Autor: Tomek Krowczynski</p>"
            f"<p>Edytor zdjec z obsluga RAW</p>"
            f"<p>GitHub: <a href='https://github.com/tomekkrow-sys/Photo_Editor_2'>tomekkrow-sys/Photo_Editor_2</a></p>"
        )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(self._drop_highlight_style)

    def dragLeaveEvent(self, event):
        self._apply_current_theme()

    def dropEvent(self, event):
        self._apply_current_theme()
        for url in event.mimeData().urls():
            p = Path(url.toLocalFile())
            if p.suffix.lower() in SUPPORTED_FORMATS:
                self._load(p)
                break

    def _apply_current_theme(self):
        from ui.theme import build_stylesheet, DARK_THEME, LIGHT_THEME
        saved = QSettings("PhotoEditor2", "PhotoEditor2").value("theme", "dark")
        if saved == "light":
            self.setStyleSheet(build_stylesheet(LIGHT_THEME))
        else:
            self.setStyleSheet(build_stylesheet(DARK_THEME))

    # === MULTI-TAB MANAGEMENT ===

    def _save_current_tab(self):
        """Save current tab state."""
        tab = self._tab_mgr.current
        if tab is None:
            return
        tab.orig = self._orig
        tab.path = self._path
        tab.preview_arr = self._preview_arr
        tab.adj = self._adj.copy() if self._adj else Adjustments()
        tab.history = self._history
        tab.adj_history = self._adj_history
        tab.ba_active = self._ba_active
        tab.spot_size = self._spot_size
        tab.brush_size = self._brush_size
        tab.draw_size = self._draw_size
        if self._path:
            tab.title = self._path.name

    def _restore_tab(self, tab: TabData):
        """Restore state from a tab."""
        self._orig = tab.orig
        self._path = tab.path
        self._preview_arr = tab.preview_arr
        self._adj = tab.adj.copy() if tab.adj else Adjustments()
        self._history = tab.history
        self._adj_history = tab.adj_history
        self._ba_active = tab.ba_active
        self._spot_size = tab.spot_size
        self._brush_size = tab.brush_size
        self._draw_size = tab.draw_size
        self.right_panel.set_adjustments(self._adj)
        self._render_now()
        self._update_tab_title()

    def _update_tab_title(self):
        """Update window title with tab info."""
        tab = self._tab_mgr.current
        if tab and tab.title:
            count = self._tab_mgr.count()
            if count > 1:
                idx = self._tab_mgr.current_index + 1
                self.setWindowTitle(f"[{idx}/{count}] {tab.title} - {t('app_name')} {_APP_VERSION}")
            else:
                self.setWindowTitle(f"{tab.title} - {t('app_name')} {_APP_VERSION}")
        else:
            self.setWindowTitle(f"{t('app_name')} {_APP_VERSION}")

    def _on_next_tab(self):
        self._save_current_tab()
        tab = self._tab_mgr.next_tab()
        if tab:
            self._restore_tab(tab)
            self.statusBar().showMessage(f"Tab {self._tab_mgr.current_index + 1}/{self._tab_mgr.count()}: {tab.title}")

    def _on_prev_tab(self):
        self._save_current_tab()
        tab = self._tab_mgr.prev_tab()
        if tab:
            self._restore_tab(tab)
            self.statusBar().showMessage(f"Tab {self._tab_mgr.current_index + 1}/{self._tab_mgr.count()}: {tab.title}")

    def _on_new_tab(self):
        self._save_current_tab()
        new_tab = self._tab_mgr.add_tab()
        self._orig = Image.new("RGB", (1920, 1080), (255, 255, 255))
        self._path = None
        self._history = EditHistory()
        self._adj = Adjustments()
        self._adj_history = EditHistory(limit=30)
        self._ba_active = False
        self._spot_size = None
        self._brush_size = None
        self._draw_size = None
        preview = prepare_preview(self._orig, max_dim=800)
        self._preview_arr = pil_to_cv(preview)
        new_tab.orig = self._orig
        new_tab.title = "Nowy"
        self._render_now()
        self._update_tab_title()
        self.statusBar().showMessage(f"Nowa zakladka {self._tab_mgr.count()}")

    def _on_close_tab(self):
        if self._tab_mgr.count() <= 1:
            return
        idx = self._tab_mgr.current_index
        self._tab_mgr.remove_tab(idx)
        if self._tab_mgr.current is not None:
            self._restore_tab(self._tab_mgr.current)
        self.statusBar().showMessage(f"Pozostalo {self._tab_mgr.count()} zakladek")

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.menuBar().setVisible(True)
            for bar in self.findChildren(QToolBar):
                bar.setVisible(True)
            self.statusBar().setVisible(True)
        else:
            self.showFullScreen()
            self.menuBar().setVisible(False)
            for bar in self.findChildren(QToolBar):
                bar.setVisible(False)
            self.statusBar().setVisible(False)

    # --- v0.4.1: Adjust (brightness/contrast/saturation) ---
    def _on_adjust(self):
        if self._orig is None:
            QMessageBox.warning(self, t("adjust"), t("status_no_image"))
            return
        from ui.adjust_dialog import AdjustDialog
        dlg = AdjustDialog(self)
        if dlg.exec() != AdjustDialog.DialogCode.Accepted:
            return
        vals = dlg.get_values()
        self._history.push(self._orig, "Korekcja obrazu")
        # Apply using PIL
        from PIL import ImageEnhance
        img = self._orig.copy()
        b = vals["brightness"]
        c = vals["contrast"]
        s = vals["saturation"]
        if b != 0:
            factor = 1.0 + b / 100.0
            img = ImageEnhance.Brightness(img).enhance(factor)
        if c != 0:
            factor = 1.0 + c / 100.0
            img = ImageEnhance.Contrast(img).enhance(factor)
        if s != 0:
            factor = 1.0 + s / 100.0
            img = ImageEnhance.Color(img).enhance(factor)
        # Temperature (warm/cool shift)
        temp = vals["temperature"]
        tint = vals["tint"]
        if temp != 0 or tint != 0:
            import numpy as np
            arr = np.array(img, dtype=np.float32)
            if temp != 0:
                arr[:, :, 0] += temp * 0.8
                arr[:, :, 2] -= temp * 0.8
            if tint != 0:
                arr[:, :, 1] += tint * 0.8
            arr = np.clip(arr, 0, 255).astype(np.uint8)
            img = Image.fromarray(arr)
        self._orig = img
        self._refresh_after_edit()
        self.statusBar().showMessage(t("adjust") + ": OK")

    # --- v0.4.1: Rotate by custom angle ---
    def _on_rotate_custom(self):
        if self._orig is None:
            QMessageBox.warning(self, t("rotate_custom"), t("status_no_image"))
            return
        from ui.rotate_dialog import RotateDialog
        dlg = RotateDialog(self)
        if dlg.exec() != RotateDialog.DialogCode.Accepted:
            return
        angle = dlg.get_angle()
        expand = dlg.expand()
        if angle == 0:
            return
        self._history.push(self._orig, f"Obrot {angle}\u00b0")
        self._orig = self._orig.rotate(-angle, expand=expand, resample=Image.Resampling.BICUBIC)
        self._refresh_after_edit()
        self.statusBar().showMessage(f"{t('rotate_custom')}: {angle}\u00b0")

    # --- v0.4.1: Eyedropper ---
    def _on_eyedropper_toggle(self):
        if self._orig is None:
            QMessageBox.warning(self, t("eyedropper"), t("status_no_image"))
            return
        if self._ba_active:
            self._on_before_after()
        if self.canvas._eyedropper_mode:
            self.canvas.cancel_eyedropper()
            self.statusBar().showMessage(t("eyedropper") + " OFF")
        else:
            self.canvas.cancel_crop()
            self.canvas.cancel_spot()
            self.canvas.cancel_brush()
            self.canvas.cancel_draw()
            self.canvas.start_eyedropper()
            self.statusBar().showMessage(t("eyedropper") + ": " + "Kliknij na obraz")

    def _on_color_picked(self, point):
        if self._orig is None:
            return
        px, py = int(point.x()), int(point.y())
        if 0 <= px < self._orig.width and 0 <= py < self._orig.height:
            r, g, b = self._orig.getpixel((px, py))[:3]
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.statusBar().showMessage(f"{t('color_picked')}: {hex_color}  RGB({r}, {g}, {b})  [{px},{py}]")
            # Copy to clipboard
            from PySide6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(hex_color)
            self.canvas.cancel_eyedropper()

    # --- v0.4.1: Histogram ---
    def _on_histogram(self):
        if self._orig is None:
            QMessageBox.warning(self, t("histogram"), t("status_no_image"))
            return
        from PySide6.QtWidgets import QDialog, QVBoxLayout
        from ui.histogram import HistogramDock
        dlg = QDialog(self)
        dlg.setWindowTitle(t("histogram"))
        dlg.setMinimumSize(400, 220)
        lay = QVBoxLayout(dlg)
        lay.setContentsMargins(8, 8, 8, 8)
        hist = HistogramDock()
        hist.set_image(pil_to_qpixmap(self._orig))
        lay.addWidget(hist)
        dlg.exec()

    # --- v0.4.4: Selective Edit ---
    def _on_select_edit(self):
        if self._orig is None:
            QMessageBox.warning(self, t("select_edit"), t("status_no_image"))
            return
        if self._ba_active:
            self._on_before_after()
        # Cancel other modes
        self.canvas.cancel_crop()
        self.canvas.cancel_spot()
        self.canvas.cancel_brush()
        self.canvas.cancel_draw()
        self.canvas.cancel_eyedropper()
        # Start selection mode
        self.canvas.start_select()
        self.statusBar().showMessage(t("select_edit") + ": " + "Zaznacz prostokat na obrazie")

    def _on_selection_made(self, rect, feather):
        if self._orig is None or rect is None:
            return
        x1, y1, x2, y2 = rect
        from ui.select_edit_dialog import SelectEditDialog
        dlg = SelectEditDialog(self)
        if dlg.exec() != SelectEditDialog.DialogCode.Accepted:
            self.canvas.cancel_select()
            return
        filt = dlg.get_filter()
        intensity = dlg.get_intensity()
        feather_px = dlg.get_feather()
        self.canvas.cancel_select()

        self._history.push(self._orig, "Edycja zaznaczenia")
        import numpy as np
        from PIL import Image, ImageFilter as PILFilter
        import core.filters as F

        img = self._orig.copy()
        # Extract region
        region = img.crop((x1, y1, x2, y2))

        # Apply filter to region
        if filt == "blur":
            k = max(1, int(intensity / 10) * 2 + 1)
            region = F.gaussian_blur(region, kernel_size=k)
        elif filt == "sharpen":
            from PIL import ImageEnhance
            factor = 1.0 + intensity / 100.0
            enhancer = ImageEnhance.Sharpness(region)
            region = enhancer.enhance(factor)
        elif filt == "black_white":
            region = F.black_and_white(region)
        elif filt == "sepia":
            region = F.sepia(region)
        elif filt == "negative":
            region = F.negative(region)
        elif filt == "vignette":
            region = F.vignette(region, strength=intensity / 100.0)
        elif filt == "emboss":
            region = F.emboss(region)
        elif filt == "brightness":
            from PIL import ImageEnhance
            factor = 0.5 + intensity / 100.0
            region = ImageEnhance.Brightness(region).enhance(factor)
        elif filt == "contrast":
            from PIL import ImageEnhance
            factor = 0.5 + intensity / 100.0
            region = ImageEnhance.Contrast(region).enhance(factor)
        elif filt == "saturation":
            from PIL import ImageEnhance
            factor = 0.5 + intensity / 100.0
            region = ImageEnhance.Color(region).enhance(factor)
        elif filt == "pixelate":
            bs = max(2, int(intensity / 5))
            region = F.pixelate(region, block_size=bs)
        elif filt == "denoise":
            region = F.denoise(region, strength=max(1, intensity // 5))
        elif filt == "hdr":
            region = F.hdr_tone_map(region, strength=intensity / 100.0)
        elif filt == "cartoon":
            region = F.cartoon(region, strength=intensity / 100.0)
        elif filt == "thermal":
            region = F.thermal(region, strength=intensity / 100.0)

        # Apply feathered mask
        if feather_px > 0:
            mask = Image.new("L", (x2 - x1, y2 - y1), 0)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            # Inner rect with feather
            draw.rectangle(
                [feather_px, feather_px, mask.width - feather_px, mask.height - feather_px],
                fill=255
            )
            mask = mask.filter(PILFilter.GaussianBlur(radius=feather_px))
        else:
            mask = Image.new("L", (x2 - x1, y2 - y1), 255)

        # Composite
        img.paste(region, (x1, y1), mask)
        self._orig = img
        self._refresh_after_edit()
        self.statusBar().showMessage(t("select_edit") + ": OK")
