@echo off
SETLOCAL ENABLEEXTENSIONS

echo ========================================
echo ResearcherNexus Safe Development Startup
echo ========================================

REM 清理现有进程
echo [1/4] Cleaning up existing processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 >nul

REM 检查端口占用
echo [2/4] Checking port availability...
netstat -an | find ":8000" >nul
if %errorlevel%==0 (
    echo WARNING: Port 8000 is still in use. Waiting...
    timeout /t 5 >nul
)

netstat -an | find ":3000" >nul
if %errorlevel%==0 (
    echo WARNING: Port 3000 is still in use. Waiting...
    timeout /t 5 >nul
)

REM 启动后端
echo [3/4] Starting backend server...
start "ResearcherNexus-Backend" cmd /k "echo Backend Server && uv run server.py --host 172.16.128.43"
timeout /t 5 >nul

REM 启动前端
echo [4/4] Starting frontend development server...
cd web
start "ResearcherNexus-Frontend" cmd /k "echo Frontend Server && pnpm dev"

echo.
echo ========================================
echo Services Started Successfully!
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo To stop services:
echo 1. Close both server windows, OR
echo 2. Run: taskkill /f /im python.exe && taskkill /f /im node.exe
echo.
echo Press any key to exit this launcher...
pause >nul

ENDLOCAL 