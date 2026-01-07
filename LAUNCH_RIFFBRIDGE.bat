@echo off
REM RiffBridge Launcher - FIXED VERSION (Auto-CD)
REM Automatically changes to the script's directory

echo.
echo ============================================================================
echo  RIFFBRIDGE LAUNCHER
echo ============================================================================
echo.

REM Change to the directory where this batch file is located
cd /d "%~dp0"

echo Running from: %CD%
echo.

REM Try to find Python
set PYTHON_CMD=

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :run
)

python3 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python3
    goto :run
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py
    goto :run
)

echo [!] ERROR: Python not found!
echo.
echo Please install Python from: https://www.python.org/
echo.
pause
exit /b 1

:run
echo Python found: %PYTHON_CMD%
"%PYTHON_CMD%" --version
echo.

REM Check if rocksmith_gui.py exists
if not exist "rocksmith_gui.py" (
    echo [!] ERROR: rocksmith_gui.py not found!
    echo.
    echo Current directory: %CD%
    echo.
    echo Files in this directory:
    dir /b *.py
    echo.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
"%PYTHON_CMD%" -c "import tkinterdnd2" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo Installing required packages...
    "%PYTHON_CMD%" -m pip install -r requirements_gui.txt
    echo.
)

echo Launching RiffBridge...
echo.
"%PYTHON_CMD%" rocksmith_gui.py

if %errorlevel% neq 0 (
    echo.
    echo [!] ERROR: Failed to run RiffBridge
    echo.
    pause
)
