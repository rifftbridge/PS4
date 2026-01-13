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
python << EOF
import struct

content_id = "EP0001-CUSA00745_00-RS002SONG0001059"
title = "Rocksmith2014 - Poison by Alice Cooper"
pubtoolinfo = "c_date=20250317,img0_l0_size=6,img0_l1_size=0,img0_sc_ksize=512,img0_pc_ksize=576"

entries = [
    ("ATTRIBUTE", 0, 4, 0x0404),
    ("CATEGORY", "ac", 4, 0x0204),
    ("CONTENT_ID", content_id, 48, 0x0204),
    ("FORMAT", "obs", 4, 0x0204),
    ("PUBTOOLINFO", pubtoolinfo, 512, 0x0204),
    ("PUBTOOLVER", 0x03870000, 4, 0x0404),
    ("TITLE", title, 128, 0x0204),
    ("TITLE_ID", "CUSA00745", 12, 0x0204),
    ("VERSION", "01.00", 8, 0x0204),
]

sfo = bytearray()
sfo += b'\x00PSF'
sfo += struct.pack('<I', 0x0101)

key_data = b""
for key, value, max_len, data_type in entries:
    key_data += key.encode('utf-8') + b'\x00'
while len(key_data) %% 4 != 0:
    key_data += b'\x00'

key_table_start = 20
index_table_size = len(entries) * 16
data_table_start = key_table_start + index_table_size + len(key_data)

sfo += struct.pack('<I', key_table_start + index_table_size)
sfo += struct.pack('<I', data_table_start)
sfo += struct.pack('<I', len(entries))

data_values = []
for key, value, max_len, data_type in entries:
    if data_type == 0x0404:
        data_values.append(struct.pack('<I', value))
    else:
        data_values.append(value.encode('utf-8') + b'\x00')

key_offset = 0
data_offset = 0
for i, (key, value, max_len, data_type) in enumerate(entries):
    sfo += struct.pack('<H', key_offset)
    sfo += struct.pack('<H', data_type)
    sfo += struct.pack('<I', len(data_values[i]))
    sfo += struct.pack('<I', max_len)
    sfo += struct.pack('<I', data_offset)
    key_offset += len(key) + 1
    data_offset += max_len

sfo += key_data

for i, (key, value, max_len, data_type) in enumerate(entries):
    data = data_values[i]
    sfo += data
    padding = max_len - len(data)
    if padding > 0:
        sfo += b'\x00' * padding

with open('build_dir/Sc0/param.sfo', 'wb') as f:
    f.write(bytes(sfo))

print(f"Created param.sfo: {len(sfo)} bytes")
EOF

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
