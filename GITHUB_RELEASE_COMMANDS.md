# Komendy do utworzenia release'u Photo Editor 2 v2.0.1

## Krok 1: Ustaw wersję projektu
```bash
echo "2.0.1" > version.txt
```

## Krok 2: Przygotuj pliki instalacyjne (jeśli nie masz już gotowych)
```bash
# Jeśli chcesz stworzyć pakiet z aktualnym kodem
tar -czf photo-editor-2-linux-x86_64.tar.gz update_manager_with_ui.py config/ version.txt README.md
```

## Krok 3: Sprawdź aktualny stan wersji
```bash
cat version.txt
```

## Krok 4: Test funkcjonalności (opcjonalne)
```bash
python3 update_manager_with_ui.py
```

## Krok 5: Gotowe do utworzenia release'u w GitHub

Przejdź do:
https://github.com/tomekkrow-sys/Photo_Editor_2/releases/new

Wpisz:
- **Tag version**: `v2.0.1`
- **Release title**: `Photo Editor 2 v2.0.1`
- Dodaj opis: 
```
Photo Editor 2 v2.0.1 - Integrated Update Manager

Features:
- Added "Check for Updates" functionality
- Added "Update Now" menu option  
- Fixed all previous update manager bugs
- Improved version comparison logic with SEMVER support
```

## Krok 6: Prześlij pliki instalacyjne (jeśli chcesz je mieć w release)
Prześlij:
1. `photo-editor-2-linux-x86_64.tar.gz` - Linux 64-bit package
2. `photo-editor-2-windows-x64.zip` - Windows 64-bit package (jeśli masz taki plik)
3. `photo-editor-2-macOS-x64.zip` - macOS 64-bit package (jeśli masz taki plik)

## Testowanie poprawności
Po utworzeniu release'u, możesz sprawdzić:
```bash
python3 update_manager_with_ui.py
```

Wynik powinien pokazywać: 
- Current version: 2.0.1
- Latest available: 2.0.1  
- Update available: False