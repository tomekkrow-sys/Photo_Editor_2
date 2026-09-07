# Komendy do utworzenia release'u Photo Editor 2 v2.0.1

## Ustaw wersję projektu
echo "2.0.1" > version.txt

## Sprawdź wersję
cat version.txt

## Test funkcjonalności update managera
python3 update_manager_with_ui.py

## Przygotuj pliki instalacyjne (jeśli potrzebne)
tar -czf photo-editor-2-linux-x86_64.tar.gz update_manager_with_ui.py config/ version.txt README.md

## Wyświetl aktualny stan projektu
ls -la

## Utwórz kopię bezpieczeństwa
cp update_manager_with_ui.py update_manager_with_ui_backup.py