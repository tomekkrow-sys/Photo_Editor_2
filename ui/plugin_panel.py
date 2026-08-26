#!/usr/bin/env python3
"""Photo Editor 2.0 — Plugin System."""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import Protocol, runtime_checkable

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import (
    QAction,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


@runtime_checkable
class Plugin(Protocol):
    """Plugin interface."""

    name: str
    description: str
    version: str

    def initialize(self, app) -> None:
        ...

    def enable(self) -> None:
        ...

    def disable(self) -> None:
        ...

    def terminate(self) -> None:
        ...

    def get_menu_actions(self) -> list[tuple[str, QAction]]:
        ...

    def get_tool_actions(self) -> list[tuple[str, QAction]]:
        ...


class PluginManager(QObject):
    """Plugin manager."""

    plugin_loaded = Signal(str)
    plugin_unloaded = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._plugins: dict[str, Plugin] = {}
        self._plugin_paths: list[Path] = []

    def discover_plugins(self, paths: list[Path] | None = None) -> list[Path]:
        paths = paths or self._plugin_paths
        plugins = []
        for plugin_path in paths:
            if plugin_path.is_file() and plugin_path.suffix == ".py":
                plugins.append(plugin_path)
            elif plugin_path.is_dir():
                plugins.extend(plugin_path.glob("*.py"))
        return plugins

    def load_plugin(self, path: Path) -> object | None:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(path.stem, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"Failed to load plugin {path}: {e}")
            return None

    def enable_plugin(self, module: object) -> bool:
        if hasattr(module, "enable"):
            try:
                module.enable()
                return True
            except Exception as e:
                print(f"Failed to enable plugin: {e}")
                return False
        return True

    def disable_plugin(self, module: object) -> bool:
        if hasattr(module, "disable"):
            try:
                module.disable()
                return True
            except Exception as e:
                print(f"Failed to disable plugin: {e}")
                return False
        return True


class PluginPanel(QWidget):
    """Plugin manager panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._plugin_manager = PluginManager()
        self._plugins: dict[str, object] = {}
        self._load_default_plugins()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plugin_list = QListWidget()
        layout.addWidget(self._plugin_list)

        button_layout = QHBoxLayout()
        self._load_btn = QPushButton("Wczytaj")
        self._load_btn.clicked.connect(self._on_load_plugin)
        button_layout.addWidget(self._load_btn)

        self._unload_btn = QPushButton("Odczytaj")
        self._unload_btn.clicked.connect(self._on_unload_plugin)
        button_layout.addWidget(self._unload_btn)

        self._enable_btn = QPushButton("Włącz")
        self._enable_btn.clicked.connect(self._on_enable_plugin)
        button_layout.addWidget(self._enable_btn)

        self._disable_btn = QPushButton("Wyłącz")
        self._disable_btn.clicked.connect(self._on_disable_plugin)
        button_layout.addWidget(self._disable_btn)

        layout.addLayout(button_layout)

        self._refresh_list()

    def _load_default_plugins(self) -> None:
        pass

    def _refresh_list(self) -> None:
        self._plugin_list.clear()
        for path, module in self._plugins.items():
            item_text = f"{path.stem} {'(włączony)' if path.stem in [m.stem for m in self._plugins.values() if hasattr(m, 'enabled') and m.enabled] else ''}"
            self._plugin_list.addItem(item_text)

    def _on_load_plugin(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Wczytaj wtyczkę", "", "Python files (*.py)"
        )
        if path:
            module = self._plugin_manager.load_plugin(Path(path))
            if module:
                self._plugins[Path(path)] = module
                if self._plugin_manager.enable_plugin(module):
                    module.enabled = True
                self._refresh_list()

    def _on_unload_plugin(self) -> None:
        current = self._plugin_list.currentItem()
        if current:
            path = Path(current.text().split()[0])
            module = self._plugins.get(path)
            if module:
                self._plugin_manager.disable_plugin(module)
                module.enabled = False
                self._refresh_list()

    def _on_enable_plugin(self) -> None:
        current = self._plugin_list.currentItem()
        if current:
            path = Path(current.text().split()[0])
            module = self._plugins.get(path)
            if module:
                self._plugin_manager.enable_plugin(module)
                module.enabled = True
                self._refresh_list()

    def _on_disable_plugin(self) -> None:
        current = self._plugin_list.currentItem()
        if current:
            path = Path(current.text().split()[0])
            module = self._plugins.get(path)
            if module:
                self._plugin_manager.disable_plugin(module)
                module.enabled = False
                self._refresh_list()


def enable():
    """Enable plugin."""
    pass


def disable():
    """Disable plugin."""
    pass
