#!/usr/bin/env python3
"""
Photo Editor 2.0

Main entry point.
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
import traceback
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QMessageBox
from core.database.catalog_database import CatalogDatabase
from core.catalog.catalog import Catalog

from config.version import (
    APP_NAME,
    APP_VERSION,
)

from ui.main_window import MainWindow
from core.crash_handler import install_exception_handler


# ==========================================================
# DIRECTORIES
# ==========================================================

ROOT_DIR = Path(__file__).resolve().parent


def _writable_dir(primary: Path, fallback_name: str) -> Path:
    """Return a writable directory (falls back to user data dir)."""

    try:
        primary.mkdir(parents=True, exist_ok=True)
        probe = primary / ".write_test"
        probe.touch()
        probe.unlink()
        return primary
    except OSError:
        fallback = (
            Path.home() / ".local" / "share" / "Photo_Editor_2" / fallback_name
        )
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


LOG_DIR = _writable_dir(ROOT_DIR / "logs", "logs")

LOG_FILE = LOG_DIR / "photo_editor.log"
UPDATE_LOG = LOG_DIR / "update.log"


# ==========================================================
# LOGGING
# ==========================================================

def configure_logging() -> None:
    """
    Configure application logging.
    """

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        encoding="utf-8",
    )

    logging.info("=" * 60)
    logging.info("Starting %s", APP_NAME)
    logging.info("Version %s", APP_VERSION)


def _ulog(msg: str) -> None:
    """Write to update.log AND app log."""
    logging.info(msg)
    try:
        with open(UPDATE_LOG, "a", encoding="utf-8") as f:
            from datetime import datetime
            f.write(f"{datetime.now().isoformat()} | {msg}\n")
    except Exception:
        pass


# ==========================================================
# EXCEPTION HANDLER
# ==========================================================

def exception_hook(exc_type, exc_value, exc_traceback):

    logging.exception(
        "Unhandled exception",
        exc_info=(exc_type, exc_value, exc_traceback),
    )

    QMessageBox.critical(
        None,
        APP_NAME,
        str(exc_value),
    )


# ==========================================================
# MAIN
# ==========================================================

def main() -> int:

    configure_logging()

    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    data_dir = _writable_dir(ROOT_DIR / "data", "data")

    database = CatalogDatabase(
        data_dir / "catalog.db"
    )
    database.initialize()

    catalog = Catalog(database)

    app = QApplication(sys.argv)

    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    install_exception_handler(APP_VERSION)

    window = MainWindow(catalog)

    window.show()

    # --- Auto-update check in background ---
    try:
        from PySide6.QtCore import QThread, Signal as QSignal

        class _UpdateChecker(QThread):
            result = QSignal(str, str)  # (current_version, latest_version) or ("","") 

            def run(self):
                try:
                    _ulog("Checking for updates...")
                    import urllib.request
                    import json
                    from config.version import APP_VERSION as _cur
                    from pathlib import Path as _P
                    cfg_path = _P(__file__).resolve().parent / "config" / "updater_config.json"
                    if cfg_path.exists():
                        cfg = json.loads(cfg_path.read_text())
                    else:
                        cfg = {}
                    gh = cfg.get("github", {})
                    url = f"{gh.get('api_url', 'https://api.github.com')}/repos/{gh.get('owner', 'tomekkrow-sys')}/{gh.get('repo', 'Photo_Editor_2')}/releases/latest"
                    req = urllib.request.Request(url, headers={"User-Agent": "Photo-Editor-2"})
                    resp = urllib.request.urlopen(req, timeout=10)
                    data = json.loads(resp.read().decode())
                    latest = data.get("tag_name", "").lstrip("v")
                    current = _cur
                    _ulog(f"Current: v{current}, Latest: v{latest}")
                    cur_parts = [int(x) for x in current.split(".")]
                    lat_parts = [int(x) for x in latest.split(".")]
                    newer = False
                    for i in range(min(len(cur_parts), len(lat_parts))):
                        if lat_parts[i] > cur_parts[i]:
                            newer = True
                            break
                        elif lat_parts[i] < cur_parts[i]:
                            break
                    if newer:
                        _ulog(f"New version available: v{latest}")
                        self.result.emit(current, latest)
                    else:
                        _ulog("Already up to date")
                        self.result.emit("", "")
                except Exception as e:
                    _ulog(f"Update check FAILED: {e}")
                    self.result.emit("", "")

        class _UpdateDownloader(QThread):
            log_line = QSignal(str)
            done = QSignal(str, str)  # (status, message)

            def __init__(self, ver: str, parent=None):
                super().__init__(parent)
                self._ver = ver

            def run(self):
                import platform
                import urllib.request
                import tempfile
                import subprocess

                ver = self._ver
                system = platform.system().lower()
                self.log_line.emit(f"System: {system}")

                assets = {
                    "linux": f"photo-editor-2_{ver}_amd64.deb",
                    "darwin": f"Photo_Editor_2-macos-v{ver}.zip",
                    "windows": f"Photo_Editor_2-windows-v{ver}.zip",
                }
                filename = assets.get(system, assets["linux"])
                download_url = f"https://github.com/tomekkrow-sys/Photo_Editor_2/releases/download/v{ver}/{filename}"
                self.log_line.emit(f"URL: {download_url}")

                try:
                    # Step 1: Download
                    tmp_dir = tempfile.mkdtemp(prefix="photo_editor_update_")
                    download_path = os.path.join(tmp_dir, filename)
                    self.log_line.emit(f"Downloading to: {download_path}")
                    _ulog(f"Downloading {download_url}")
                    urllib.request.urlretrieve(download_url, download_path)
                    size = os.path.getsize(download_path)
                    self.log_line.emit(f"Downloaded: {size} bytes")
                    _ulog(f"Downloaded: {download_path} ({size} bytes)")

                    if system != "linux":
                        self.done.emit("ok", f"Pobrano: {download_path}")
                        return

                    # Step 2: Copy to ~/Downloads
                    downloads = os.path.expanduser("~/Downloads")
                    os.makedirs(downloads, exist_ok=True)
                    dest = os.path.join(downloads, filename)
                    shutil.copy2(download_path, dest)
                    self.log_line.emit(f"Copied to: {dest}")
                    _ulog(f"Copied to: {dest}")

                    # Step 3: Install
                    self.log_line.emit("Installing with pkexec...")
                    _ulog("Attempting pkexec dpkg -i")
                    installed = False
                    try:
                        ret = subprocess.run(
                            ["pkexec", "dpkg", "-i", dest],
                            timeout=120
                        )
                        self.log_line.emit(f"pkexec returned: {ret.returncode}")
                        _ulog(f"pkexec returned: {ret.returncode}")
                        if ret.returncode == 0:
                            installed = True
                            self.log_line.emit("Install SUCCESS via pkexec")
                            _ulog("Install SUCCESS via pkexec")
                        else:
                            self.log_line.emit(f"pkexec failed (rc={ret.returncode}), trying terminal...")
                            _ulog(f"pkexec failed rc={ret.returncode}")
                    except FileNotFoundError:
                        self.log_line.emit("pkexec not found on system")
                        _ulog("pkexec not found")
                    except subprocess.TimeoutExpired:
                        self.log_line.emit("pkexec timed out (120s)")
                        _ulog("pkexec timed out")
                    except Exception as e:
                        self.log_line.emit(f"pkexec error: {e}")
                        _ulog(f"pkexec error: {e}")

                    # Step 4: Terminal fallback
                    if not installed:
                        self.log_line.emit("Trying terminal fallback...")
                        _ulog("Trying terminal fallback")
                        script_path = os.path.join(tmp_dir, "install.sh")
                        with open(script_path, "w") as f:
                            f.write(f"#!/bin/bash\n")
                            f.write(f"echo '=== Photo Editor 2 - Aktualizacja ==='\n")
                            f.write(f"sudo dpkg -i \"{dest}\"\n")
                            f.write(f"RC=$?\n")
                            f.write(f"if [ $RC -ne 0 ]; then\n")
                            f.write(f"  echo 'Naprawa zaleznosci...'\n")
                            f.write(f"  sudo apt-get install -f -y\n")
                            f.write(f"fi\n")
                            f.write(f"echo ''\n")
                            f.write(f"echo 'Gotowe! Zamknij i uruchom program ponownie.'\n")
                            f.write(f"read -p 'Enter aby zamknac...'\n")
                        os.chmod(script_path, 0o755)

                        # Clean LD_LIBRARY_PATH so system terminal works
                        env = os.environ.copy()
                        env.pop("LD_LIBRARY_PATH", None)
                        env.pop("PYTHONPATH", None)

                        for term in [
                            ["konsole", "-e", "bash", script_path],
                            ["x-terminal-emulator", "-e", f"bash {script_path}"],
                            ["xterm", "-e", f"bash {script_path}"],
                            ["gnome-terminal", "--", "bash", script_path],
                            ["lxterminal", "-e", f"bash {script_path}"],
                        ]:
                            try:
                                self.log_line.emit(f"Trying: {term[0]}")
                                _ulog(f"Trying terminal: {term[0]}")
                                subprocess.Popen(term, start_new_session=True, env=env)
                                installed = True
                                self.log_line.emit(f"Opened: {term[0]}")
                                _ulog(f"Opened terminal: {term[0]}")
                                break
                            except FileNotFoundError:
                                self.log_line.emit(f"{term[0]} not found")
                                _ulog(f"{term[0]} not found")
                            except Exception as e:
                                self.log_line.emit(f"{term[0]} failed: {e}")
                                _ulog(f"{term[0]} failed: {e}")

                    if installed:
                        self.done.emit("ok",
                            f"Pobrano v{ver} do: {dest}\n\n"
                            f"Zainstalowano lub otwarto terminal.\n"
                            f"Po instalacji zamknij program i uruchom ponownie.")
                    else:
                        self.done.emit("manual",
                            f"Pobrano: {dest}\n\n"
                            f"Nie udalo sie zainstalowac automatycznie.\n\n"
                            f"Otworz terminal i wklej:\n\n"
                            f"sudo dpkg -i \"{dest}\"")
                except Exception as e:
                    tb = traceback.format_exc()
                    self.log_line.emit(f"FATAL: {e}")
                    _ulog(f"FATAL: {e}\n{tb}")
                    self.done.emit("error", f"Blad: {e}")

        def _on_update_result(cur, ver):
            if not ver:
                return
            from config.i18n import t

            ret = QMessageBox.information(
                window,
                t("check_updates"),
                f"Nowa wersja: v{ver}\nObecna: v{cur}\n\nPobrac i zainstalowac?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if ret != QMessageBox.StandardButton.Yes:
                return

            downloader = _UpdateDownloader(ver, window)

            from PySide6.QtWidgets import QProgressDialog
            from PySide6.QtCore import Qt as QQt

            progress = QProgressDialog("", "Anuluj", 0, 0, window)
            progress.setWindowTitle("Aktualizacja")
            progress.setWindowModality(QQt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.show()

            log_text = ["Przygotowywanie..."]

            def on_log(line):
                log_text.append(line)
                progress.setLabelText(line)
                if len(log_text) > 50:
                    log_text.pop(0)

            def on_done(status, message):
                progress.close()
                if status == "error":
                    # Show full log + error
                    full_log = "\n".join(log_text)
                    QMessageBox.warning(window, "Aktualizacja",
                        f"{message}\n\n--- Log ---\n{full_log}")
                elif status == "manual":
                    QMessageBox.information(window, "Aktualizacja", message)
                else:
                    QMessageBox.information(window, "Aktualizacja", message)

            downloader.log_line.connect(on_log)
            downloader.done.connect(on_done)
            downloader.start()

        _checker = _UpdateChecker()
        _checker.result.connect(_on_update_result)
        _checker.start()
    except Exception as e:
        logging.warning("Auto-update setup failed: %s", e)

    logging.info("Application started")

    return app.exec()


# ==========================================================
# START
# ==========================================================

if __name__ == "__main__":
    raise SystemExit(main())
