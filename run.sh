#!/bin/bash
set -e
cd "$(dirname "$0")"
PY="$(dirname "$0")/.venv/bin/python3"
export PYTHONFAULTHANDLER=1
"$PY" -X faulthandler photo_editor.py 2>crash.log || {
    echo "Program zakonczyl sie bledem - szczegoly w crash.log"
    exit 1
}
