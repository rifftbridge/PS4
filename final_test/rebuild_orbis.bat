@echo off
REM =============================================================================
REM Rocksmith PC to PS4 Converter - Using orbis-pub-cmd.exe (Sony's Official Tool)
REM This creates proper PFS-encrypted PKGs
REM =============================================================================

echo ============================================================
echo STEP 1: Converting PSARC to PS4 format
echo ============================================================
python rocksmith_pc_to_ps4_complete.py CoopPois_from_working_pkg.psarc . "Rocksmith2014 - Poison by Alice Cooper"

if errorlevel 1 (
    echo [ERROR] Conversion failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo STEP 2: Building PKG using orbis-pub-cmd.exe (Sony's tool)
echo ============================================================
echo This will create a proper PFS-encrypted PKG
echo.

REM orbis-pub-cmd.exe img_create --skip_digest CoopPois_from_working_pkg.gp4 .
orbis-pub-cmd.exe img_create CoopPois_from_working_pkg.gp4 .

if errorlevel 1 (
    echo [ERROR] PKG build failed!
    echo.
    echo Trying without digest calculation...
    orbis-pub-cmd.exe img_create --skip_digest CoopPois_from_working_pkg.gp4 .
    if errorlevel 1 (
        echo [ERROR] PKG build still failed!
        pause
        exit /b 1
    )
)

echo.
echo ============================================================
echo SUCCESS! PKG created with proper PFS encryption
echo ============================================================
echo.
echo PKG File: EP0001-CUSA00745_00-RS003715FCE87B8D.pkg
echo Location: %CD%
echo.
echo This PKG has proper PFS encryption and should work on PS4!
echo.
echo NEXT STEPS:
echo 1. Copy PKG to USB drive: PS4\PACKAGES\
echo 2. Install on PS4 via Package Installer
echo 3. Launch Rocksmith 2014 and check DLC list
echo.
pause
