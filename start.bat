@echo off
chcp 65001 >nul 2>nul
cd /d "%~dp0"

echo ========================================
echo   Stock Advisor - One-Click Start
echo ========================================
echo.

echo [1/3] Backend dependencies...
if not exist "backend\venv" (
    python -m venv "backend\venv"
)
"backend\venv\Scripts\pip.exe" install -q -r "backend\requirements.txt" 2>nul
echo   [OK] Backend ready

echo [2/3] Frontend dependencies...
if not exist "frontend\node_modules" (
    cd /d "%~dp0frontend"
    call npm install --silent 2>nul
    cd /d "%~dp0"
)
echo   [OK] Frontend ready

echo [3/3] Starting services...
taskkill /f /im python.exe >nul 2>&1
timeout /t 1 /nobreak >nul

start "Backend" cmd /c "cd /d "%~dp0backend" && "venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
start "Frontend" cmd /c "cd /d "%~dp0frontend" && npx vite --host"

timeout /t 4 /nobreak >nul

echo.
echo ========================================
echo   All services running!
echo   Backend : http://127.0.0.1:8000
echo   Frontend: http://localhost:5173
echo   API Docs: http://127.0.0.1:8000/docs
echo ========================================
echo.
echo Close the windows to stop, or press any key...
pause >nul

echo Stopping...
taskkill /f /fi "WindowTitle eq Backend*" >nul 2>&1
taskkill /f /fi "WindowTitle eq Frontend*" >nul 2>&1
echo Done.