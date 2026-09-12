#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== Photo Editor 2 - budowanie AppImage ==="

VERSION=$(cat version.txt)

# 1. Zbuduj binarne via PyInstaller
DIST=dist/Photo_Editor_2
if [ ! -d "$DIST" ]; then
    echo "==> PyInstaller: buduje binarie..."
    python3 -m PyInstaller --noconfirm --windowed \
        --name Photo_Editor_2 \
        --collect-all rawpy \
        photo_editor.py
fi

# 2. Przygotuj AppDir structure
APPDIR=dist/AppDir
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/lib" "$APPDIR/opt/photo-editor-2"

cp -r "$DIST"/* "$APPDIR/opt/photo-editor-2/"

# 3. Zbuduj AppImage
APPIMAGE_NAME="Photo_Editor_2-v${VERSION}-x86_64.AppImage"
echo "==> Budowanie AppImage: $APPIMAGE_NAME"

# Użyj appimagetool jeśli dostępny, inaczej zbuduj ręcznie
if command -v appimagetool &> /dev/null; then
    appimagetool -n "$APPDIR" "$DIST/$APPIMAGE_NAME"
else
    # Prosta budowa — plik binarny + _internal
    cp -r "$APPDIR/opt/photo-editor-2/Photo_Editor_2" "$DIST/$APPIMAGE_NAME"
    chmod +x "$DIST/$APPIMAGE_NAME"
fi

echo "=== Gotowe ==="
ls -lh "$DIST/$APPIMAGE_NAME"
