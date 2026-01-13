@echo off
REM Complete Rocksmith PC to PS4 Converter with Format Conversion
REM This script converts PS4-format PSARCs to PC-format, then builds PKG

setlocal enabledelayedexpansion

if "%~1"=="" (
    echo ================================================
    echo Rocksmith PC to PS4 Complete Converter
    echo ================================================
    echo.
    echo Usage: convert_and_build.bat ^<input.psarc^> [song_title]
    echo.
    echo Example:
    echo   convert_and_build.bat cooppois_p.psarc "Poison by Alice Cooper"
    echo.
    echo This script will:
    echo   1. Check PSARC format (flags)
    echo   2. Convert to PC format if needed (flags 4 -^> 0)
    echo   3. Build GP4 project
    echo   4. Create PKG file
    echo.
    pause
    exit /b 1
)

set "INPUT=%~1"
set "BASENAME=%~n1"
set "TITLE=%~2"

if "%TITLE%"=="" (
    set "TITLE=Rocksmith2014 - %BASENAME%"
)

echo ================================================
echo Rocksmith PC to PS4 Complete Converter
echo ================================================
echo.
echo Input:  %INPUT%
echo Title:  %TITLE%
echo.

REM Check prerequisites
if not exist "PkgTool.Core.exe" (
    echo ERROR: PkgTool.Core.exe not found
    pause
    exit /b 1
)

if not exist "rocksmith_pc_to_ps4_complete.py" (
    echo ERROR: rocksmith_pc_to_ps4_complete.py not found
    pause
    exit /b 1
)

if not exist "convert_psarc_to_pc_format.py" (
    echo ERROR: convert_psarc_to_pc_format.py not found
    pause
    exit /b 1
)

if not exist "%INPUT%" (
    echo ERROR: Input file not found: %INPUT%
    pause
    exit /b 1
)

echo Step 1/4: Checking PSARC format...
echo.

REM Check current format
python << EOF
import struct
with open('%INPUT%', 'rb') as f:
    f.seek(28)
    flags = struct.unpack('>I', f.read(4))[0]
    if flags == 0:
        print("Format: PC (flags=0) - No conversion needed")
        exit(0)
    elif flags == 4:
        print("Format: PS4/Mac (flags=4) - Conversion required")
        exit(1)
    else:
        print(f"Format: Unknown (flags={flags})")
        exit(2)
EOF

if errorlevel 1 (
    echo.
    echo Step 2/4: Converting to PC format...
    python convert_psarc_to_pc_format.py "%INPUT%" "%BASENAME%_pc.psarc"
    set "WORKING_PSARC=%BASENAME%_pc.psarc"
    echo.
) else (
    echo   Already in PC format, using original file
    set "WORKING_PSARC=%INPUT%"
    echo.
)

echo Step 3/4: Creating GP4 project...
python rocksmith_pc_to_ps4_complete.py "%WORKING_PSARC%" "%BASENAME%_ps4" "%TITLE%"
echo.

if not exist "%BASENAME%_ps4\%BASENAME%_pc.gp4" (
    if not exist "%BASENAME%_ps4\%BASENAME%.gp4" (
        echo ERROR: GP4 file was not created
        pause
        exit /b 1
    )
    set "GP4_FILE=%BASENAME%_ps4\%BASENAME%.gp4"
) else (
    set "GP4_FILE=%BASENAME%_ps4\%BASENAME%_pc.gp4"
)

echo Step 4/4: Building PKG...
PkgTool.Core.exe pkg_build "%GP4_FILE%" "%BASENAME%_ps4"
echo.

REM Find the PKG file
for %%f in (%BASENAME%_ps4\*.pkg) do (
    set "PKG_FILE=%%f"
    goto :found
)

echo ERROR: PKG file was not created
pause
exit /b 1

:found
echo ================================================
echo SUCCESS! Conversion Complete!
echo ================================================
echo.
echo PKG file: !PKG_FILE!
dir "!PKG_FILE!"
echo.
echo Next steps:
echo 1. Copy PKG to USB drive (FAT32 format)
echo 2. Create folder on USB: PS4\PACKAGES\
echo 3. Put PKG file in that folder
echo 4. On PS4: Settings -^> Package Installer
echo 5. Install the PKG
echo 6. Launch Rocksmith 2014
echo.

if exist "%BASENAME%_pc.psarc" (
    echo NOTE: Converted PSARC saved as: %BASENAME%_pc.psarc
    echo.
)

pause
