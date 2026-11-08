@echo off
cd /d "%~dp0"

docker compose up -d --wait
if errorlevel 1 (
    echo Database startup failed. Check Docker Desktop.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -B -m uvicorn app:app --reload
pause