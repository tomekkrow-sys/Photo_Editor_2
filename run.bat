@echo off
rem Photo Editor 2 - uruchamianie pod Windows
set PYTHONFAULTHANDLER=1
python -X faulthandler photo_editor.py 2>crash.log
if errorlevel 1 pause
