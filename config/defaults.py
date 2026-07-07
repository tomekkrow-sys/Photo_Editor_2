#!/usr/bin/env python3
"""
Photo Editor 2.0
Default application settings.
"""

from __future__ import annotations

# ==========================================================
# WINDOW
# ==========================================================

DEFAULT_WINDOW_WIDTH: int = 1600
DEFAULT_WINDOW_HEIGHT: int = 900

DEFAULT_WINDOW_X: int = 100
DEFAULT_WINDOW_Y: int = 100

DEFAULT_MAXIMIZED: bool = False

# ==========================================================
# LANGUAGE
# ==========================================================

DEFAULT_LANGUAGE: str = "pl_PL"

# ==========================================================
# THEME
# ==========================================================

DEFAULT_THEME: str = "dark"

# ==========================================================
# CANVAS
# ==========================================================

DEFAULT_CANVAS_BACKGROUND: str = "#2B2B2B"

DEFAULT_SHOW_GRID: bool = False

DEFAULT_GRID_SIZE: int = 25

DEFAULT_SMOOTH_TRANSFORM: bool = True

# ==========================================================
# ZOOM
# ==========================================================

DEFAULT_ZOOM: int = 100

DEFAULT_MIN_ZOOM: int = 5

DEFAULT_MAX_ZOOM: int = 3200

# ==========================================================
# HISTORY
# ==========================================================

DEFAULT_HISTORY_SIZE: int = 100

# ==========================================================
# AUTOSAVE
# ==========================================================

DEFAULT_AUTOSAVE: bool = True

DEFAULT_AUTOSAVE_INTERVAL: int = 300

# ==========================================================
# EXPORT
# ==========================================================

DEFAULT_EXPORT_FORMAT: str = "PNG"

DEFAULT_JPEG_QUALITY: int = 95

# ==========================================================
# UI
# ==========================================================

SHOW_STATUSBAR: bool = True

SHOW_TOOLBAR: bool = True

SHOW_LEFT_PANEL: bool = True

SHOW_RIGHT_PANEL: bool = True