#!/bin/bash
cd "$(dirname "$0")"
if [ -x .venv/bin/python ]; then
    PY=.venv/bin/python
else
    PY=python3
fi
export PYTHONFAULTHANDLER=1
"$PY" -X faulthandler photo_editor.py 2>crash.log || {
    echo "Program zakonczyl sie bledem - szczegoly w crash.log"
    exit 1
}
