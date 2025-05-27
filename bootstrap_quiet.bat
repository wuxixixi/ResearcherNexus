@echo off
:: ResearcherNexus Quiet Bootstrap Script - Suppresses backuper 404 messages
:: This script starts the frontend and backend services without the annoying 404 logs

echo Starting ResearcherNexus in quiet mode...
echo.

:: Check if processes are already running
tasklist /FI "IMAGENAME eq node.exe" 2>NUL | find /I /N "node.exe">NUL
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Node.js processes are already running.
    echo Please run stop_services.bat first if you want to restart.
    echo.
)

tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if %ERRORLEVEL% EQU 0 (
    echo [WARNING] Python processes are already running.
    echo Please run stop_services.bat first if you want to restart.
    echo.
)

:: Check if we're in development or production mode
if exist "web\.next\BUILD_ID" (
    echo Running in PRODUCTION mode
    set "FRONTEND_CMD=cd web && pnpm start"
) else (
    echo Running in DEVELOPMENT mode
    echo [NOTE] Run 'cd web && pnpm build' to build for production
    set "FRONTEND_CMD=cd web && pnpm dev"
)

:: Start Backend Server (with updated code that handles /c_hello)
echo.
echo Starting Backend Server...
start /B cmd /c "python server.py 2>&1"

:: Wait for backend to be ready
echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

:: Test backend health
curl -s http://localhost:8000/api/health >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend failed to start!
    echo Please check the logs.
    pause
    exit /b 1
)

echo Backend is ready!

:: Start Frontend
echo.
echo Starting Frontend...
start /B cmd /c "%FRONTEND_CMD% 2>&1"

:: Wait for frontend to be ready
echo Waiting for frontend to start...
timeout /t 5 /nobreak >nul

:: Display access information
echo.
echo ========================================
echo ResearcherNexus is running!
echo.
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo.
echo The /c_hello requests from backuper are now handled silently.
echo.
echo Press Ctrl+C to stop the services
echo ========================================
echo.

:: Keep the script running
:loop
timeout /t 60 /nobreak >nul
goto loop 