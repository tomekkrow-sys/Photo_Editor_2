#!/usr/bin/env python3
from __future__ import annotations
import cv2
import numpy as np
from PIL import Image
from PySide6.QtGui import QImage, QPixmap

def prepare_preview(pil_img, max_dim=2400):
    w, h = pil_img.size
    if max(w, h) > max_dim:
        r = max_dim / max(w, h)
        return pil_img.resize((int(w*r), int(h*r)), Image.Resampling.LANCZOS)
    return pil_img.copy()

def pil_to_cv(pil_img):
    arr = np.array(pil_img)
    if arr.shape[2] == 4:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGBA2BGR)
    else:
        arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    return arr.astype(np.float32) / 255.0

def cv_to_pil(arr):
    arr = np.clip(arr * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))

def apply_adjustments_cv(arr, adj):
    out = arr.copy()
    if adj.exposure != 0.0 or adj.contrast != 0.0:
        alpha = 1.0 + adj.contrast / 100.0
        beta = adj.exposure / 5.0
        out = np.clip(out * alpha + beta, 0, 1)
    if adj.highlights != 0.0 or adj.shadows != 0.0:
        gray = cv2.cvtColor((out*255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)/255.0
        gray = gray[:,:,None]
        if adj.highlights != 0.0:
            mask = (gray > 0.5).astype(np.float32)
            out = out * (1.0 - mask * adj.highlights / 200.0)
        if adj.shadows != 0.0:
            mask = (gray <= 0.5).astype(np.float32)
            out = out * (1.0 + mask * adj.shadows / 100.0)
        out = np.clip(out, 0, 1)
    if adj.whites != 0.0 or adj.blacks != 0.0:
        wp = 1.0 - adj.whites / 200.0
        bp = adj.blacks / 200.0
        if wp > bp:
            out = np.clip((out - bp) / (wp - bp), 0, 1)
    if adj.temperature != 0.0:
        out[:,:,2] = np.clip(out[:,:,2] + adj.temperature / 300.0, 0, 1)  # R
        out[:,:,0] = np.clip(out[:,:,0] - adj.temperature / 300.0, 0, 1)  # B
    if adj.tint != 0.0:
        out[:,:,2] = np.clip(out[:,:,2] + adj.tint / 400.0, 0, 1)        # R
        out[:,:,1] = np.clip(out[:,:,1] - adj.tint / 400.0, 0, 1)        # G
    if adj.saturation != 0.0:
        hsv = cv2.cvtColor((out*255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] = np.clip(hsv[:,:,1] * (1.0 + adj.saturation / 100.0), 0, 255)
        out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32) / 255.0
    if adj.vibrance != 0.0:
        gray = cv2.cvtColor((out*255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32)/255.0
        gray = gray[:,:,None]
        mx = np.max(out, axis=2, keepdims=True)
        mn = np.min(out, axis=2, keepdims=True)
        sat = mx - mn
        mask = 1.0 - np.abs(gray - 0.5) * 2.0
        boost = 1.0 + (adj.vibrance / 100.0) * (1.0 - sat) * mask
        out = np.clip((out - gray) * boost + gray, 0, 1)
    if adj.sharpness > 0.0:
        blur = cv2.GaussianBlur(out, (0,0), 1.5)
        out = np.clip(out + (out - blur) * (adj.sharpness / 50.0), 0, 1)
    if adj.clarity != 0.0:
        blur = cv2.GaussianBlur(out, (0,0), 3.0)
        out = np.clip(out + (out - blur) * (adj.clarity / 100.0), 0, 1)
    return out

def apply_adjustments_arr(arr, adj):
    return apply_adjustments_cv(arr, adj)

def arr_to_pil(arr):
    return cv_to_pil(arr)

def pil_to_qpixmap(pil_img):
    if pil_img.mode == "RGBA":
        data = pil_img.tobytes("raw", "RGBA")
        qimg = QImage(data, pil_img.width, pil_img.height, pil_img.width * 4, QImage.Format.Format_RGBA8888)
    else:
        data = pil_img.tobytes("raw", "RGB")
        qimg = QImage(data, pil_img.width, pil_img.height, pil_img.width * 3, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(qimg)
