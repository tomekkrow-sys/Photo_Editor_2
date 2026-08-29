#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== Photo Editor 2 - odinstalowanie ==="

# Usuń binarne
sudo rm -rf /opt/photo-editor-2

# Usuń ikonę
sudo rm -f /usr/share/icons/hicolor/256x256/apps/photo-editor-2.png

# Usuń .desktop
sudo rm -f /usr/share/applications/photo-editor-2.desktop

# Czyść sherek icon cache
sudo update-icon-caches /usr/share/icons/hicolor 2>/dev/null || true

echo "=== Odinstalowanie zakończone ==="
