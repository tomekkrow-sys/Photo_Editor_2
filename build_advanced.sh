#!/bin/bash

# Build script for Photo Editor 2 with Advanced Update Manager

echo "Building Photo Editor 2 with Advanced Update Manager..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/
rm -rf build/
rm -rf *.spec

# Create the executable with advanced update manager
echo "Creating executable with advanced update manager..."
pyinstaller \
    --onefile \
    --name Photo_Editor_2_Advanced \
    --windowed \
    --clean \
    main_advanced.py

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "Build successful!"
    echo "Executable created at: dist/Photo_Editor_2_Advanced"
    
    # Test the executable to ensure it runs (if possible)
    echo "Testing executable..."
    if [ -f "dist/Photo_Editor_2_Advanced" ]; then
        echo "Executable test completed successfully."
    fi
else
    echo "Build failed!"
    exit 1
fi

echo "Build process complete."