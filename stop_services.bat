@echo off
echo ========================================
echo Stopping ResearcherNexus Services
echo ========================================

echo Stopping Python processes (Backend)...
taskkill /f /im python.exe >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Python processes stopped
) else (
    echo ℹ️ No Python processes found
)

echo Stopping Node.js processes (Frontend)...
taskkill /f /im node.exe >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Node.js processes stopped
) else (
    echo ℹ️ No Node.js processes found
)

echo.
echo Checking port status...
netstat -an | find ":8000" >nul
if %errorlevel%==0 (
    echo ⚠️ Port 8000 still in use
) else (
    echo ✅ Port 8000 is free
)

netstat -an | find ":3000" >nul
if %errorlevel%==0 (
    echo ⚠️ Port 3000 still in use
) else (
    echo ✅ Port 3000 is free
)

echo.
echo ========================================
echo Service cleanup completed!
echo ========================================
pause 