#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== Photo Editor 2 - instalacja ==="

# Kopia binarnej
cp -r dist/Photo_Editor_2 /opt/photo-editor-2/ 2>/dev/null || {
    echo "Uwaga: kopiowanie do /opt/photo-editor-2..."
    sudo cp -r dist/Photo_Editor_2 /opt/photo-editor-2/
}

# Ikona
cp resources/icons/photo_editor_2.png /usr/share/icons/hicolor/256x256/apps/photo-editor-2.png 2>/dev/null || {
    echo "Uwaga: kopiowanie ikony..."
    sudo cp resources/icons/photo_editor_2.png /usr/share/icons/hicolor/256x256/apps/photo-editor-2.png
}

# Plik .desktop
cp Photo_Editor_2.desktop /usr/share/applications/photo-editor-2.desktop

echo "=== Instalacja zakończona ==="
