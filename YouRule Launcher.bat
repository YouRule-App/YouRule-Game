@echo off
cd /d "%~dp0"
start "YouRule Server" cmd /k "venv\Scripts\activate.bat && python watchdog.py"
timeout /t 3 /nobreak >nul
start "" "http://localhost:5002/anchor_setup.html"
echo Server is running. Close this window to stop.
echo.
pause >nul
taskkill /fi "windowtitle eq YouRule Server" /t /f >nul 2>&1
