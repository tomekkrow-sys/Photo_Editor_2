# Komendy do utworzenia release'u v0.2.2 na GitHubie

## Przygotowanie

1. Sprawdź aktualne tagi:
```bash
git tag -l
```

2. Utwórz nowy tag v0.2.2 (jeśli jeszcze nie istnieje):
```bash
git tag -a v0.2.2 -m "Release version 0.2.2"
```

3. Wypchnij tag na GitHub:
```bash
git push origin v0.2.2
```

## Utworzenie release'u przez GitHub CLI

Jeśli masz zainstalowany `gh`:

```bash
gh release create 'v0.2.2' \
  --title 'Version 0.2.2' \
  --notes-file RELEASE_NOTES_v0.2.2.md \
  path/to/your/files...
```

## Użycie GitHub CLI bez pliku release notes

Jeśli nie chcesz używać pliku:

```bash
gh release create 'v0.2.2' \
  --title 'Version 0.2.2' \
  --notes "This release includes several bug fixes and performance improvements to the update manager system."
```

## Poniżej znajduje się zawartość RELEASE_NOTES_v0.2.2.md:

# Photo Editor 2 - Update Manager Release

## Version 0.2.2

This release includes several bug fixes and performance improvements to the update manager system.

## Changes

- Fixed memory leak in the update verification process
- Improved error handling for network timeouts during downloads
- Optimized backup creation process to reduce execution time
- Enhanced logging for debugging update failures
- Added validation for update file integrity before installation
- Fixed issue with automatic updates not working when system time is incorrect

## New Features

1. **Enhanced Error Handling**:
   - More descriptive error messages for failed updates
   - Better handling of network connectivity issues
   - Improved user feedback during update processes

2. **Performance Improvements**:
   - Optimized backup creation algorithm
   - Reduced memory consumption during update verification
   - Faster file integrity checks

## Backward Compatibility

This update maintains strict backward compatibility with existing code:
- The `check_and_update()` function works exactly as before
- No changes required for existing Photo Editor 2 applications
- All existing workflows remain functional

## Installation

The update manager is included in the main application and runs automatically at startup.

To manually check for updates, run:

```python
from updater import check_and_update
result = check_and_update()
```

## Configuration

Update settings can be modified via `config/updater_config.json`:

```json
{
    "github": {
        "api_url": "https://api.github.com",
        "owner": "tomekkrow-sys",
        "repo": "Photo_Editor_2"
    },
    "update": {
        "check_interval_hours": 24,
        "backup_enabled": true,
        "auto_update": false,
        "background_updates": true
    }
}
```

## Requirements

- Python 3.6+
- PySide6>=6.5.0
- Pillow>=10.0.0
- rawpy>=0.18.0
- opencv-python-headless>=4.8.0
- gnupg>=0.5.0 (new requirement for this release)

This release improves the stability and reliability of Photo Editor 2's update system while maintaining existing functionality.