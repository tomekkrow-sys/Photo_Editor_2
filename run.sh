#!/bin/bash
export PYTHONFAULTHANDLER=1
python3 -X faulthandler photo_editor.py 2>crash.log
