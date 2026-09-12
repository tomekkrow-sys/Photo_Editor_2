#!/bin/bash
set -e
cd "$(dirname "$0")"

echo "=== Photo Editor 2 - budowanie pakietu .deb ==="

VERSION=$(cat version.txt)
PKG=packaging/debian
DIST=dist/Photo_Editor_2

# 1. PyInstaller (jednorazowo: pip install pyinstaller)
if [ ! -d "$DIST" ]; then
    echo "==> PyInstaller: buduje binarie..."
    python3 -m PyInstaller --noconfirm --windowed \
        --name Photo_Editor_2 \
        --collect-all rawpy \
        photo_editor.py
fi

# 2. Struktura pakietu
echo "==> Skladam strukture pakietu..."
rm -rf "$PKG/opt" "$PKG/usr"
mkdir -p "$PKG/opt/photo-editor-2" "$PKG/usr/bin" \
         "$PKG/usr/share/applications" "$PKG/usr/share/icons/hicolor/256x256/apps"

cp -r "$DIST"/* "$PKG/opt/photo-editor-2/"
cp resources/icons/photo_editor_2.png \
   "$PKG/usr/share/icons/hicolor/256x256/apps/photo-editor-2.png"

cat > "$PKG/usr/bin/photo-editor-2" << 'EOF'
#!/bin/bash
cd /opt/photo-editor-2 && exec ./Photo_Editor_2 "$@"
EOF
chmod 755 "$PKG/usr/bin/photo-editor-2"

cat > "$PKG/usr/share/applications/photo-editor-2.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Photo Editor 2
Comment=Edytor zdjec z obsluga RAW
Exec=/usr/bin/photo-editor-2
Icon=photo-editor-2
Terminal=false
Categories=Graphics;Photography;
EOF

# 3. Wersja w control
sed -i "s/^Version:.*/Version: $VERSION/" "$PKG/DEBIAN/control"

# 4. Budowa .deb
echo "==> dpkg-deb..."
dpkg-deb --root-owner-group --build "$PKG" "photo-editor-2_${VERSION}_amd64.deb"

echo ""
echo "=== GOTOWE: photo-editor-2_${VERSION}_amd64.deb ==="
echo "Instalacja: sudo dpkg -i photo-editor-2_${VERSION}_amd64.deb"
echo "Uruchomienie: photo-editor-2  (albo z menu aplikacji)"
