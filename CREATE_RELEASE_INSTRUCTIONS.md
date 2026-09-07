# Instrukcje tworzenia Release'u v2.0.1 dla Photo Editor 2

## Wymagania wstępne:
- Kontroler wersji (np. git) z lokalnym repozytorium
- Zaktualizowane pliki: version.txt musi zawierać "2.0.1"
- Gotowe pliki instalacyjne dla różnych platform 

## Krok 1: Ustaw wersję
```bash
echo "2.0.1" > version.txt
```

## Krok 2: Zatwierdź zmiany
```bash
git add .
git commit -m "Update to v2.0.1 with integrated update manager"
git push origin main
```

## Krok 3: Utwórz Release w GitHub

1. Przejdź do repozytorium: https://github.com/tomekkrow-sys/Photo_Editor_2
2. Kliknij "Releases" w lewej kolumnie
3. Kliknij "Draft a new release"
4. Uzupełnij pola:
   - **Tag version**: `v2.0.1`
   - **Release title**: `Photo Editor 2 v2.0.1`
   - **Description**: 
     ```
     Release of Photo Editor 2 version 2.0.1 with integrated update manager.
     
     Changes:
     - Added integrated Update Manager functionality
     - Implemented "Check for Updates" and "Update Now" options
     - Fixed all previous update manager bugs
     ```
5. Dodaj pliki instalacyjne jako assets:
   - `photo-editor-2-linux-x86_64.tar.gz`
   - `photo-editor-2-windows-x64.zip`
   - `photo-editor-2-macOS-x64.zip`

## Krok 4: Sprawdź działanie aktualizacji
Po utworzeniu release'u, menedżer aktualizacji powinien:

1. Odczytać wersję z `version.txt` (2.0.1)
2. Pobrać listę release'ów z GitHub (`v2.0.1`)
3. Porównać wersje 
4. Jeśli nowsza wersja dostępna, pobrać odpowiedni plik do aktualizacji

## Krok 5: Testowanie
W terminalu:
```bash
python3 update_manager_with_ui.py
```
Lub z aplikacji:
```python
from update_manager_with_ui import check_updates
result = check_updates()
print(result)
```

## Uwagi końcowe:
- Pliki instalacyjne muszą być zgodne z nazwami wykrywanymi przez menedżer
- Release musi zawierać assety dla każdej platformy (Linux, Windows, macOS)
- System automatycznie wykryje platformę i pobierze odpowiedni plik

Utworzony release `v2.0.1` zapewni użytkownikom funkcjonalność aktualizacji w aplikacji.