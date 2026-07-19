#!/bin/bash
set -e

echo "=== Syntax check ==="
python -m py_compile photo_editor.py $(find core ui config -name "*.py")

echo "=== Ruff ==="
ruff check .

echo
echo "Testy zakończone pomyślnie."