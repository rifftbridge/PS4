@echo off
REM Rebuild PKG using EXACT PSARC from working Arczi PKG
REM This creates a replica that should work identically

echo ================================================
echo Creating EXACT Replica of Working Arczi PKG
echo ================================================
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

if not exist "CoopPois_from_working_pkg.psarc" (
    echo ERROR: CoopPois_from_working_pkg.psarc not found
    echo.
    echo Please download from GitHub:
    echo https://github.com/rifftbridge/PS4/blob/claude/rocksmith-pc-ps4-converter-TlrD1/samples/CoopPois_from_working_pkg.psarc
    pause
    exit /b 1
)

echo Step 1: Cleaning old files...
if exist "EP0001-CUSA00745_00-RS002SONG0001059.pkg" del /Q EP0001-CUSA00745_00-RS002SONG0001059.pkg
if exist "arczi_replica.gp4" del /Q arczi_replica.gp4
if exist "build_dir" rd /S /Q build_dir
echo   Done!
echo.

echo Step 2: Creating GP4 using working PSARC...
python rocksmith_pc_to_ps4_complete.py CoopPois_from_working_pkg.psarc . "Rocksmith2014 - Poison by Alice Cooper"
echo.

REM Rename the GP4 file for clarity
if exist "CoopPois_from_working_pkg.gp4" (
    ren "CoopPois_from_working_pkg.gp4" "arczi_replica.gp4"
)

if not exist "arczi_replica.gp4" (
    echo ERROR: GP4 file was not created
    pause
    exit /b 1
)

echo Step 3: Replace icon with working icon...
if exist "icon0_from_working_pkg.png" (
    copy /Y "icon0_from_working_pkg.png" "build_dir\Sc0\icon0.png" >nul
    echo   Replaced with working icon (474 KB)
) else (
    echo   Using generated icon (68 bytes - minimal)
)
echo.

echo Step 4: Building PKG...
PkgTool.Core.exe pkg_build arczi_replica.gp4 .
echo.

if exist "EP0001-CUSA00745_00-RS002SONG0001059.pkg" (
    echo ================================================
    echo SUCCESS! PKG Created!
    echo ================================================
    echo.
    dir EP0001-CUSA00745_00-RS002SONG0001059.pkg
    echo.
    echo This PKG uses:
    echo   - EXACT PSARC from working Arczi PKG (4.8 MB)
    echo   - param.sfo with PUBTOOLINFO and PUBTOOLVER (972 bytes)
    echo   - Same Content ID format as working PKG
    echo.
    echo It should work identically on PS4!
    echo.
) else (
    echo ERROR: PKG file was not created
    echo Check the output above for errors
)

pause
