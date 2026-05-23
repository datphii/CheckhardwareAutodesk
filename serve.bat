@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe serve.py %1
) else (
    python serve.py %1
)
pause
