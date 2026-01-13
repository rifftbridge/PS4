@echo off
REM Download all required files for Arczi Replica Test
REM Run this in an empty folder, then copy your PkgTool files

echo ================================================
echo Downloading Arczi Replica Test Files
echo ================================================
echo.

echo Downloading Python converter...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/final_test/rocksmith_pc_to_ps4_complete.py' -OutFile 'rocksmith_pc_to_ps4_complete.py'"

echo Downloading test script...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/final_test/rebuild_arczi_replica.bat' -OutFile 'rebuild_arczi_replica.bat'"

echo Downloading working PSARC...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/final_test/CoopPois_from_working_pkg.psarc' -OutFile 'CoopPois_from_working_pkg.psarc'"

echo Downloading working icon...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/final_test/icon0_from_working_pkg.png' -OutFile 'icon0_from_working_pkg.png'"

echo Downloading README...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/final_test/README.md' -OutFile 'README.md'"

echo Downloading checklist...
powershell -Command "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/final_test/CHECKLIST.txt' -OutFile 'CHECKLIST.txt'"

echo.
echo ================================================
echo Download Complete!
echo ================================================
echo.
echo NEXT STEPS:
echo 1. Copy PkgTool.Core.exe and all .dll files from C:\test
echo 2. Run: rebuild_arczi_replica.bat
echo 3. Test the PKG on your PS4
echo.
echo See README.md for detailed instructions
echo.
pause
