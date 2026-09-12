#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=== Photo Editor 2 - Automatyczne tworzenie release'u v0.2.6 ==="
echo ""

# Krok 1: Aktualizacja wersji
echo ">>> Krok 1: Aktualizacja wersji..."
echo "0.2.6" > version.txt
cat version.txt
echo ""

# Krok 2: Budowanie AppImage
echo ">>> Krok 2: Budowanie AppImage..."
bash build_appimage.sh
echo ""

# Krok 3: Budowanie .deb
echo ">>> Krok 3: Budowanie pakietu .deb..."
bash build_deb.sh
echo ""

# Krok 4: Budowanie wersji zaawansowanej (opcjonalne)
# echo ">>> Krok 4: Budowanie wersji advanced..."
# pyinstaller --noconfirm --windowed --clean --name Photo_Editor_2_Advanced main_advanced.py
# echo ""

echo ">>> Wszystkie pliki instalacyjne zostały wygenerowane w katalogach:"
echo "   - dist/Photo_Editor_2-v0.2.6-x86_64.AppImage"
echo "   - packaging/debian/photo-editor-2_0.2.6_amd64.deb"
echo ""

# Krok 5: Instrukcja dla GitHub Release
echo "=== NASTĘPNY KROK: Utworzenie release na GitHub ==="
echo "1. Wejdź na: https://github.com/tomekkrow-sys/Photo_Editor_2/releases/new"
echo "2. Tag version: v0.2.6"
echo "3. Release title: Photo Editor 2 v0.2.6"
echo "4. Dodaj opis:"
echo "   Photo Editor 2 v0.2.6 - improved update manager"
echo ""
echo "5. Prześlij pliki:"
echo "   - dist/Photo_Editor_2-v0.2.6-x86_64.AppImage"
echo "   - packaging/debian/photo-editor-2_0.2.6_amd64.deb"
echo "   - (opcjonalnie: pliki Windows/macOS)"
echo ""
echo "=== AUTOMATYCZNE WYKONYWANIE ZAKOŃCZONE ==="