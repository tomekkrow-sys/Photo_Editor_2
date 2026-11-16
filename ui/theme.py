#!/usr/bin/env python3
"""Central theme system for Photo Editor 2 — Modern UI.

Provides:
- DARK_THEME / LIGHT_THEME token dicts
- current theme state: current_name(), current_theme(), tc(key)
- set_theme() with change-listener notification (widgets repaint)
- apply_theme() — application-level stylesheet (dialogs inherit)
- build_stylesheet() — full QSS for the given theme
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication

# ==========================================================
# SVG assets used inside QSS (checkmark, combo/spin arrows)
# ==========================================================

_UI_ICONS = (Path(__file__).resolve().parent.parent / "resources" / "icons" / "ui").as_posix()


def _icon(name: str) -> str:
    return f"{_UI_ICONS}/{name}.svg"


# ==========================================================
# DARK THEME (default) — Modern dark with blue accent
# NOTE: Qt parses 8-digit hex as #AARRGGBB (alpha FIRST).
# ==========================================================

DARK_THEME = {
    "name": "dark",
    "bg_primary": "#121216",
    "bg_secondary": "#1A1A20",
    "bg_tertiary": "#22222A",
    "bg_canvas": "#0E0E12",
    "accent": "#4A9EFF",
    "accent_hover": "#6CB4FF",
    "accent_pressed": "#3380DD",
    "accent_subtle": "#224A9EFF",  # alpha 0x22 (~13%) + #4A9EFF
    "text_primary": "#EEEEF0",
    "text_secondary": "#9898A4",
    "text_muted": "#5E5E6C",
    "border": "#2C2C36",
    "border_light": "#3A3A46",
    "success": "#34D399",
    "success_hover": "#4AE0A8",
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
    "name": "light",
    "bg_primary": "#F8F8FA",
    "bg_secondary": "#FFFFFF",
    "bg_tertiary": "#EEEEF2",
    "bg_canvas": "#E4E4EA",
    "accent": "#0066CC",
    "accent_hover": "#007AFF",
    "accent_pressed": "#0055AA",
    "accent_subtle": "#180066CC",  # alpha 0x18 (~9%) + #0066CC
    "text_primary": "#1C1C1E",
    "text_secondary": "#636366",
    "text_muted": "#AEAEB2",
    "border": "#D1D1D6",
    "border_light": "#C6C6CA",
    "success": "#28A745",
    "success_hover": "#34C759",
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


# ==========================================================
# THEME STATE
# ==========================================================

_current_name = "dark"
_listeners: list = []  # callables invoked after theme change


def get_theme(name: str | None = None) -> dict:
    """Return theme dict by name (defaults to current)."""
    n = (name or _current_name).lower()
    return LIGHT_THEME if n == "light" else DARK_THEME


def current_name() -> str:
    return _current_name


def current_theme() -> dict:
    return get_theme(_current_name)


def tc(key: str, default: str = "") -> str:
    """Theme color shortcut — tc('accent')."""
    return current_theme().get(key, default)


def on_change(cb) -> None:
    """Register a callback invoked after every set_theme()."""
    if cb not in _listeners:
        _listeners.append(cb)


def set_theme(name: str, *, save: bool = True) -> str:
    """Switch theme ('dark'/'light'), persist, apply, notify listeners."""
    global _current_name
    n = "light" if str(name).lower() == "light" else "dark"
    _current_name = n
    if save:
        try:
            QSettings("PhotoEditor2", "PhotoEditor2").setValue("theme", n)
        except Exception:
            pass
    apply_theme()
    for cb in list(_listeners):
        try:
            cb()
        except Exception:
            pass
    return n


def toggle_theme(*, save: bool = True) -> str:
    return set_theme("light" if _current_name == "dark" else "dark", save=save)


def apply_theme(app_or_widget=None) -> None:
    """Apply current theme stylesheet at application level (or given widget)."""
    ss = build_stylesheet(current_theme())
    app = app_or_widget if isinstance(app_or_widget, QApplication) else QApplication.instance()
    if app is not None:
        app.setStyleSheet(ss)
    elif app_or_widget is not None:
        app_or_widget.setStyleSheet(ss)


def init_theme() -> str:
    """Load saved theme from QSettings without forcing a save."""
    global _current_name
    try:
        saved = QSettings("PhotoEditor2", "PhotoEditor2").value("theme", "dark")
    except Exception:
        saved = "dark"
    _current_name = "light" if str(saved).lower() == "light" else "dark"
    return _current_name


# ==========================================================
# STYLESHEET
# ==========================================================

def build_stylesheet(theme: dict) -> str:
    t = theme
    return f"""
    /* === GLOBAL === */
    QWidget {{
        background-color: {t["bg_primary"]};
        color: {t["text_primary"]};
        font-family: 'Segoe UI', 'SF Pro Display', 'Inter', 'Helvetica Neue', 'Noto Sans', Arial, sans-serif;
        font-size: 14px;
        font-weight: 400;
        selection-background-color: {t["accent"]};
        selection-color: white;
    }}
    QWidget:disabled {{
        color: {t["text_muted"]};
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
        background: transparent;
    }}
    QMenuBar::item:selected {{
        background: {t["accent_subtle"]};
        color: {t["accent"]};
    }}
    QMenuBar::item:pressed {{
        background: {t["accent"]};
        color: white;
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
        font-weight: 400;
        background: transparent;
    }}
    QMenu::item:selected {{
        background: {t["accent_subtle"]};
        color: {t["accent"]};
    }}
    QMenu::item:disabled {{
        color: {t["text_muted"]};
    }}
    QMenu::separator {{
        height: 1px;
        background: {t["border"]};
        margin: 4px 10px;
    }}
    QMenu::icon {{
        width: 16px;
        height: 16px;
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
        border: 1px solid transparent;
        padding: 6px 8px;
        font-size: 13px;
        font-weight: 500;
        border-radius: 6px;
    }}
    QToolButton:hover {{
        background: {t["button_hover"]};
        color: {t["text_primary"]};
    }}
    QToolButton:pressed {{
        background: {t["accent_pressed"]};
        color: white;
    }}
    QToolButton:checked {{
        background: {t["accent_subtle"]};
        color: {t["accent"]};
        border: 1px solid {t["accent"]};
    }}
    QToolButton:disabled {{
        color: {t["text_muted"]};
    }}
    QToolBar::separator {{
        background: {t["border"]};
        width: 1px;
        margin: 6px 4px;
    }}

    /* === STATUS BAR === */
    QStatusBar {{
        background: {t["bg_secondary"]};
        color: {t["text_secondary"]};
        border-top: 1px solid {t["border"]};
        padding: 3px 10px;
        font-size: 12px;
        font-weight: 400;
    }}
    QStatusBar QLabel {{
        color: {t["text_secondary"]};
        padding: 0 8px;
        font-size: 12px;
        font-weight: 400;
    }}

    /* === SCROLL AREA / SCROLLBARS (both axes) === */
    QScrollArea {{
        border: none;
        background: {t["bg_secondary"]};
    }}
    QScrollBar:vertical {{
        background: {t["scrollbar_bg"]};
        width: 10px;
        border-radius: 5px;
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
    QScrollBar:horizontal {{
        background: {t["scrollbar_bg"]};
        height: 10px;
        border-radius: 5px;
        margin: 2px;
    }}
    QScrollBar::handle:horizontal {{
        background: {t["scrollbar_handle"]};
        min-width: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {t["accent"]};
    }}
    QScrollBar::add-line, QScrollBar::sub-line {{
        width: 0px;
        height: 0px;
        background: none;
        border: none;
    }}
    QScrollBar::add-page, QScrollBar::sub-page {{
        background: none;
    }}
    QScrollBar::corner {{
        background: transparent;
    }}

    /* === GROUP BOX === */
    QGroupBox {{
        background: {t["group_bg"]};
        border: 1px solid {t["border"]};
        border-radius: 10px;
        margin-top: 12px;
        padding: 18px 10px 10px 10px;
        font-weight: 600;
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
    QSlider::handle:horizontal:focus {{
        border: 2px solid {t["text_primary"]};
    }}
    QSlider::sub-page:horizontal {{
        background: {t["accent"]};
        border-radius: 2px;
    }}
    QSlider::add-page:horizontal {{
        background: {t["slider_groove"]};
        border-radius: 2px;
    }}
    QSlider:disabled {{
        background: {t["bg_tertiary"]};
    }}

    /* === BUTTONS === */
    QPushButton {{
        background: {t["button_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["border"]};
        padding: 7px 14px;
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
    QPushButton:disabled {{
        background: {t["bg_tertiary"]};
        color: {t["text_muted"]};
        border-color: {t["border"]};
    }}
    QPushButton:default {{
        background: {t["accent"]};
        color: white;
        border: none;
    }}
    QPushButton:default:hover {{
        background: {t["accent_hover"]};
    }}
    QPushButton:default:pressed {{
        background: {t["accent_pressed"]};
    }}
    QPushButton[accent="success"] {{
        background: {t["success"]};
        color: white;
        font-weight: 700;
        border: none;
    }}
    QPushButton[accent="success"]:hover {{
        background: {t["success_hover"]};
    }}
    QPushButton[accent="success"]:pressed {{
        background: {t["success"]};
    }}
    QPushButton[compact="true"] {{
        padding: 5px 8px;
        font-size: 12px;
    }}

    /* === INPUT FIELDS === */
    QLineEdit {{
        background: {t["input_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["input_border"]};
        padding: 7px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 400;
    }}
    QLineEdit:focus {{
        border: 1px solid {t["accent"]};
        background: {t["bg_tertiary"]};
    }}
    QLineEdit:disabled {{
        background: {t["bg_tertiary"]};
        color: {t["text_muted"]};
    }}
    QLineEdit[clearButton="true"] {{
        padding-right: 24px;
    }}
    QComboBox {{
        background: {t["input_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["input_border"]};
        padding: 7px 28px 7px 12px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 400;
    }}
    QComboBox:hover {{
        border-color: {t["border_light"]};
    }}
    QComboBox:focus {{
        border: 1px solid {t["accent"]};
    }}
    QComboBox:disabled {{
        background: {t["bg_tertiary"]};
        color: {t["text_muted"]};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
        background: transparent;
    }}
    QComboBox::down-arrow {{
        image: url({_icon("chevron-down")});
        width: 12px;
        height: 12px;
    }}
    QComboBox::down-arrow:on {{
        image: url({_icon("chevron-up")});
    }}
    QComboBox QAbstractItemView {{
        background: {t["bg_secondary"]};
        color: {t["text_primary"]};
        border: 1px solid {t["border"]};
        border-radius: 8px;
        padding: 4px;
        selection-background-color: {t["accent_subtle"]};
        selection-color: {t["accent"]};
        outline: none;
    }}
    QSpinBox, QDoubleSpinBox {{
        background: {t["input_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["input_border"]};
        padding: 6px 28px 6px 10px;
        border-radius: 8px;
        font-size: 13px;
    }}
    QSpinBox:hover, QDoubleSpinBox:hover {{
        border-color: {t["border_light"]};
    }}
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border: 1px solid {t["accent"]};
    }}
    QSpinBox:disabled, QDoubleSpinBox:disabled {{
        background: {t["bg_tertiary"]};
        color: {t["text_muted"]};
    }}
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 22px;
        border-left: 1px solid {t["input_border"]};
        border-top-right-radius: 8px;
        background: transparent;
    }}
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        subcontrol-origin: padding;
        subcontrol-position: bottom right;
        width: 22px;
        border-left: 1px solid {t["input_border"]};
        border-bottom-right-radius: 8px;
        background: transparent;
    }}
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background: {t["button_hover"]};
    }}
    QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
        image: url({_icon("chevron-up")});
        width: 11px;
        height: 11px;
    }}
    QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
        image: url({_icon("chevron-down")});
        width: 11px;
        height: 11px;
    }}
    QTextEdit, QPlainTextEdit, QTextBrowser {{
        background: {t["input_bg"]};
        color: {t["text_primary"]};
        border: 1px solid {t["input_border"]};
        border-radius: 8px;
        padding: 8px 10px;
        font-size: 13px;
        selection-background-color: {t["accent"]};
        selection-color: white;
    }}
    QTextEdit:focus, QPlainTextEdit:focus {{
        border: 1px solid {t["accent"]};
    }}

    /* === LABELS === */
    QLabel {{
        color: {t["text_primary"]};
        font-size: 13px;
        font-weight: 400;
        background: transparent;
    }}
    QLabel:disabled {{
        color: {t["text_muted"]};
    }}
    QLabel#histHeader {{
        color: {t["accent"]};
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        padding: 6px 8px;
        background: {t["bg_secondary"]};
        border-bottom: 1px solid {t["border"]};
    }}

    /* === TABLE === */
    QTableWidget, QTableView, QTreeView, QListView {{
        background: {t["bg_secondary"]};
        color: {t["text_primary"]};
        border: 1px solid {t["border"]};
        gridline-color: {t["border"]};
        border-radius: 8px;
        alternate-background-color: {t["bg_tertiary"]};
    }}
    QTableWidget::item:selected, QTableView::item:selected,
    QTreeView::item:selected, QListView::item:selected {{
        background: {t["accent_subtle"]};
        color: {t["accent"]};
    }}
    QHeaderView::section {{
        background: {t["bg_tertiary"]};
        color: {t["text_primary"]};
        border: none;
        border-bottom: 1px solid {t["border"]};
        padding: 8px 12px;
        font-weight: 600;
        font-size: 12px;
    }}

    /* === DIALOGS === */
    QDialog {{
        background: {t["bg_primary"]};
        color: {t["text_primary"]};
    }}
    QDialogButtonBox {{
        spacing: 8px;
    }}
    QDialogButtonBox QPushButton {{
        min-width: 84px;
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
        min-height: 6px;
        max-height: 6px;
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
        background: {t["accent_subtle"]};
        color: {t["accent"]};
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
    QCheckBox:disabled {{
        color: {t["text_muted"]};
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {t["border_light"]};
        border-radius: 4px;
        background: {t["input_bg"]};
    }}
    QCheckBox::indicator:hover {{
        border-color: {t["accent"]};
    }}
    QCheckBox::indicator:checked {{
        background: {t["accent"]};
        border-color: {t["accent"]};
        image: url({_icon("check")});
    }}
    QCheckBox::indicator:checked:hover {{
        background: {t["accent_hover"]};
        border-color: {t["accent_hover"]};
    }}
    QCheckBox::indicator:disabled {{
        background: {t["bg_tertiary"]};
        border-color: {t["border"]};
    }}

    /* === RADIO BUTTON === */
    QRadioButton {{
        spacing: 8px;
        font-size: 13px;
    }}
    QRadioButton::indicator {{
        width: 18px;
        height: 18px;
        border: 2px solid {t["border_light"]};
        border-radius: 11px;
        background: {t["input_bg"]};
    }}
    QRadioButton::indicator:hover {{
        border-color: {t["accent"]};
    }}
    QRadioButton::indicator:checked {{
        background: {t["accent"]};
        border: 5px solid {t["input_bg"]};
        image: url({_icon("radio-dot")});
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
        color: {t["accent"]};
    }}
    QDockWidget::close-button, QDockWidget::float-button {{
        background: transparent;
        border: none;
        padding: 2px;
    }}

    /* === FRAME === */
    QFrame[frameShape="4"] {{
        background: {t["border"]};
        max-height: 1px;
    }}

    /* === SEPARATOR (menu/tool) === */
    QSeparator {{
        background: {t["border"]};
        max-height: 1px;
    }}
    """
