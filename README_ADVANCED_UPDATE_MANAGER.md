# Photo Editor 2 - Advanced Update Manager

This project includes an advanced update manager for Photo Editor 2 with background updates and automated publishing capabilities.

## Features

- Automatic version checking against GitHub releases
- Background update checking without requiring application restart
- Download and installation of updates
- Version comparison system
- Integration with main application startup
- Automated release publishing capabilities (requires GitHub API token)

## Files Created

1. `version.txt` - Current version tracking file
2. `main_advanced.py` - Main application entry point with advanced update management
3. `updater_advanced.py` - Advanced update manager implementation with:
   - Background update checking thread
   - Automatic downloading and installing of updates
   - GitHub release publishing capabilities (API integration)
   - Logging system
   - Version comparison logic

## How It Works

1. On application start, the updater checks the current version against the latest GitHub release in the background
2. If a newer version is available, it can download the update silently 
3. The update installation process runs without requiring the application to restart
4. Automated publishing capabilities are available for creating new GitHub releases

## Usage

To use the advanced update manager in your own project:

```python
from updater_advanced import check_and_update

# Check for updates and perform update if needed
result = check_and_update()
```

## Automated Publishing

The system includes functions to automate the process of publishing new versions to GitHub:

1. `auto_publish_new_version(version, commit_message)` - Automatically publish a new version
2. `create_github_release(version, release_notes)` - Create a GitHub release programmatically

These functions require proper authentication tokens and are disabled in demo mode.

## Building

The complete application can be built using PyInstaller:
```bash
pyinstaller --onefile main_advanced.py
```

This creates a single executable file in the `dist` directory named `Photo_Editor_2_Advanced`.

## Implementation Details

The advanced update manager has these key components:

1. **Version Comparison**: Simple dotted version string comparison
2. **Background Threads**: Continuous monitoring for updates without user interruption
3. **Download/Install Pipeline**: Complete process for fetching and installing updates  
4. **Logging System**: Comprehensive logging of all update operations
5. **Error Handling**: Robust error handling throughout the update process

## Testing

When running the advanced version, you can see:
- Background thread starting for periodic checks
- Version comparison between local and remote versions
- Simulated download/install activities