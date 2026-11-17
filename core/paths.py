#!/usr/bin/env python3
"""Zapisywalne katalogi użytkownika (XDG).

Aplikacja zainstalowana w /opt nie jest zapisywalna dla zwykłego
użytkownika — dane użytkownika (presety, skróty itd.) trzymamy
w katalogach domowych.
"""
from __future__ import annotations

import os
from pathlib import Path

# Nazwa zgodna z istniejącymi katalogami logów (photo_editor.py).
_APP_DIR = "Photo_Editor_2"


def user_data_dir() -> Path:
    """Katalog danych użytkownika (presety, bufor itd.)."""
    xdg = os.environ.get("XDG_DATA_HOME", "")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    path = base / _APP_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def user_config_dir() -> Path:
    """Katalog konfiguracji użytkownika (skróty, ustawienia)."""
    xdg = os.environ.get("XDG_CONFIG_HOME", "")
    base = Path(xdg) if xdg else Path.home() / ".config"
    path = base / _APP_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path
