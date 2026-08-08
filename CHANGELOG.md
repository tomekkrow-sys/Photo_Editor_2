# Changelog

Wszystkie istotne zmiany w projekcie Photo Editor 2.

Format oparty na [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/).

## [Unreleased]

### Dodane
- Filtr **Czarno-biały** (menu Filtry / pasek narzędzi): naturalne tony,
  łagodna krzywa S, podgląd i zapis jako nowy plik
- Filtry **Sepia**, **Negatyw**, **Winieta** (menu Filtry)
- **Auto-korekta** jednym kliknięciem (menu Obraz): balans bieli
  gray-world + rozciągnięcie kontrastu, z obsługą Cofnij
- **Zmień rozmiar** (menu Obraz): dialog z blokadą proporcji,
  z obsługą Cofnij

## [0.1.0] - 2026-08-08

### Dodane
- Filtr **Ołówek**: naturalne cieniowanie tonalne (kreski OpenCV + warstwa
  tonów), podgląd i zapis jako nowy plik (`*_olowek.png`)
- **Cofnij/Ponów** (Ctrl+Z / Ctrl+Shift+Z) dla kadrowania, obrotu i odbić
  — historia `EditHistory` z limitem kroków
- **Zapisz** (Ctrl+S, z potwierdzeniem nadpisania, RAW → Zapisz jako),
  **Zapisz jako** (Ctrl+Shift+S), **Nowy** (Ctrl+N), **Eksport** (Ctrl+E)
- Operacje schowka: **Kopiuj** (z nałożonymi korektami), **Wklej** jako
  nowy dokument, **Wytnij**, **Usuń** (bez ruszania pliku na dysku)
- `run.bat` — uruchamianie pod Windows
- Moduły: core/jobs, core/export, core/tools, core/render, core/image,
  ui/develop/panels
- Testy: 73 testy jednostkowe (filtry, historia, operacje MainWindow,
  schowek, pipeline)

### Naprawione
- Przywrócone klasy `ImageAdjustments` i `ImageHistory` usunięte
  przez refaktor modułów (psuły canvas i testy)
- Świeży klon z GitHuba nie startował — `.gitignore` blokował
  `ui/export_dialog.py` i `ui/batch_dialog.py`
- `pil_to_qpixmap`: obsługa trybów innych niż RGB (skala szarości,
  paleta) — błąd przy podglądzie filtra ołówka
- `AdjustmentSettings.copy()` było poza klasą
- `brush_tool`: `CompositionMode_Saturation` nie istnieje w Qt6
  (zastąpione Overlay)
- `export_manager`: poprawiona ścieżka importu po refaktorze
- `crash_handler`: pełne nazwy enumów Qt
- `spot_tool`: ochrona przed brakiem punktu źródłowego
- `metadata_panel`: `self.size` przykrywało metodę `QWidget.size()`
- `run.sh`: używa venv projektu i własnego katalogu
- Kadrowanie: skalowanie współrzędnych z podglądu do pełnej rozdzielczości

### Zmienione
- Reorganizacja architektury modułów (core/image, core/render, ui/export)
- Błędy zapisu/otwierania trafiają do `logs/photo_editor.log`
