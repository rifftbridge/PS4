@echo off
REM =============================================================================
REM Rocksmith PC to PS4 Converter - WORKING SOLUTION
REM Converts any PC/Steam PSARC to PS4 PKG
REM =============================================================================

if "%~1"=="" (
    echo Usage: convert_song.bat [psarc_file] [song_title]
    echo.
    echo Example:
    echo   convert_song.bat "cherub_rock.psarc" "Cherub Rock by Smashing Pumpkins"
    echo.
    pause
    exit /b 1
)

set PSARC_FILE=%~1
set SONG_TITLE=%~2

if "%SONG_TITLE%"=="" (
    echo [ERROR] Song title is required!
    echo Usage: convert_song.bat [psarc_file] [song_title]
    pause
    exit /b 1
)

echo ============================================================
echo Rocksmith PC to PS4 Converter - WORKING SOLUTION
echo ============================================================
echo.
echo Input PSARC: %PSARC_FILE%
echo Song Title: %SONG_TITLE%
echo.

REM Step 1: Convert PSARC to PS4 format (creates GP4, param.sfo, copies files)
echo ============================================================
echo STEP 1: Converting PSARC to PS4 format
echo ============================================================
python rocksmith_pc_to_ps4_complete.py "%PSARC_FILE%" . "%SONG_TITLE%"

if errorlevel 1 (
    echo [ERROR] Conversion failed!
    pause
    exit /b 1
)

REM Find the generated GP4 file
for %%F in (*.gp4) do set GP4_FILE=%%F

if not defined GP4_FILE (
    echo [ERROR] GP4 file not found!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo STEP 2: Building PKG with LibOrbisPkg (proper PFS encryption)
echo ============================================================
echo.
echo Using: %GP4_FILE%
echo.

C:\PS4\tools\LibOrbisPkg\PkgTool.Core.exe pkg_build "%GP4_FILE%" .

if errorlevel 1 (
    echo [ERROR] PKG build failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo SUCCESS! PKG Created
echo ============================================================
echo.
echo The PKG has been created in the current directory.
echo.
echo NEXT STEPS:
echo 1. Copy PKG to USB: PS4\PACKAGES\
echo 2. Install on PS4 via Package Installer
echo 3. Launch Rocksmith 2014 and check DLC list
echo.
pause
