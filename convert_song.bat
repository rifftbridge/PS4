@echo off
REM Complete Rocksmith PC to PS4 Converter
REM Usage: convert_song.bat <input.psarc> [song_title]
REM Example: convert_song.bat cooppois_p.psarc "Poison by Alice Cooper"

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Usage: convert_song.bat ^<input.psarc^> [song_title]
    echo.
    echo Example:
    echo   convert_song.bat cooppois_p.psarc "Poison by Alice Cooper"
    echo.
    pause
    exit /b 1
)

set "INPUT=%~1"
set "BASENAME=%~n1"
set "OUTPUT=%BASENAME%_ps4"
set "TITLE=%~2"

REM Use default title if not provided
if "%TITLE%"=="" (
    set "TITLE=Rocksmith2014 - %BASENAME%"
)

echo ================================================
echo Rocksmith PC to PS4 DLC Converter
echo ================================================
echo.
echo Input:  %INPUT%
echo Output: %OUTPUT%
echo Title:  %TITLE%
echo.

REM Check if input file exists
if not exist "%INPUT%" (
    echo ERROR: Input file not found: %INPUT%
    pause
    exit /b 1
)

REM Check if Python script exists
if not exist "rocksmith_pc_to_ps4_complete.py" (
    echo ERROR: rocksmith_pc_to_ps4_complete.py not found
    echo Please download it from GitHub or create it in this directory
    pause
    exit /b 1
)

REM Check if PkgTool.Core.exe exists
if not exist "PkgTool.Core.exe" (
    echo ERROR: PkgTool.Core.exe not found
    echo Please copy PkgTool.Core.exe to this directory
    pause
    exit /b 1
)

echo Step 1/2: Creating GP4 project...
echo.

REM Run Python converter
python rocksmith_pc_to_ps4_complete.py "%INPUT%" "%OUTPUT%" "%TITLE%"

if errorlevel 1 (
    echo ERROR: Python conversion failed
    pause
    exit /b 1
)

echo.
echo Step 2/2: Building PKG file...
echo.

REM Build PKG from GP4
PkgTool.Core.exe pkg_build "%OUTPUT%\%BASENAME%.gp4" "%OUTPUT%"

if errorlevel 1 (
    echo ERROR: PKG build failed
    pause
    exit /b 1
)

echo.
echo ================================================
echo SUCCESS! Conversion complete!
echo ================================================
echo.
echo PKG file created: %OUTPUT%\%BASENAME%.pkg
echo.
echo Next steps:
echo 1. Copy %BASENAME%.pkg to USB drive (FAT32 format)
echo 2. Create folder on USB: PS4\PACKAGES\
echo 3. Put the .pkg file in that folder
echo 4. On PS4, go to Package Installer and install
echo 5. Launch Rocksmith 2014 and enjoy!
echo.
pause
