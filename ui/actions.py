#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtGui import QAction
from config import shortcuts
from config.i18n import t, I18n


def _tip(action, text, shortcut=None):
    """Set tooltip with optional shortcut suffix."""
    if shortcut:
        action.setToolTip(f"{text}  ({shortcut})")
    else:
        action.setToolTip(text)


class ActionManager:
    def __init__(self, parent):
        self.parent = parent
        self._create_actions()
        I18n.get().on_change(self._refresh_texts)

    def _create_actions(self):
        self.new = QAction(t("new"), self.parent)
        self.new.setShortcut(shortcuts.NEW)
        _tip(self.new, t("new"), shortcuts.NEW)

        self.open = QAction(t("open"), self.parent)
        self.open.setShortcut(shortcuts.OPEN)
        _tip(self.open, t("open"), shortcuts.OPEN)

        self.save = QAction(t("save"), self.parent)
        self.save.setShortcut(shortcuts.SAVE)
        _tip(self.save, t("save"), shortcuts.SAVE)

        self.save_as = QAction(t("save_as"), self.parent)
        self.save_as.setShortcut(shortcuts.SAVE_AS)
        _tip(self.save_as, t("save_as"), shortcuts.SAVE_AS)

        self.export = QAction(t("export"), self.parent)
        self.export.setShortcut(shortcuts.EXPORT)
        _tip(self.export, t("export"), shortcuts.EXPORT)

        self.batch = QAction(t("batch"), self.parent)
        _tip(self.batch, t("batch"))

        self.exit = QAction(t("exit"), self.parent)
        self.exit.setShortcut(shortcuts.EXIT)
        _tip(self.exit, t("exit"), shortcuts.EXIT)

        self.undo = QAction(t("undo"), self.parent)
        self.undo.setShortcut(shortcuts.UNDO)
        _tip(self.undo, t("undo"), shortcuts.UNDO)

        self.redo = QAction(t("redo"), self.parent)
        self.redo.setShortcut(shortcuts.REDO)
        _tip(self.redo, t("redo"), shortcuts.REDO)

        self.cut = QAction(t("cut"), self.parent)
        self.cut.setShortcut(shortcuts.CUT)
        _tip(self.cut, t("cut"), shortcuts.CUT)

        self.copy = QAction(t("copy"), self.parent)
        self.copy.setShortcut(shortcuts.COPY)
        _tip(self.copy, t("copy"), shortcuts.COPY)

        self.paste = QAction(t("paste"), self.parent)
        self.paste.setShortcut(shortcuts.PASTE)
        _tip(self.paste, t("paste"), shortcuts.PASTE)

        self.delete = QAction(t("delete"), self.parent)
        self.delete.setShortcut(shortcuts.DELETE)
        _tip(self.delete, t("delete"), shortcuts.DELETE)

        self.zoom_in = QAction(t("zoom_in"), self.parent)
        self.zoom_in.setShortcut(shortcuts.ZOOM_IN)
        _tip(self.zoom_in, t("zoom_in"), shortcuts.ZOOM_IN)

        self.zoom_out = QAction(t("zoom_out"), self.parent)
        self.zoom_out.setShortcut(shortcuts.ZOOM_OUT)
        _tip(self.zoom_out, t("zoom_out"), shortcuts.ZOOM_OUT)

        self.fit = QAction(t("fit"), self.parent)
        self.fit.setShortcut(shortcuts.FIT)
        _tip(self.fit, t("fit"), shortcuts.FIT)

        self.actual_size = QAction("100%", self.parent)
        self.actual_size.setShortcut(shortcuts.ACTUAL_SIZE)
        _tip(self.actual_size, t("actual_size"), shortcuts.ACTUAL_SIZE)

        self.crop = QAction(t("crop"), self.parent)
        self.crop.setShortcut(shortcuts.CROP)
        _tip(self.crop, t("crop"), shortcuts.CROP)

        self.spot = QAction(t("spot"), self.parent)
        _tip(self.spot, t("spot"))

        self.brush = QAction(t("brush"), self.parent)
        _tip(self.brush, t("brush"))

        self.frame = QAction(t("frame"), self.parent)
        _tip(self.frame, t("frame"))

        self.info = QAction(t("info"), self.parent)
        _tip(self.info, t("info"))

        self.compare = QAction(t("compare"), self.parent)
        _tip(self.compare, t("compare"))

        self.rotate_left = QAction(t("rotate_left"), self.parent)
        _tip(self.rotate_left, t("rotate_left"))

        self.rotate_right = QAction(t("rotate_right"), self.parent)
        _tip(self.rotate_right, t("rotate_right"))

        self.flip_h = QAction(t("flip_h"), self.parent)
        _tip(self.flip_h, t("flip_h"))

        self.flip_v = QAction(t("flip_v"), self.parent)
        _tip(self.flip_v, t("flip_v"))

        self.before_after = QAction(t("before_after"), self.parent)
        _tip(self.before_after, t("before_after"))

        self.pencil = QAction(t("pencil"), self.parent)
        _tip(self.pencil, t("pencil"))

        self.black_white = QAction(t("black_white"), self.parent)
        _tip(self.black_white, t("black_white"))

        self.sepia = QAction(t("sepia"), self.parent)
        _tip(self.sepia, t("sepia"))

        self.negative = QAction(t("negative"), self.parent)
        _tip(self.negative, t("negative"))

        self.gaussian_blur = QAction(t("blur"), self.parent)
        _tip(self.gaussian_blur, t("blur"))

        self.sharpen = QAction(t("sharpen"), self.parent)
        _tip(self.sharpen, t("sharpen"))

        self.emboss = QAction(t("emboss"), self.parent)
        _tip(self.emboss, t("emboss"))

        self.vignette = QAction(t("vignette"), self.parent)
        _tip(self.vignette, t("vignette"))

        self.auto_enhance = QAction(t("auto_enhance"), self.parent)
        _tip(self.auto_enhance, t("auto_enhance"))

        self.resize_image = QAction(t("resize"), self.parent)
        _tip(self.resize_image, t("resize"))

        self.overlay = QAction(t("overlay"), self.parent)
        _tip(self.overlay, t("overlay"))

        self.straighten = QAction(t("straighten"), self.parent)
        _tip(self.straighten, t("straighten"))

        self.watermark = QAction(t("watermark"), self.parent)
        _tip(self.watermark, t("watermark"))

        self.check_updates = QAction(t("check_updates"), self.parent)
        _tip(self.check_updates, t("check_updates"))

        self.about = QAction(t("about"), self.parent)
        _tip(self.about, t("about"))

        self.hdr = QAction(t("hdr"), self.parent)
        _tip(self.hdr, t("hdr"))

        self.cartoon = QAction(t("cartoon"), self.parent)
        _tip(self.cartoon, t("cartoon"))

        self.glitch = QAction(t("glitch"), self.parent)
        _tip(self.glitch, t("glitch"))

        self.thermal = QAction(t("thermal"), self.parent)
        _tip(self.thermal, t("thermal"))

        self.pixelate = QAction(t("pixelate"), self.parent)
        _tip(self.pixelate, t("pixelate"))

        self.duotone = QAction(t("duotone"), self.parent)
        _tip(self.duotone, t("duotone"))

        self.theme_toggle = QAction(t("theme"), self.parent)
        _tip(self.theme_toggle, t("theme"))

        self.lang_pl = QAction(t("lang_pl"), self.parent)
        _tip(self.lang_pl, t("lang_pl"))

        self.lang_en = QAction(t("lang_en"), self.parent)
        _tip(self.lang_en, t("lang_en"))

        self.lang_es = QAction(t("lang_es"), self.parent)
        _tip(self.lang_es, t("lang_es"))

        self.shortcuts = QAction(t("shortcuts"), self.parent)
        _tip(self.shortcuts, t("shortcuts"))

        self.layers = QAction(t("layers"), self.parent)
        _tip(self.layers, t("layers"))

        self.face_detect = QAction(t("face_detect"), self.parent)
        _tip(self.face_detect, t("face_detect"))

        self.history_timeline = QAction(t("history"), self.parent)
        _tip(self.history_timeline, t("history"))

        self.text_tool = QAction(t("text_tool"), self.parent)
        _tip(self.text_tool, t("text_tool"))

        self.draw_tool = QAction(t("draw_tool"), self.parent)
        _tip(self.draw_tool, t("draw_tool"))

        self.denoise = QAction(t("denoise"), self.parent)
        _tip(self.denoise, t("denoise"))

        self.perspective = QAction(t("perspective"), self.parent)
        _tip(self.perspective, t("perspective"))

        self.lens_correction = QAction(t("lens_correction"), self.parent)
        _tip(self.lens_correction, t("lens_correction"))

        self.adjust = QAction(t("adjust"), self.parent)
        _tip(self.adjust, t("adjust"))

        self.rotate_custom = QAction(t("rotate_custom"), self.parent)
        _tip(self.rotate_custom, t("rotate_custom"))

        self.eyedropper = QAction(t("eyedropper"), self.parent)
        _tip(self.eyedropper, t("eyedropper"))

        self.histogram = QAction(t("histogram"), self.parent)
        _tip(self.histogram, t("histogram"))

    def _refresh_texts(self, lang=None):
        self.new.setText(t("new"))
        self.open.setText(t("open"))
        self.save.setText(t("save"))
        self.save_as.setText(t("save_as"))
        self.export.setText(t("export"))
        self.batch.setText(t("batch"))
        self.exit.setText(t("exit"))
        self.undo.setText(t("undo"))
        self.redo.setText(t("redo"))
        self.cut.setText(t("cut"))
        self.copy.setText(t("copy"))
        self.paste.setText(t("paste"))
        self.delete.setText(t("delete"))
        self.zoom_in.setText(t("zoom_in"))
        self.zoom_out.setText(t("zoom_out"))
        self.fit.setText(t("fit"))
        self.crop.setText(t("crop"))
        self.spot.setText(t("spot"))
        self.brush.setText(t("brush"))
        self.frame.setText(t("frame"))
        self.info.setText(t("info"))
        self.compare.setText(t("compare"))
        self.rotate_left.setText(t("rotate_left"))
        self.rotate_right.setText(t("rotate_right"))
        self.flip_h.setText(t("flip_h"))
        self.flip_v.setText(t("flip_v"))
        self.before_after.setText(t("before_after"))
        self.pencil.setText(t("pencil"))
        self.black_white.setText(t("black_white"))
        self.sepia.setText(t("sepia"))
        self.negative.setText(t("negative"))
        self.gaussian_blur.setText(t("blur"))
        self.sharpen.setText(t("sharpen"))
        self.emboss.setText(t("emboss"))
        self.vignette.setText(t("vignette"))
        self.auto_enhance.setText(t("auto_enhance"))
        self.resize_image.setText(t("resize"))
        self.overlay.setText(t("overlay"))
        self.straighten.setText(t("straighten"))
        self.watermark.setText(t("watermark"))
        self.check_updates.setText(t("check_updates"))
        self.about.setText(t("about"))
        self.hdr.setText(t("hdr"))
        self.cartoon.setText(t("cartoon"))
        self.glitch.setText(t("glitch"))
        self.thermal.setText(t("thermal"))
        self.pixelate.setText(t("pixelate"))
        self.duotone.setText(t("duotone"))
        self.theme_toggle.setText(t("theme"))
        self.shortcuts.setText(t("shortcuts"))
        self.layers.setText(t("layers"))
        self.face_detect.setText(t("face_detect"))
        self.history_timeline.setText(t("history"))
        # Refresh tooltips
        _tip(self.new, t("new"), shortcuts.NEW)
        _tip(self.open, t("open"), shortcuts.OPEN)
        _tip(self.save, t("save"), shortcuts.SAVE)
        _tip(self.save_as, t("save_as"), shortcuts.SAVE_AS)
        _tip(self.export, t("export"), shortcuts.EXPORT)
        _tip(self.batch, t("batch"))
        _tip(self.exit, t("exit"), shortcuts.EXIT)
        _tip(self.undo, t("undo"), shortcuts.UNDO)
        _tip(self.redo, t("redo"), shortcuts.REDO)
        _tip(self.cut, t("cut"), shortcuts.CUT)
        _tip(self.copy, t("copy"), shortcuts.COPY)
        _tip(self.paste, t("paste"), shortcuts.PASTE)
        _tip(self.delete, t("delete"), shortcuts.DELETE)
        _tip(self.zoom_in, t("zoom_in"), shortcuts.ZOOM_IN)
        _tip(self.zoom_out, t("zoom_out"), shortcuts.ZOOM_OUT)
        _tip(self.fit, t("fit"), shortcuts.FIT)
        _tip(self.actual_size, t("actual_size"), shortcuts.ACTUAL_SIZE)
        _tip(self.crop, t("crop"), shortcuts.CROP)
        _tip(self.spot, t("spot"))
        _tip(self.brush, t("brush"))
        _tip(self.frame, t("frame"))
        _tip(self.info, t("info"))
        _tip(self.compare, t("compare"))
        _tip(self.rotate_left, t("rotate_left"))
        _tip(self.rotate_right, t("rotate_right"))
        _tip(self.flip_h, t("flip_h"))
        _tip(self.flip_v, t("flip_v"))
        _tip(self.before_after, t("before_after"))
        _tip(self.pencil, t("pencil"))
        _tip(self.black_white, t("black_white"))
        _tip(self.sepia, t("sepia"))
        _tip(self.negative, t("negative"))
        _tip(self.gaussian_blur, t("blur"))
        _tip(self.sharpen, t("sharpen"))
        _tip(self.emboss, t("emboss"))
        _tip(self.vignette, t("vignette"))
        _tip(self.auto_enhance, t("auto_enhance"))
        _tip(self.resize_image, t("resize"))
        _tip(self.overlay, t("overlay"))
        _tip(self.straighten, t("straighten"))
        _tip(self.watermark, t("watermark"))
        _tip(self.check_updates, t("check_updates"))
        _tip(self.about, t("about"))
        _tip(self.hdr, t("hdr"))
        _tip(self.cartoon, t("cartoon"))
        _tip(self.glitch, t("glitch"))
        _tip(self.thermal, t("thermal"))
        _tip(self.pixelate, t("pixelate"))
        _tip(self.duotone, t("duotone"))
        _tip(self.theme_toggle, t("theme"))
        _tip(self.shortcuts, t("shortcuts"))
        _tip(self.layers, t("layers"))
        _tip(self.face_detect, t("face_detect"))
        _tip(self.history_timeline, t("history"))
        # New actions
        self.text_tool.setText(t("text_tool"))
        self.draw_tool.setText(t("draw_tool"))
        self.denoise.setText(t("denoise"))
        self.perspective.setText(t("perspective"))
        self.lens_correction.setText(t("lens_correction"))
        _tip(self.text_tool, t("text_tool"))
        _tip(self.draw_tool, t("draw_tool"))
        _tip(self.denoise, t("denoise"))
        _tip(self.perspective, t("perspective"))
        _tip(self.lens_correction, t("lens_correction"))
        # New v0.4.1 actions
        self.adjust.setText(t("adjust"))
        self.rotate_custom.setText(t("rotate_custom"))
        self.eyedropper.setText(t("eyedropper"))
        self.histogram.setText(t("histogram"))
        _tip(self.adjust, t("adjust"))
        _tip(self.rotate_custom, t("rotate_custom"))
        _tip(self.eyedropper, t("eyedropper"))
        _tip(self.histogram, t("histogram"))
