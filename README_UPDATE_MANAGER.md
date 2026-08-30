# Photo Editor 2 - Update Manager Implementation

This project includes a basic update manager for Photo Editor 2.

## Features

- Automatic version checking against GitHub releases
- Download and installation of updates
- Version comparison system
- Integration with main application startup

## Files Created

1. `version.txt` - Current version tracking file
2. `main.py` - Main application entry point with update management
3. `updater.py` - Update manager implementation with download/install capabilities

## How It Works

1. On application start, the updater checks the current version against the latest GitHub release
2. If a newer version is available, it can download and install the update
3. After installation, the application restarts to run the new version

## Usage

To use the update manager in your own project:

```python
from updater import check_and_update

# Check for updates and perform update if needed
result = check_and_update()
```

## Building

The complete application can be built using PyInstaller:
```bash
pyinstaller --onefile main.py
```

This creates a single executable file in the `dist` directory.