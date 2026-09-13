#!/usr/bin/env python3
"""Central theme system for Photo Editor 2."""

from __future__ import annotations

# ==========================================================
# DARK THEME (domyślny)
# ==========================================================

DARK_THEME = {
    # Paleta kolorów
    "bg_primary": "#1B1B1F",
    "bg_secondary": "#232328",
    "bg_tertiary": "#2B2B32",
    "bg_canvas": "#111114",
    "accent": "#5B9EF4",
    "accent_hover": "#7BB3FF",
    "accent_pressed": "#3D7AD4",
    "text_primary": "#E8E8EC",
    "text_secondary": "#A0A0AB",
    "text_muted": "#6B6B76",
    "border": "#3A3A42",
    "border_light": "#4A4A54",
    "success": "#4CAF7D",
    "warning": "#E5A93B",
    "danger": "#E05555",
    "group_bg": "#232328",
    "slider_groove": "#3A3A42",
    "slider_handle": "#5B9EF4",
    "input_bg": "#2B2B32",
    "input_border": "#3A3A42",
    "button_bg": "#333340",
    "button_hover": "#44445A",
    "scrollbar_bg": "#2B2B32",
    "scrollbar_handle": "#4A4A54",
}

# ==========================================================
# LIGHT THEME
# ==========================================================

LIGHT_THEME = {
    "bg_primary": "#F5F5F7",
    "bg_secondary": "#FFFFFF",
    "bg_tertiary": "#EAEAEE",
    "bg_canvas": "#E0E0E4",
    "accent": "#0066CC",
    "accent_hover": "#007AFF",
    "accent_pressed": "#0055AA",
    "text_primary": "#1A1A1E",
    "text_secondary": "#5A5A66",
    "text_muted": "#8A8A96",
    "border": "#D0D0D8",
    "border_light": "#C0C0C8",
    "success": "#2D8B55",
    "warning": "#CC8800",
    "danger": "#CC3333",
    "group_bg": "#FFFFFF",
    "slider_groove": "#D0D0D8",
    "slider_handle": "#0066CC",
    "input_bg": "#FFFFFF",
    "input_border": "#D0D0D8",
    "button_bg": "#E0E0E6",
    "button_hover": "#D0D0D8",
    "scrollbar_bg": "#F0F0F4",
    "scrollbar_handle": "#C0C0C8",
}


def get_theme(name: str = "dark") -> dict:
    return DARK_THEME if name == "dark" else LIGHT_THEME


def build_stylesheet(theme: dict) -> str:
    t = theme
    return f"""
    /* === GLOBAL === */
    QWidget {{
        background-color: {t["bg_primary"]};
        color: {t["text_primary"]};
        font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
        font-size: 14px;
        font-weight: 400;
    }}

    /* === MAIN WINDOW === */
    QMainWindow {{
        background-color: {t["bg_primary"]};
    }}
    QSplitter::handle {{
        background: {t["border"]};
        width: 2px;
    }}

    /* === MENU BAR === */
    QMenuBar {{
        background: {t["bg_secondary"]};
        color: {t["text_primary"]};
        border-bottom: 1px solid {t["border"]};
        padding: 2px 4px;
        font-size: 14px;
        font-weight: 500;
    }}
    QMenuBar::item {{
        padding: 6px 12px;
        border-radius: 4px;
    }}
    QMenuBar::item:selected {{
        background: {t["accent"]};
        color: white;
    }}
    QMenu {{
        background: {t["bg_secondary"]};
        color: {t["text_primary"]};
        border: 1px solid {t["border"]};
        border-radius: 6px;
        padding: 4px;
    }}
    QMenu::item {{
        padding: 8px 24px 8px 12px;
        border-radius: 4px;
        font-size: 14px;
    }}
    QMenu::item:selected {{
        background: {t["accent"]};
        color: white;
    }}
    QMenu::separator {{
        height: 1px;
        background: {t["border"]};
        margin: 4px 8px;
    }}

    /* === TOOLBAR === */
    QToolBar {{
        background: {t["bg_secondary"]};
        border-bottom: 1px solid {t["border"]};
        spacing: 2px;
        padding: 3px 8px;
    }}
    QToolButton {{
        color: {t["text_secondary"]};
        background: transparent;
        border: none;
        padding: 5px 10px;
        font-size: 13px;
        border-radius: 4px;
    }}
    QToolButton:hover {{
        background: {t["button_hover"]};
        color: {t["text_primary"]};
    }}
    QToolButton:pressed {{
        background: {t["accent"]};
        color: white;
    }}

    /* === STATUS BAR === */
    QStatusBar {{
        background: {t["bg_secondary"]};
        color: {t["text_secondary"]};
        border-top: 1px solid {t["border"]};
        padding: 2px 8px;
        font-size: 13px;
    }}
    QStatusBar QLabel {{
        color: {t["text_secondary"]};
        padding: 0 8px;
        font-size: 13px;
    }}

    /* === SCROLL AREA (right panel) === */
    QScrollArea {{
        border: none;
        background: {t["bg_secondary"]};
    }}
    QScrollBar:vertical {{
        background: {t["scrollbar_bg"]};
        width: 8px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical {{
        background: {t["scrollbar_handle"]};
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* === GROUP BOX === */
    QGroupBox {{
        background: {t["group_bg"]};
        border: 1px solid {t["border"]};
        border-radius: 8px;
        margin-top: 10px;
        padding: 14px 8px 8px 8px;
        font-weight: 600;
        color: {t["text_primary"]};
        font-size: 13px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 12px;
        padding: 0 6px;
        color: {t["accent"]};
        font-size: 13px;
    }}

    /* === SLIDER === */
    QSlider::groove:horizontal {{
        height: 4px;
        background: {t["slider_groove"]};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        width: 16px;
        height: 16px;
        background: {t["slider_handle"]};
        border-radius: 8px;
        margin: -6px 0;
        border: 2px solid {t["bg_secondary"]};
    }}
    QSlider::sub-page:horizontal {{
        background: {t["accent"]};
        border-radius: 2px;
    }}
    QSlider::add-page:horizontal {{
        background: {t["slider_groove"]};
        border-radius: 2px;
    }}

    /* === BUTTONS === */
    QPushButton {{
        background: {t["button_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["border"]};
        padding: 7px 18px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 14px;
    }}
    QPushButton:hover {{
        background: {t["button_hover"]};
        border-color: {t["border_light"]};
    }}
    QPushButton:pressed {{
        background: {t["accent_pressed"]};
        color: white;
    }}

    /* === INPUT FIELDS === */
    QLineEdit {{
        background: {t["input_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["input_border"]};
        padding: 7px 12px;
        border-radius: 6px;
        font-size: 14px;
    }}
    QLineEdit:focus {{
        border-color: {t["accent"]};
    }}
    QComboBox {{
        background: {t["input_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["input_border"]};
        padding: 7px 12px;
        border-radius: 6px;
        font-size: 14px;
    }}
    QComboBox:focus {{
        border-color: {t["accent"]};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}

    /* === LABELS === */
    QLabel {{
        color: {t["text_primary"]};
        font-size: 14px;
    }}

    /* === TABLE === */
    QTableWidget {{
        background: {t["bg_secondary"]};
        color: {t["text_primary"]};
        border: 1px solid {t["border"]};
        gridline-color: {t["border"]};
        border-radius: 6px;
    }}
    QTableWidget::item:selected {{
        background: {t["accent"]};
        color: white;
    }}
    QHeaderView::section {{
        background: {t["bg_tertiary"]};
        color: {t["text_primary"]};
        border: none;
        border-bottom: 1px solid {t["border"]};
        padding: 8px 10px;
        font-weight: 600;
        font-size: 13px;
    }}

    /* === DIALOGS === */
    QDialog {{
        background: {t["bg_primary"]};
        color: {t["text_primary"]};
    }}

    /* === MESSAGE BOX === */
    QMessageBox {{
        background: {t["bg_primary"]};
    }}

    /* === PROGRESS BAR === */
    QProgressBar {{
        background: {t["slider_groove"]};
        border: none;
        border-radius: 4px;
        height: 8px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background: {t["accent"]};
        border-radius: 4px;
    }}

    /* === LIST WIDGET === */
    QListWidget {{
        background: {t["input_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["border"]};
        border-radius: 6px;
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 6px 8px;
        border-radius: 4px;
    }}
    QListWidget::item:selected {{
        background: {t["accent"]};
        color: white;
    }}
    QListWidget::item:hover {{
        background: {t["button_hover"]};
    }}
    """
