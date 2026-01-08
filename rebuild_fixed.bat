@echo off
REM Rebuild PKG with fixed converter
REM Run this in C:\test after downloading the updated Python script

echo ================================================
echo Rebuilding PKG with FIXED Converter
echo ================================================
echo.

REM Check prerequisites
if not exist "PkgTool.Core.exe" (
    echo ERROR: PkgTool.Core.exe not found
    pause
    exit /b 1
)

if not exist "cooppois_p.psarc" (
    echo ERROR: cooppois_p.psarc not found
    pause
    exit /b 1
)

if not exist "rocksmith_pc_to_ps4_complete.py" (
    echo ERROR: rocksmith_pc_to_ps4_complete.py not found
    echo Please download the updated version from GitHub
    pause
    exit /b 1
)

echo Step 1: Cleaning old files...
if exist "cooppois_p.gp4" del /Q cooppois_p.gp4
if exist "build_dir" rd /S /Q build_dir
if exist "cooppois_p.pkg" del /Q cooppois_p.pkg
echo   Done!
echo.

echo Step 2: Creating GP4 with FIXED converter...
python rocksmith_pc_to_ps4_complete.py cooppois_p.psarc . "Poison by Alice Cooper"
echo.

if not exist "cooppois_p.gp4" (
    echo ERROR: GP4 file was not created
    pause
    exit /b 1
)

echo Step 3: Building PKG...
PkgTool.Core.exe pkg_build cooppois_p.gp4 .
echo.

if not exist "cooppois_p.pkg" (
    echo ERROR: PKG file was not created
    pause
    exit /b 1
)

echo ================================================
echo SUCCESS! PKG Created!
echo ================================================
echo.
echo File: cooppois_p.pkg
dir cooppois_p.pkg
echo.
echo Next steps:
echo 1. Copy cooppois_p.pkg to USB drive (FAT32)
echo 2. Create folder: PS4\PACKAGES\
echo 3. Put PKG file in that folder
echo 4. Install on PS4 using Package Installer
echo.
pause
