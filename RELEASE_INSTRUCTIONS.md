# Instrukcje ustawienia release w repozytorium GitHub

## 1. Przygotowanie release

Aby menedżer aktualizacji mógł działać poprawnie, należy utworzyć release w repozytorium:

1. Przejdź do strony repozytorium: https://github.com/tomekkrow-sys/Photo_Editor_2
2. Kliknij "Releases" w lewej kolumnie
3. Kliknij "Draft a new release"
4. Wpisz tag: `v1.0.1` (zgodny z plikiem version.txt)
5. Nazwij release: `Version 1.0.1`
6. Opis release'u: 
   ```
   Release of Photo Editor 2 version 1.0.1
   ```

## 2. Dodanie artefaktów

Do release trzeba dodać odpowiednie pliki, które będą pobierane przez menedżer aktualizacji:

### Linux (x86_64)
- Plik: `photo-editor-2-linux-x86_64.tar.gz`
- Przykładowa konfiguracja dla platformy Linux:
  ```
  {
      "name": "photo-editor-2-linux-x86_64.tar.gz",
      "browser_download_url": "https://github.com/tomekkrow-sys/Photo_Editor_2/releases/download/v1.0.1/photo-editor-2-linux-x86_64.tar.gz"
  }
  ```

### Windows (x64)
- Plik: `photo-editor-2-windows-x64.zip`
- Przykładowa konfiguracja dla platformy Windows:
  ```
  {
      "name": "photo-editor-2-windows-x64.zip",
      "browser_download_url": "https://github.com/tomekkrow-sys/Photo_Editor_2/releases/download/v1.0.1/photo-editor-2-windows-x64.zip"
  }
  ```

## 3. Weryfikacja działania

Po utworzeniu release'u menedżer aktualizacji powinien:
1. Wczytać konfigurację z `config/updater_config.json`
2. Sprawdzić wersję z `version.txt` (1.0.1)
3. Pobrać listę release'ów z GitHub
4. Porównać wersje
5. Jeśli nowsza wersja dostępna, pobrać odpowiedni plik do aktualizacji

## 4. Testowanie

### Test w terminalu:
```bash
# Po rozpakowaniu projektu
python3 -c "
from unified_updater_final import UpdateManager
updater = UpdateManager()
latest = updater.get_latest_version()
print(f'Latest version from GitHub: {latest}')
"
```

## 5. Wymagania dla release

Upewnij się, że pliki release'ów:
- Zawierają odpowiednie nazwy plików zgodne ze standardem (np. `photo-editor-2-linux-x86_64.tar.gz`)
- Mają dostępne linki do pobierania
- Są dołączone jako assety do odpowiedniego release'u