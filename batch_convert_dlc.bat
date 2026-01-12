@echo off
REM =============================================================================
REM Rocksmith PC to PS4 DLC Batch Converter
REM Converts all PSARC files in a folder to PS4 PKG format
REM =============================================================================

if "%~1"=="" (
    echo Usage: batch_convert_dlc.bat [input_folder] [output_folder]
    echo.
    echo Example:
    echo   batch_convert_dlc.bat "C:\Rocksmith\DLC" "C:\PS4\output"
    echo.
    echo This will convert all .psarc files in the input folder to PKG files.
    echo.
    pause
    exit /b 1
)

set INPUT_FOLDER=%~1
set OUTPUT_FOLDER=%~2

if "%OUTPUT_FOLDER%"=="" (
    set OUTPUT_FOLDER=%~dp0output
)

echo ============================================================
echo Rocksmith PC to PS4 Batch Converter
echo ============================================================
echo.
echo Input folder: %INPUT_FOLDER%
echo Output folder: %OUTPUT_FOLDER%
echo.
echo Press any key to start conversion...
pause > nul

python batch_convert_dlc.py "%INPUT_FOLDER%" "%OUTPUT_FOLDER%"

if errorlevel 1 (
    echo.
    echo [ERROR] Batch conversion failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo All conversions complete!
echo ============================================================
pause
