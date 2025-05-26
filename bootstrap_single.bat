@echo off
SETLOCAL ENABLEEXTENSIONS

echo ========================================
echo ResearcherNexus Single Process Startup
echo ========================================

REM 强力清理所有相关进程
echo [1/5] Force cleaning all processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 >nul

REM 再次确认清理
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 1 >nul

REM 清理端口占用
echo [2/5] Cleaning port usage...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :8000') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :3000') do (
    taskkill /f /pid %%a >nul 2>&1
)
timeout /t 2 >nul

REM 验证清理结果
echo [3/5] Verifying cleanup...
tasklist | findstr "python.exe node.exe" >nul 2>&1
if %errorlevel%==0 (
    echo ⚠️ Warning: Some processes still running
    tasklist | findstr "python.exe node.exe"
    echo Waiting for cleanup...
    timeout /t 3 >nul
) else (
    echo ✅ All processes cleaned
)

REM 启动后端（在新窗口中）
echo [4/5] Starting backend server...
start "ResearcherNexus-Backend" cmd /c "echo Starting Backend Server... && uv run server.py && pause"
timeout /t 8 >nul

REM 启动前端（在新窗口中）
echo [5/5] Starting frontend server...
cd web
start "ResearcherNexus-Frontend" cmd /c "echo Starting Frontend Server... && pnpm dev && pause"

echo.
echo ========================================
echo Services Started Successfully!
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Two separate windows have been opened:
echo 1. Backend Server (Python)
echo 2. Frontend Server (Node.js)
echo.
echo To stop services:
echo - Close both server windows manually, OR
echo - Run: stop_services.bat
echo.
echo Press any key to exit this launcher...
pause >nul

ENDLOCAL 