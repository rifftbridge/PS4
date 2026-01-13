@echo off
REM =============================================================================
REM Rename PKG file to readable format
REM Usage: rename_pkg.bat "Song Title by Artist"
REM =============================================================================

if "%~1"=="" (
    echo Usage: rename_pkg.bat "Song Title by Artist"
    echo.
    echo Example:
    echo   rename_pkg.bat "Amber by 311"
    echo.
    pause
    exit /b 1
)

set SONG_TITLE=%~1

REM Find the most recent PKG file
for /f "delims=" %%F in ('dir /b /od *.pkg 2^>nul') do set NEWEST_PKG=%%F

if not defined NEWEST_PKG (
    echo [ERROR] No PKG file found in current directory
    pause
    exit /b 1
)

echo Found PKG: %NEWEST_PKG%
echo.

REM Parse song title to create filename
REM Example: "Amber by 311" -> "311-Amber_(PS4).pkg"
set NEW_NAME=%SONG_TITLE: by =-%
set NEW_NAME=%NEW_NAME: =_%
set NEW_NAME=%NEW_NAME:~0,50%_(PS4).pkg

echo Renaming to: %NEW_NAME%
ren "%NEWEST_PKG%" "%NEW_NAME%"

if errorlevel 1 (
    echo [ERROR] Rename failed
    pause
    exit /b 1
)

echo.
echo ✅ Success! Renamed to: %NEW_NAME%
echo.
pause
