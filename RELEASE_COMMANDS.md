# Komendy do tworzenia release'u v2.0.1 dla Photo Editor 2

## Wymagania:
- Dostęp do repozytorium https://github.com/tomekkrow-sys/Photo_Editor_2  
- Prawa do tworzenia release'ów
- Przesłane pliki instalacyjne (pakietów .tar.gz, .zip)

## Komendy do wykonania:

1. **Sprawdzenie statusu repozytorium:**
```bash
cd /workspace/Photo_Editor_2
git add .
git commit -m "Update to v2.0.1 with integrated update manager"
git push origin main
```

2. **Stworzenie release'u (przygotowanie):**
```bash
# Pobierz aktualne wersje plików instalacyjnych do odpowiednich nazw
cp photo-editor-2-update-manager-release-v2.0.1.tar.gz release_assets/photo-editor-2-linux-x86_64.tar.gz
echo "2.0.1" > release_assets/version.txt
```

3. **Przygotowanie dokumentacji do release'u:**
```bash
# Stwórz plik z opisem release'u
cat > release_notes_v2.0.1.md << EOF
# Photo Editor 2 v2.0.1 Release Notes

## Features
- Added integrated Update Manager functionality
- Implemented "Check for Updates" and "Update Now" options in menu
- Fixed all previous update manager bugs and issues
- Improved version comparison logic with support for SEMVER format
- Automatic platform detection and downloading of appropriate assets
- Enhanced error handling and logging

## Changes
- Complete rewrite of update manager logic
- Added UI integration methods (check_updates(), update_now())
- Updated configuration schema to support GitHub API settings
- Improved robustness of asset download process

## Installation
For detailed installation instructions, see README.md file.
EOF
```

4. **Komenda do testowania poprawności konfiguracji:**
```bash
# Test aktualizacji z wersji v2.0.1
python3 update_manager_with_ui.py
```

5. **Komendy do uploadu plików (jeśli używamy GitHub CLI):**
```bash
# Jeśli masz zainstalowanygh cli:
gh release create v2.0.1 \
  release_assets/photo-editor-2-linux-x86_64.tar.gz \
  release_assets/photo-editor-2-windows-x64.zip \
  release_assets/photo-editor-2-macOS-x64.zip \
  --title "Photo Editor 2 v2.0.1" \
  --notes "Release of Photo Editor 2 version 2.0.1 with integrated update manager.

Features:
- Added integrated Update Manager functionality
- Implemented 'Check for Updates' and 'Update Now' options in menu
- Fixed all previous update manager bugs and issues
- Improved version comparison logic with support for SEMVER format
- Automatic platform detection and downloading of appropriate assets"
```

## Instrukcje manualne:

Jeśli nie masz GitHub CLI, przejdź ręcznie do:
https://github.com/tomekkrow-sys/Photo_Editor_2/releases/new

1. Wpisz tag: `v2.0.1`
2. Wpisz tytuł: `Photo Editor 2 v2.0.1`  
3. Dodaj opis z punktami:
   - Added integrated Update Manager functionality
   - Implemented "Check for Updates" and "Update Now" options in menu
   - Fixed all previous update manager bugs and issues
4. Prześlij pliki:
   - `photo-editor-2-linux-x86_64.tar.gz`
   - `photo-editor-2-windows-x64.zip` 
   - `photo-editor-2-macOS-x64.zip`

## Testowanie:

Po utworzeniu release'u, uruchom test:
```bash
# W terminalu
from update_manager_with_ui import check_updates
result = check_updates()
print(result)
```