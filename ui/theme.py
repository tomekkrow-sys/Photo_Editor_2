#!/usr/bin/env python3
"""Central theme system for Photo Editor 2 — Modern UI."""

from __future__ import annotations

# ==========================================================
# DARK THEME (default) — Modern dark with blue accent
# ==========================================================

DARK_THEME = {
    "bg_primary": "#121216",
    "bg_secondary": "#1A1A20",
    "bg_tertiary": "#22222A",
    "bg_canvas": "#0E0E12",
    "accent": "#4A9EFF",
    "accent_hover": "#6CB4FF",
    "accent_pressed": "#3380DD",
    "accent_subtle": "#4A9EFF22",
    "text_primary": "#EEEEF0",
    "text_secondary": "#9898A4",
    "text_muted": "#5E5E6C",
    "border": "#2C2C36",
    "border_light": "#3A3A46",
    "success": "#34D399",
    "warning": "#FBBF24",
    "danger": "#F87171",
    "group_bg": "#1A1A20",
    "slider_groove": "#2C2C36",
    "slider_handle": "#4A9EFF",
    "input_bg": "#22222A",
    "input_border": "#2C2C36",
    "button_bg": "#2A2A34",
    "button_hover": "#36364A",
    "scrollbar_bg": "#1A1A20",
    "scrollbar_handle": "#3A3A46",
    "tooltip_bg": "#2A2A34",
    "tooltip_text": "#EEEEF0",
    "shadow": "#000000",
}

# ==========================================================
# LIGHT THEME — Clean, bright, Apple-like
# ==========================================================

LIGHT_THEME = {
    "bg_primary": "#F8F8FA",
    "bg_secondary": "#FFFFFF",
    "bg_tertiary": "#EEEEF2",
    "bg_canvas": "#E4E4EA",
    "accent": "#0066CC",
    "accent_hover": "#007AFF",
    "accent_pressed": "#0055AA",
    "accent_subtle": "#0066CC18",
    "text_primary": "#1C1C1E",
    "text_secondary": "#636366",
    "text_muted": "#AEAEB2",
    "border": "#D1D1D6",
    "border_light": "#C6C6CA",
    "success": "#28A745",
    "warning": "#F5A623",
    "danger": "#DC3545",
    "group_bg": "#FFFFFF",
    "slider_groove": "#D1D1D6",
    "slider_handle": "#0066CC",
    "input_bg": "#FFFFFF",
    "input_border": "#D1D1D6",
    "button_bg": "#E5E5EA",
    "button_hover": "#D1D1D6",
    "scrollbar_bg": "#F0F0F4",
    "scrollbar_handle": "#C6C6CA",
    "tooltip_bg": "#1C1C1E",
    "tooltip_text": "#FFFFFF",
    "shadow": "#000000",
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
        font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', 'Noto Sans', Arial, sans-serif;
        font-size: 14px;
        font-weight: 500;
        selection-background-color: {t["accent"]};
        selection-color: white;
    }}

    /* === MAIN WINDOW === */
    QMainWindow {{
        background-color: {t["bg_primary"]};
    }}
    QSplitter::handle {{
        background: {t["border"]};
        width: 1px;
    }}
    QSplitter::handle:hover {{
        background: {t["accent"]};
    }}

    /* === MENU BAR === */
    QMenuBar {{
        background: {t["bg_secondary"]};
        color: {t["text_primary"]};
        border-bottom: 1px solid {t["border"]};
        padding: 2px 4px;
        font-size: 13px;
        font-weight: 600;
    }}
    QMenuBar::item {{
        padding: 6px 10px;
        border-radius: 6px;
        margin: 1px 1px;
    }}
    QMenuBar::item:selected {{
        background: {t["accent_subtle"]};
        color: {t["accent"]};
    }}
    QMenu {{
        background: {t["bg_secondary"]};
        color: {t["text_primary"]};
        border: 1px solid {t["border"]};
        border-radius: 10px;
        padding: 6px;
    }}
    QMenu::item {{
        padding: 8px 20px 8px 14px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
    }}
    QMenu::item:selected {{
        background: {t["accent"]};
        color: white;
    }}
    QMenu::separator {{
        height: 1px;
        background: {t["border"]};
        margin: 4px 10px;
    }}

    /* === TOOLBAR === */
    QToolBar {{
        background: {t["bg_secondary"]};
        border-bottom: 1px solid {t["border"]};
        spacing: 2px;
        padding: 3px 6px;
    }}
    QToolButton {{
        color: {t["text_secondary"]};
        background: transparent;
        border: none;
        padding: 5px 10px;
        font-size: 13px;
        font-weight: 600;
        border-radius: 6px;
    }}
    QToolButton:hover {{
        background: {t["button_hover"]};
        color: {t["text_primary"]};
    }}
    QToolButton:pressed {{
        background: {t["accent"]};
        color: white;
    }}
    QToolButton:checked {{
        background: {t["accent_subtle"]};
        color: {t["accent"]};
        border: 1px solid {t["accent"]};
    }}

    /* === STATUS BAR === */
    QStatusBar {{
        background: {t["bg_secondary"]};
        color: {t["text_secondary"]};
        border-top: 1px solid {t["border"]};
        padding: 3px 10px;
        font-size: 12px;
        font-weight: 500;
    }}
    QStatusBar QLabel {{
        color: {t["text_secondary"]};
        padding: 0 8px;
        font-size: 12px;
        font-weight: 500;
    }}

    /* === SCROLL AREA === */
    QScrollArea {{
        border: none;
        background: {t["bg_secondary"]};
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        border-radius: 4px;
        margin: 2px;
    }}
    QScrollBar::handle:vertical {{
        background: {t["scrollbar_handle"]};
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {t["accent"]};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}

    /* === GROUP BOX === */
    QGroupBox {{
        background: {t["group_bg"]};
        border: 1px solid {t["border"]};
        border-radius: 10px;
        margin-top: 12px;
        padding: 18px 10px 10px 10px;
        font-weight: 700;
        color: {t["text_primary"]};
        font-size: 13px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        left: 14px;
        padding: 0 8px;
        color: {t["accent"]};
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
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
    QSlider::handle:horizontal:hover {{
        background: {t["accent_hover"]};
        width: 18px;
        height: 18px;
        border-radius: 9px;
        margin: -7px 0;
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
        padding: 8px 20px;
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background: {t["button_hover"]};
        border-color: {t["border_light"]};
    }}
    QPushButton:pressed {{
        background: {t["accent_pressed"]};
        color: white;
        border-color: {t["accent_pressed"]};
    }}
    QPushButton:focus {{
        border: 1px solid {t["accent"]};
    }}
    QPushButton[accent="success"] {{
        background: {t["success"]};
        color: white;
        font-weight: 700;
        border: none;
    }}
    QPushButton[accent="success"]:hover {{
        background: {t["accent_hover"]};
    }}

    /* === INPUT FIELDS === */
    QLineEdit {{
        background: {t["input_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["input_border"]};
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
    }}
    QLineEdit:focus {{
        border: 1px solid {t["accent"]};
        background: {t["bg_tertiary"]};
    }}
    QComboBox {{
        background: {t["input_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["input_border"]};
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
    }}
    QComboBox:focus {{
        border: 1px solid {t["accent"]};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox QAbstractItemView {{
        background: {t["bg_secondary"]};
        color: {t["text_primary"]};
        border: 1px solid {t["border"]};
        border-radius: 8px;
        padding: 4px;
        selection-background-color: {t["accent"]};
        selection-color: white;
    }}
    QSpinBox {{
        background: {t["input_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["input_border"]};
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 13px;
    }}
    QSpinBox:focus {{
        border: 1px solid {t["accent"]};
    }}
    QDoubleSpinBox {{
        background: {t["input_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["input_border"]};
        padding: 6px 10px;
        border-radius: 8px;
        font-size: 13px;
    }}

    /* === LABELS === */
    QLabel {{
        color: {t["text_primary"]};
        font-size: 13px;
        font-weight: 500;
        background: transparent;
    }}

    /* === TABLE === */
    QTableWidget {{
        background: {t["bg_secondary"]};
        color: {t["text_primary"]};
        border: 1px solid {t["border"]};
        gridline-color: {t["border"]};
        border-radius: 8px;
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
        padding: 8px 12px;
        font-weight: 700;
        font-size: 12px;
        text-transform: uppercase;
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
        height: 6px;
        text-align: center;
        color: transparent;
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
        border-radius: 8px;
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 6px 8px;
        border-radius: 6px;
    }}
    QListWidget::item:selected {{
        background: {t["accent"]};
        color: white;
    }}
    QListWidget::item:hover {{
        background: {t["button_hover"]};
    }}

    /* === TAB WIDGET === */
    QTabWidget::pane {{
        border: 1px solid {t["border"]};
        border-radius: 8px;
        background: {t["bg_secondary"]};
        top: -1px;
    }}
    QTabBar::tab {{
        background: {t["bg_tertiary"]};
        color: {t["text_secondary"]};
        border: 1px solid {t["border"]};
        padding: 8px 16px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        font-weight: 600;
        font-size: 12px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background: {t["bg_secondary"]};
        color: {t["accent"]};
        border-bottom-color: {t["bg_secondary"]};
    }}
    QTabBar::tab:hover {{
        background: {t["button_hover"]};
        color: {t["text_primary"]};
    }}

    /* === CHECKBOX === */
    QCheckBox {{
        spacing: 8px;
        font-size: 13px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {t["border_light"]};
        border-radius: 4px;
        background: {t["input_bg"]};
    }}
    QCheckBox::indicator:checked {{
        background: {t["accent"]};
        border-color: {t["accent"]};
    }}
    QCheckBox::indicator:hover {{
        border-color: {t["accent"]};
    }}

    /* === TOOLTIP === */
    QToolTip {{
        background: {t["tooltip_bg"]};
        color: {t["tooltip_text"]};
        border: 1px solid {t["border"]};
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}

    /* === DOCK WIDGET === */
    QDockWidget {{
        titlebar-close-icon: none;
        titlebar-normal-icon: none;
    }}
    QDockWidget::title {{
        background: {t["bg_secondary"]};
        border-bottom: 1px solid {t["border"]};
        padding: 8px;
        font-weight: 700;
        font-size: 12px;
        text-transform: uppercase;
        color: {t["accent"]};
    }}

    /* === FRAME === */
    QFrame[frameShape="4"] {{
        background: {t["border"]};
        max-height: 1px;
    }}
    """
