@echo off
REM RiffBridge Build Script - FINAL with All Fixes
REM - Icon embedded
REM - Artwork embedded  
REM - PS4 files accepted

echo.
echo ============================================================================
echo  RIFFBRIDGE BUILD - FINAL VERSION
echo ============================================================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo Running from: %CD%
echo.

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] ERROR: Python not found!
    pause
    exit /b 1
)

echo [1/5] Python found:
python --version
echo.

REM Check required files
echo [2/5] Checking required files...

if not exist "rocksmith_gui.py" (
    echo [!] ERROR: rocksmith_gui.py not found!
    echo Current directory: %CD%
    pause
    exit /b 1
)

if not exist "enhanced_converter.py" goto :missing
if not exist "rocksmith_pc_to_ps4.py" goto :missing
if not exist "steam_dlc_database.py" goto :missing
if not exist "requirements_gui.txt" goto :missing

echo   + All Python files found
echo.

REM Check for icon
if exist "RiffBridge_icon.ico" (
    echo   + Icon found: RiffBridge_icon.ico
    set ICON_FLAG=--icon=RiffBridge_icon.ico
    set ICON_DATA=--add-data "RiffBridge_icon.ico;."
) else (
    echo   ! Icon not found
    set ICON_FLAG=
    set ICON_DATA=
)

REM Check for artwork (new filename!)
set ARTWORK_FLAG=
if exist "Riff_Bridge_cover_art.jpg" (
    echo   + Artwork found: Riff_Bridge_cover_art.jpg
    set "ARTWORK_FLAG=--add-data Riff_Bridge_cover_art.jpg;."
    goto :artwork_done
)

if exist "Rifft_Bridge_square_artwork_02_copy.jpg" (
    echo   + Artwork found: Rifft_Bridge_square_artwork_02_copy.jpg
    set "ARTWORK_FLAG=--add-data Rifft_Bridge_square_artwork_02_copy.jpg;."
    goto :artwork_done
)

echo   ! Artwork not found
:artwork_done

echo.
goto :install

:missing
echo [!] ERROR: Missing required Python files!
pause
exit /b 1

:install
echo [3/5] Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements_gui.txt >nul 2>&1

echo   + Dependencies installed
echo.

echo [4/5] Building RiffBridge.exe...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build" >nul 2>&1
if exist "dist" rmdir /s /q "dist" >nul 2>&1
if exist "RiffBridge.spec" del /q "RiffBridge.spec" >nul 2>&1

echo Building... (takes ~1 minute)
echo.

python -m PyInstaller --name RiffBridge ^
    --onefile ^
    --windowed ^
    %ICON_FLAG% ^
    --add-data "enhanced_converter.py;." ^
    --add-data "rocksmith_pc_to_ps4.py;." ^
    --add-data "steam_dlc_database.py;." ^
    %ICON_DATA% ^
    %ARTWORK_FLAG% ^
    --hidden-import tkinterdnd2 ^
    --hidden-import PIL._tkinter_finder ^
    --hidden-import PIL.Image ^
    --hidden-import PIL.ImageDraw ^
    --hidden-import PIL.ImageFont ^
    --hidden-import PIL.ImageTk ^
    --collect-all tkinterdnd2 ^
    --clean ^
    rocksmith_gui.py

echo.
echo Build command completed with error level: %errorlevel%
echo.

REM Check if exe exists
if exist "dist\RiffBridge.exe" (
    echo.
    echo ============================================================================
    echo [5/5] BUILD SUCCESSFUL!
    echo ============================================================================
    echo.
    echo RiffBridge.exe created!
    echo Location: dist\RiffBridge.exe
    echo.
    
    REM Show size
    for %%A in (dist\RiffBridge.exe) do (
        set size=%%~zA
        set /a sizeMB=%%~zA/1024/1024
    )
    echo Size: ~%sizeMB% MB
    echo.
    
    echo Features:
    if not "%ICON_FLAG%"=="" echo   + Custom icon embedded
    if not "%ARTWORK_FLAG%"=="" echo   + Artwork embedded
    echo   + PS4 and PC files supported
    echo   + No Python needed to run
    echo.
    echo To test: dist\RiffBridge.exe
    echo.
    echo IMPORTANT: This .exe has the PS4 fix!
    echo            Delete any old RiffBridge.exe files!
    echo.
) else (
    echo.
    echo ============================================================================
    echo [!] BUILD FAILED - RiffBridge.exe was not created
    echo ============================================================================
    echo.
    echo Please check the error messages above.
    echo.
    echo Common issues:
    echo   - Missing dependencies: Run "pip install -r requirements_gui.txt"
    echo   - PyInstaller not installed: Run "pip install pyinstaller"
    echo   - Syntax error in rocksmith_gui.py
    echo.
    echo If you see errors about modules not found, try:
    echo   pip install --upgrade pyinstaller pillow tkinterdnd2
    echo.
    
    REM Check if there's a build log
    if exist "build\RiffBridge\warn-RiffBridge.txt" (
        echo Build warnings detected. Check: build\RiffBridge\warn-RiffBridge.txt
        echo.
    )
)

pause
