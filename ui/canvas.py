#!/usr/bin/env python3
from __future__ import annotations
from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

class Canvas(QWidget):
    spot_clicked = Signal(object)
    spot_wheel = Signal(int)
    brush_stroke = Signal(object, object)
    brush_wheel = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap = None
        self.update()
        self._pixmap_before = None
        self.update()
        self._pixmap_after = None
        self.update()
        self._zoom = 1.0
        self._offset_x = 0.0
        self._offset_y = 0.0
        self._dragging = False
        self._last_pos = None
        self._crop_mode = False
        self._crop_start = None
        self._crop_end = None
        self._spot_mode = False
        self._brush_mode = False
        self._brush_points = None
        self._brush_button = None
        self._ba_mode = False
        self._ba_split = 0.5
        self._ba_drag = False
        self.setAutoFillBackground(True)
        self.setStyleSheet("background: #141414;")
        self.setCursor(Qt.OpenHandCursor)

    def set_pixmap(self, pixmap):
        self._pixmap = pixmap
        self.update()
        self._offset_x = 0.0
        self._offset_y = 0.0
        self._zoom = 1.0
        self._crop_mode = False
        self._ba_mode = False
        self._spot_mode = False
        self._brush_mode = False
        self._brush_points = None
        self._crop_start = None
        self._crop_end = None
        self.update()

    def set_before_after(self, before, after):
        self._pixmap_before = before
        self.update()
        self._pixmap_after = after
        self.update()
        self._offset_x = 0.0
        self._offset_y = 0.0
        self._zoom = 1.0
        self._crop_mode = False
        self._ba_mode = True
        self._ba_split = 0.5
        self.setCursor(Qt.SplitHCursor)
        self.update()

    def cancel_before_after(self):
        self._ba_mode = False
        self._ba_split = 0.5
        self.setCursor(Qt.OpenHandCursor)
        self.update()

    def start_crop(self):
        self._crop_mode = True
        self._crop_start = None
        self._crop_end = None
        self.setCursor(Qt.CrossCursor)
        self.update()

    def cancel_crop(self):
        self._crop_mode = False
        self._crop_start = None
        self._crop_end = None
        self.setCursor(Qt.OpenHandCursor)
        self.update()

    def start_spot(self):
        self._spot_mode = True
        self.setCursor(Qt.CrossCursor)
        self.update()

    def cancel_spot(self):
        self._spot_mode = False
        self.setCursor(Qt.OpenHandCursor)
        self.update()

    def start_brush(self):
        self._brush_mode = True
        self._brush_points = None
        self.setCursor(Qt.CrossCursor)
        self.update()

    def cancel_brush(self):
        self._brush_mode = False
        self._brush_points = None
        self.setCursor(Qt.OpenHandCursor)
        self.update()

    def get_crop_rect(self):
        if self._crop_start is None or self._crop_end is None or self._pixmap is None:
            return None
        x1 = min(self._crop_start.x(), self._crop_end.x())
        y1 = min(self._crop_start.y(), self._crop_end.y())
        x2 = max(self._crop_start.x(), self._crop_end.x())
        y2 = max(self._crop_start.y(), self._crop_end.y())
        iw = self._pixmap.width() * self._zoom
        self.update()
        ih = self._pixmap.height() * self._zoom
        self.update()
        cx = (self.width() - iw) / 2 + self._offset_x
        cy = (self.height() - ih) / 2 + self._offset_y
        x1 = (x1 - cx) / self._zoom
        y1 = (y1 - cy) / self._zoom
        x2 = (x2 - cx) / self._zoom
        y2 = (y2 - cy) / self._zoom
        x1 = max(0, min(x1, self._pixmap.width()))
        self.update()
        y1 = max(0, min(y1, self._pixmap.height()))
        self.update()
        x2 = max(0, min(x2, self._pixmap.width()))
        self.update()
        y2 = max(0, min(y2, self._pixmap.height()))
        self.update()
        if x2 - x1 < 10 or y2 - y1 < 10:
            return None
        return (int(x1), int(y1), int(x2), int(y2))

    def _img_rect(self):
        if self._ba_mode and self._pixmap_after:
            pm = self._pixmap_after
            self.update()
        elif self._pixmap:
            pm = self._pixmap
            self.update()
        else:
            return None
        iw = pm.width() * self._zoom
        ih = pm.height() * self._zoom
        x = (self.width() - iw) / 2 + self._offset_x
        y = (self.height() - ih) / 2 + self._offset_y
        return (x, y, iw, ih)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#141414"))

        if self._ba_mode and self._pixmap_before and self._pixmap_after:
            r = self._img_rect()
            if r:
                x, y, iw, ih = r
                split_x = x + iw * self._ba_split
                # Before (left)
                src_before = QRectF(0, 0, self._pixmap_before.width() * self._ba_split, self._pixmap_before.height())
                self.update()
                dst_before = QRectF(x, y, iw * self._ba_split, ih)
                painter.drawPixmap(dst_before, self._pixmap_before, src_before)
                # After (right)
                src_after = QRectF(self._pixmap_after.width() * self._ba_split, 0, self._pixmap_after.width() * (1 - self._ba_split), self._pixmap_after.height())
                self.update()
                dst_after = QRectF(split_x, y, iw * (1 - self._ba_split), ih)
                painter.drawPixmap(dst_after, self._pixmap_after, src_after)
                # Divider line
                pen = QPen(QColor("#FFFFFF"))
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawLine(int(split_x), int(y), int(split_x), int(y + ih))
                # Labels
                painter.setPen(QColor("#FFFFFF"))
                painter.drawText(int(x + 10), int(y + 20), "PRZED")
                painter.drawText(int(x + iw - 60), int(y + 20), "PO")

        elif self._pixmap and not self._pixmap.isNull():
            r = self._img_rect()
            if r:
                x, y, iw, ih = r
                painter.drawPixmap(QRectF(x, y, iw, ih), self._pixmap, QRectF(self._pixmap.rect()))
                if self._crop_mode and self._crop_start and self._crop_end:
                    pen = QPen(QColor("#4A9EFF"))
                    pen.setWidth(2)
                    pen.setStyle(Qt.PenStyle.DashLine)
                    painter.setPen(pen)
                    painter.drawRect(QRectF(self._crop_start, self._crop_end))
                    painter.fillRect(QRectF(self._crop_start, self._crop_end), QColor(74, 158, 255, 30))

        painter.end()

    def mousePressEvent(self, event):
        if self._brush_mode:
            r = self._img_rect()
            if r and self._pixmap and not self._pixmap.isNull():
                x, y, iw, ih = r
                px = (event.pos().x() - x) / self._zoom
                py = (event.pos().y() - y) / self._zoom
                if 0 <= px < self._pixmap.width() and 0 <= py < self._pixmap.height():
                    self._brush_points = [QPointF(px, py)]
                    self._brush_button = event.button()
            return
        if self._spot_mode:
            r = self._img_rect()
            if r and self._pixmap and not self._pixmap.isNull():
                x, y, iw, ih = r
                px = (event.pos().x() - x) / self._zoom
                py = (event.pos().y() - y) / self._zoom
                if 0 <= px < self._pixmap.width() and 0 <= py < self._pixmap.height():
                    self.spot_clicked.emit(QPointF(px, py))
            return
        if self._ba_mode:
            r = self._img_rect()
            if r:
                x, y, iw, ih = r
                split_x = x + iw * self._ba_split
                if abs(event.pos().x() - split_x) < 10:
                    self._ba_drag = True
            return
        if self._crop_mode:
            self._crop_start = event.pos()
            self._crop_end = event.pos()
            return
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._last_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self._brush_mode:
            if self._brush_points is not None:
                r = self._img_rect()
                if r:
                    x, y, iw, ih = r
                    px = (event.pos().x() - x) / self._zoom
                    py = (event.pos().y() - y) / self._zoom
                    px = max(0, min(px, self._pixmap.width()))
                    py = max(0, min(py, self._pixmap.height()))
                    self._brush_points.append(QPointF(px, py))
            return
        if self._spot_mode:
            return
        if self._ba_mode and self._ba_drag:
            r = self._img_rect()
            if r:
                x, y, iw, ih = r
                self._ba_split = (event.pos().x() - x) / iw
                self._ba_split = max(0.05, min(0.95, self._ba_split))
                self.update()
            return
        if self._crop_mode and self._crop_start:
            self._crop_end = event.pos()
            self.update()
            return
        if self._dragging and self._last_pos:
            dx = event.pos().x() - self._last_pos.x()
            dy = event.pos().y() - self._last_pos.y()
            self._offset_x += dx
            self._offset_y += dy
            self._last_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if self._brush_mode:
            if self._brush_points:
                self.brush_stroke.emit(self._brush_points, self._brush_button)
            self._brush_points = None
            self._brush_button = None
            return
        if self._spot_mode:
            return
        if self._ba_mode:
            self._ba_drag = False
            return
        if self._crop_mode:
            self._crop_end = event.pos()
            self.update()
            return
        if event.button() == Qt.LeftButton:
            self._dragging = False
            self.setCursor(Qt.OpenHandCursor)

    def wheelEvent(self, event):
        if self._ba_mode:
            return
        if self._spot_mode:
            self.spot_wheel.emit(event.angleDelta().y())
            return
        if self._brush_mode:
            self.brush_wheel.emit(event.angleDelta().y())
            return
        if self._pixmap is None or self._pixmap.isNull():
            return
        old_zoom = self._zoom
        delta = event.angleDelta().y()
        if delta > 0:
            self._zoom = min(self._zoom * 1.15, 32.0)
        else:
            self._zoom = max(self._zoom / 1.15, 0.05)
        mx = event.position().x()
        my = event.position().y()
        old_iw = self._pixmap.width() * old_zoom
        self.update()
        old_ih = self._pixmap.height() * old_zoom
        self.update()
        old_x = (self.width() - old_iw) / 2 + self._offset_x
        old_y = (self.height() - old_ih) / 2 + self._offset_y
        rel_x = (mx - old_x) / old_zoom
        rel_y = (my - old_y) / old_zoom
        new_iw = self._pixmap.width() * self._zoom
        self.update()
        new_ih = self._pixmap.height() * self._zoom
        self.update()
        new_x = mx - rel_x * self._zoom
        new_y = my - rel_y * self._zoom
        self._offset_x = new_x - (self.width() - new_iw) / 2
        self._offset_y = new_y - (self.height() - new_ih) / 2
        self.update()
