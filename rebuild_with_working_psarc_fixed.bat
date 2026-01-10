@echo off
REM Rebuild PKG using EXACT files from working Arczi PKG
REM This creates an exact replica that should work

echo ================================================
echo Creating EXACT Replica of Working PKG
echo ================================================
echo.

REM Check prerequisites
if not exist "PkgTool.Core.exe" (
    echo ERROR: PkgTool.Core.exe not found
    pause
    exit /b 1
)

if not exist "CoopPois_from_working_pkg.psarc" (
    echo ERROR: CoopPois_from_working_pkg.psarc not found
    echo Please download this file from GitHub samples folder
    pause
    exit /b 1
)

if not exist "icon0_from_working_pkg.png" (
    echo ERROR: icon0_from_working_pkg.png not found
    echo Please download this file from GitHub samples folder
    pause
    exit /b 1
)

echo Step 1: Creating directory structure...
if exist "arczi_replica.gp4" del /Q arczi_replica.gp4
if exist "build_dir" rd /S /Q build_dir
mkdir build_dir\Sc0
mkdir build_dir\Image0\DLC
echo   Done!
echo.

echo Step 2: Creating param.sfo with EXACT settings...
REM Create a temporary Python script
echo import struct > create_sfo.py
echo. >> create_sfo.py
echo content_id = "EP0001-CUSA00745_00-RS002SONG0001059" >> create_sfo.py
echo title = "Rocksmith2014 - Poison by Alice Cooper" >> create_sfo.py
echo pubtoolinfo = "c_date=20250317,img0_l0_size=6,img0_l1_size=0,img0_sc_ksize=512,img0_pc_ksize=576" >> create_sfo.py
echo. >> create_sfo.py
echo entries = [ >> create_sfo.py
echo     ("ATTRIBUTE", 0, 4, 0x0404), >> create_sfo.py
echo     ("CATEGORY", "ac", 4, 0x0204), >> create_sfo.py
echo     ("CONTENT_ID", content_id, 48, 0x0204), >> create_sfo.py
echo     ("FORMAT", "obs", 4, 0x0204), >> create_sfo.py
echo     ("PUBTOOLINFO", pubtoolinfo, 512, 0x0204), >> create_sfo.py
echo     ("PUBTOOLVER", 0x03870000, 4, 0x0404), >> create_sfo.py
echo     ("TITLE", title, 128, 0x0204), >> create_sfo.py
echo     ("TITLE_ID", "CUSA00745", 12, 0x0204), >> create_sfo.py
echo     ("VERSION", "01.00", 8, 0x0204), >> create_sfo.py
echo ] >> create_sfo.py
echo. >> create_sfo.py
echo sfo = bytearray() >> create_sfo.py
echo sfo += b'\x00PSF' >> create_sfo.py
echo sfo += struct.pack('^<I', 0x0101) >> create_sfo.py
echo. >> create_sfo.py
echo key_data = b"" >> create_sfo.py
echo for key, value, max_len, data_type in entries: >> create_sfo.py
echo     key_data += key.encode('utf-8') + b'\x00' >> create_sfo.py
echo while len(key_data) %% 4 != 0: >> create_sfo.py
echo     key_data += b'\x00' >> create_sfo.py
echo. >> create_sfo.py
echo key_table_start = 20 >> create_sfo.py
echo index_table_size = len(entries) * 16 >> create_sfo.py
echo data_table_start = key_table_start + index_table_size + len(key_data) >> create_sfo.py
echo. >> create_sfo.py
echo sfo += struct.pack('^<I', key_table_start + index_table_size) >> create_sfo.py
echo sfo += struct.pack('^<I', data_table_start) >> create_sfo.py
echo sfo += struct.pack('^<I', len(entries)) >> create_sfo.py
echo. >> create_sfo.py
echo data_values = [] >> create_sfo.py
echo for key, value, max_len, data_type in entries: >> create_sfo.py
echo     if data_type == 0x0404: >> create_sfo.py
echo         data_values.append(struct.pack('^<I', value)) >> create_sfo.py
echo     else: >> create_sfo.py
echo         data_values.append(value.encode('utf-8') + b'\x00') >> create_sfo.py
echo. >> create_sfo.py
echo key_offset = 0 >> create_sfo.py
echo data_offset = 0 >> create_sfo.py
echo for i, (key, value, max_len, data_type) in enumerate(entries): >> create_sfo.py
echo     sfo += struct.pack('^<H', key_offset) >> create_sfo.py
echo     sfo += struct.pack('^<H', data_type) >> create_sfo.py
echo     sfo += struct.pack('^<I', len(data_values[i])) >> create_sfo.py
echo     sfo += struct.pack('^<I', max_len) >> create_sfo.py
echo     sfo += struct.pack('^<I', data_offset) >> create_sfo.py
echo     key_offset += len(key) + 1 >> create_sfo.py
echo     data_offset += max_len >> create_sfo.py
echo. >> create_sfo.py
echo sfo += key_data >> create_sfo.py
echo. >> create_sfo.py
echo for i, (key, value, max_len, data_type) in enumerate(entries): >> create_sfo.py
echo     data = data_values[i] >> create_sfo.py
echo     sfo += data >> create_sfo.py
echo     padding = max_len - len(data) >> create_sfo.py
echo     if padding ^> 0: >> create_sfo.py
echo         sfo += b'\x00' * padding >> create_sfo.py
echo. >> create_sfo.py
echo with open('build_dir/Sc0/param.sfo', 'wb') as f: >> create_sfo.py
echo     f.write(bytes(sfo)) >> create_sfo.py
echo. >> create_sfo.py
echo print(f"Created param.sfo: {len(sfo)} bytes") >> create_sfo.py

python create_sfo.py
del create_sfo.py
echo.

echo Step 3: Copying working files...
copy /Y "icon0_from_working_pkg.png" "build_dir\Sc0\icon0.png" >nul
copy /Y "CoopPois_from_working_pkg.psarc" "build_dir\Image0\DLC\CoopPois.psarc" >nul
echo   Done!
echo.

echo Step 4: Creating GP4 project file...
(
echo ^<?xml version="1.0" encoding="utf-8" standalone="yes"?^>
echo ^<psproject fmt="gp4" version="1000"^>
echo   ^<volume^>
echo     ^<volume_type^>pkg_ps4_ac_data^</volume_type^>
echo     ^<volume_id^>PS4VOLUME^</volume_id^>
echo     ^<volume_ts^>2025-03-17 00:00:00^</volume_ts^>
echo     ^<package content_id="EP0001-CUSA00745_00-RS002SONG0001059" passcode="00000000000000000000000000000000"/^>
echo   ^</volume^>
echo   ^<files img_no="0"^>
echo       ^<file targ_path="sce_sys/param.sfo" orig_path="build_dir/Sc0/param.sfo"/^>
echo       ^<file targ_path="sce_sys/icon0.png" orig_path="build_dir/Sc0/icon0.png"/^>
echo       ^<file targ_path="DLC/CoopPois.psarc" orig_path="build_dir/Image0/DLC/CoopPois.psarc" pfs_compression="enable"/^>
echo   ^</files^>
echo   ^<rootdir^>
echo     ^<dir targ_name="sce_sys"/^>
echo     ^<dir targ_name="DLC"/^>
echo   ^</rootdir^>
echo ^</psproject^>
) > arczi_replica.gp4
echo   Done!
echo.

echo Step 5: Building PKG...
PkgTool.Core.exe pkg_build arczi_replica.gp4 .
echo.

if exist "EP0001-CUSA00745_00-RS002SONG0001059.pkg" (
    echo ================================================
    echo SUCCESS! PKG Created!
    echo ================================================
    echo.
    echo File: EP0001-CUSA00745_00-RS002SONG0001059.pkg
    dir EP0001-CUSA00745_00-RS002SONG0001059.pkg
    echo.
    echo This PKG uses EXACT files from working Arczi PKG
    echo It should work identically on PS4
    echo.
) else (
    echo ERROR: PKG file was not created
)

pause
