@echo off
SETLOCAL ENABLEEXTENSIONS

REM Check if argument is dev mode
SET MODE=%1
IF "%MODE%"=="--dev" GOTO DEV
IF "%MODE%"=="-d" GOTO DEV
IF "%MODE%"=="dev" GOTO DEV
IF "%MODE%"=="development" GOTO DEV

:PROD
echo Starting ResearcherNexus in [PRODUCTION] mode...
CALL :CLEANUP_PROCESSES
echo Starting backend server...
start "ResearcherNexus-Backend" cmd /c "echo Starting Backend Server... && uv run server.py --host 172.16.128.43 && pause"
timeout /t 5 >nul
echo Starting frontend server...
cd web
start "ResearcherNexus-Frontend" cmd /c "echo Starting Frontend Server... && pnpm start && pause"
echo.
echo ========================================
echo ResearcherNexus Production Mode Started
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Two separate windows have been opened.
echo Press any key to stop all services...
pause
echo.
echo Stopping all services...
CALL :CLEANUP_PROCESSES
GOTO END

:DEV
echo Starting ResearcherNexus in [DEVELOPMENT] mode...
CALL :CLEANUP_PROCESSES
echo Starting backend server...
start "ResearcherNexus-Backend" cmd /c "echo Starting Backend Server... && uv run server.py --host 172.16.128.43 && pause"
timeout /t 8 >nul
echo Starting frontend development server...
cd web
start "ResearcherNexus-Frontend" cmd /c "echo Starting Frontend Server... && pnpm dev && pause"
echo.
echo ========================================
echo ResearcherNexus Development Mode Started
echo ========================================
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Two separate windows have been opened.
echo Press any key to stop all services...
pause
echo.
echo Stopping all services...
CALL :CLEANUP_PROCESSES
GOTO END

:CLEANUP_PROCESSES
echo [INFO] Cleaning up existing processes...

REM 强力清理多轮
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 2 >nul

REM 再次确认清理
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
timeout /t 1 >nul

REM 清理端口占用进程
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :8000') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr :3000') do (
    taskkill /f /pid %%a >nul 2>&1
)

REM 等待端口释放
timeout /t 3 >nul

REM 验证清理结果
tasklist | findstr "python.exe node.exe" >nul 2>&1
if %errorlevel%==0 (
    echo [WARN] Some processes may still be running
    timeout /t 2 >nul
) else (
    echo [OK] All processes cleaned successfully
)
GOTO :EOF

:END
ENDLOCAL
