#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$PROJECT_DIR" || exit 1

clear

echo "=========================================="
echo "         Photo Editor 2.0"
echo "=========================================="
echo

if [ ! -d ".venv" ]; then
    echo "[ERROR] Brak środowiska .venv"
    exit 1
fi

source .venv/bin/activate

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] Python3 nie został znaleziony."
    exit 1
fi

mkdir -p logs

echo "Uruchamianie..."

python3 photo_editor.py 2>&1 | tee logs/startup.log

EXIT_CODE=${PIPESTATUS[0]}

echo
echo "=========================================="

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "Program zakończył pracę poprawnie."
else
    echo "Program zakończył się błędem."
    echo "Sprawdź:"
    echo "logs/startup.log"
fi

echo "Kod wyjścia: $EXIT_CODE"
echo "=========================================="

deactivate