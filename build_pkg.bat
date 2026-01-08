@echo off
REM Simple PKG Builder for Windows
REM Usage: build_pkg.bat

echo ================================================
echo Rocksmith PC to PS4 PKG Builder
echo ================================================
echo.

REM Check if PkgTool.Core.exe exists
if not exist "PkgTool.Core.exe" (
    echo ERROR: PkgTool.Core.exe not found in current directory
    echo Please make sure PkgTool.Core.exe is in the same folder
    pause
    exit /b 1
)

REM Check if GP4 file exists
if not exist "cooppois_p.gp4" (
    echo ERROR: cooppois_p.gp4 not found
    echo Please run the Python converter first to create the GP4 file
    pause
    exit /b 1
)

echo Building PKG from GP4 project...
echo.

REM Build the PKG
PkgTool.Core.exe pkg_build cooppois_p.gp4 .

if errorlevel 1 (
    echo.
    echo ERROR: PKG build failed!
    echo Check the error messages above
    pause
    exit /b 1
)

echo.
echo ================================================
echo SUCCESS! PKG file created!
echo ================================================
echo.
echo Look for cooppois_p.pkg in the current directory
echo Copy it to USB drive at: PS4\PACKAGES\
echo.
pause
