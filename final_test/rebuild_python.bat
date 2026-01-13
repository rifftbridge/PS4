@echo off
REM =============================================================================
REM Rocksmith PC to PS4 Converter - PYTHON-ONLY VERSION
REM No DLL dependencies required!
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
echo STEP 2: Building PKG using Python PKG builder
echo ============================================================
python ..\ps4_pkg_builder.py CoopPois_from_working_pkg.gp4 .

if errorlevel 1 (
    echo [ERROR] PKG build failed!
    pause
    exit /b 1
)

echo.
echo ============================================================
echo SUCCESS! PKG created
echo ============================================================
echo.
echo PKG File: EP0001-CUSA00745_00-RS003715FCE87B8D.pkg
echo Location: %CD%
echo.
echo NEXT STEPS:
echo 1. Copy PKG to USB drive: PS4\PACKAGES\
echo 2. Install on PS4 via Package Installer
echo 3. Launch Rocksmith 2014 and check DLC list
echo.
echo NOTE: This is a simplified fake PKG without PFS encryption
echo       It should work on GoldHEN jailbroken PS4 (FW 11.00)
echo       If it fails, we may need to build proper PFS PKGs
echo.
pause
