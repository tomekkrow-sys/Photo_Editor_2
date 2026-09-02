# Changelog

Wszystkie istotne zmiany w projekcie Photo Editor 2.

Format oparty na [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/).

## [0.2.0] - 2026-08-28

### Dodane
- Workflow GitHub Actions budujący AppImage dla Linux
- Instalator `.deb` z gotowym pakietem (CI)
- Instalator Windows `.exe` (PyInstaller, CI)
- Instalator macOS `.app` (PyInstaller, CI)
- `run.bat` — uruchamianie pod Windows
- `run.sh` — uruchamianie pod Linux
- **Zaawansowany menedżer aktualizacji**:
  - Automatyczne sprawdzanie wersji z GitHub
  - Aktualizacje w tle bez restartu aplikacji
  - Możliwość automatycznego tworzenia nowych wersji

### Naprawione
- Python 3.13 w `.venv` działa na glibc systemie



## [Unreleased]

### Dodane
- Filtr **Czarno-biały** (menu Filtry / pasek narzędzi): naturalne tony,
  łagodna krzywa S, podgląd i zapis jako nowy plik
- Filtry **Sepia**, **Negatyw**, **Winieta** (menu Filtry)
- **Auto-korekta** jednym kliknięciem (menu Obraz): balans bieli
  gray-world + rozciągnięcie kontrastu, z obsługą Cofnij
- **Zmień rozmiar** (menu Obraz): dialog z blokadą proporcji,
  z obsługą Cofnij
- **Usuń obiekt** (Narzędzia / pasek): retusz punktowy (heal/clone),
  klik na element usuwa go z próbką z sąsiedniego obszaru,
  kółko myszy zmienia rozmiar pędzla, obsługa Cofnij
- `pil_to_qimage` / `qimage_to_pil` w core/pipeline
- **Cofnij/Ponów obejmuje suwaki korekty** — Ctrl+Z cofa edycje obrazu
  i zmiany korekt (sesje suwaka grupowane), nowsza akcja wygrywa
- **Pędzel korekt** (Narzędzia / pasek): lewy przycisk rozjaśnia,
  prawy przyciemnia, kółko myszy zmienia rozmiar; obsługa Cofnij
- **Informacje o zdjęciu** (menu Obraz): wymiary, rozmiar pliku
  i dane EXIF (aparat, obiektyw, ISO, czas, przysłona, ogniskowa, data)
- **Ostatnio otwierane** (menu Plik): 8 ostatnich zdjęć,
  zapamiętywane między uruchomieniami
- Filtr **Ramka** (menu Filtry): biała obwódka, podgląd i zapis
  jako nowy plik
- **Porównaj z plikiem** (menu Widok): bieżące zdjęcie obok innego
  z dysku z przeciąganą linią podziału
- **Nałóż warstwę z pliku** (menu Obraz): inne zdjęcie jako warstwa
  z suwakiem krycia i trybami mieszania (Normalny, Pomnóż, Naładka,
  Ekran), z obsługą Cofnij
- Workflow GitHub Actions budujący `Photo_Editor_2.exe` dla Windows
  (artefakt do pobrania po kazdym pushu)
- Pelne polskie etykiety przyciskow (Obroc w lewo/prawo,
  Odbij poziomo/pionowo, Przybliz, Oddal)
- **Wyprostuj horyzont** (menu Obraz): obrot o dowolny kat
  (-45°..+45°) z automatycznym przycieciem pustych naroznikow,
  z obsluga Cofnij
- **Znak wodny** (menu Obraz): tekst na zdjeciu z wyborem pozycji
  (5 miejsc), krycia i konturem dla czytelnosci, z obsluga Cofnij
- Pakiet **.deb dla Debiana** (`build_deb.sh`): instaluje do /opt,
  wpis w menu aplikacji, komenda `photo-editor-2`; CI buduje
  artefakt `Photo_Editor_2-debian`
- Ikona aplikacji (resources/icons/photo_editor_2.png)

### Naprawione
- Logi i katalog danych zapisuja sie w katalogu uzytkownika,
  gdy lokalizacja programu jest tylko-do-odczytu (instalacja /opt)
- Wczytywanie presetow wywalalo sie (brak `Adjustments.from_dict`)
- `pil_to_cv` crashowal na obrazach w trybach L/LA/P
- Histogram szarosci: przepełnienie uint8 (200 raportowane jako 29)
- core/canvas: identity-check przed kosztownym apply_settings
- Filtr **Ołówek**: przerobiony na naturalny — jasny papier, miekkie
  szare kreski (nigdy czarne), cienie podniesione i czytelne,
  wstepne wygladzenie tlumace ziarno zdjecia; parametry mozna stroic
  (shading, stroke_strength, lift)
- Ołówek v4: balans miedzy widoczna faktura kresek (tekstura OpenCV
  zlagodzona x0.65) a tonalnoscia (shading=0.35, lift=0.15)

### Usuniete
- Przestarzale testy starej architektury MainWindow (pokrycie zapewnia
  test_main_window_ops.py)

### Zmienione
- „Batch" przemianowany na **Konwerter folderu** (przycisk, okno,
  komunikaty)

### Naprawione
- Konwerter folderu: pliki RAW (.nef, .cr2, .arw...) były pomijane —
  teraz dekodowane przez rawpy jak przy normalnym otwieraniu,
  z uwzględnieniem orientacji EXIF
- spot_tool: błędna geometria prostokątów w `_stamp` (nic nie
  malowało) oraz czarna ramka przy stemplu (brak kanału alfa)

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
