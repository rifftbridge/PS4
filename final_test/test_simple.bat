@echo off
REM Simple test - just show what files exist

echo Current directory: %CD%
echo.
echo Checking for required files...
echo.

if exist "PkgTool.Core.exe" (
    echo [OK] PkgTool.Core.exe found
) else (
    echo [MISSING] PkgTool.Core.exe
)

if exist "rocksmith_pc_to_ps4_complete.py" (
    echo [OK] rocksmith_pc_to_ps4_complete.py found
) else (
    echo [MISSING] rocksmith_pc_to_ps4_complete.py
)

if exist "CoopPois_from_working_pkg.psarc" (
    echo [OK] CoopPois_from_working_pkg.psarc found
) else (
    echo [MISSING] CoopPois_from_working_pkg.psarc
)

echo.
echo All files in directory:
dir /b
echo.
pause

REM If all files exist, run the conversion
if not exist "PkgTool.Core.exe" goto :missing
if not exist "rocksmith_pc_to_ps4_complete.py" goto :missing
if not exist "CoopPois_from_working_pkg.psarc" goto :missing

echo.
echo All files found! Starting conversion...
echo.

python rocksmith_pc_to_ps4_complete.py CoopPois_from_working_pkg.psarc . "Rocksmith2014 - Poison by Alice Cooper"

if exist "icon0_from_working_pkg.png" (
    echo Replacing icon with working icon...
    copy /Y icon0_from_working_pkg.png build_dir\Sc0\icon0.png
)

echo.
echo Building PKG...
.\PkgTool.Core.exe pkg_build CoopPois_from_working_pkg.gp4 .

echo.
echo Looking for PKG file...
dir *.pkg

echo.
pause
goto :end

:missing
echo.
echo ERROR: Some required files are missing!
echo Please check the list above.
pause
goto :end

:end
