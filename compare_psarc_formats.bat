@echo off
REM Quick test to compare PSARC formats

echo ================================================
echo PSARC Format Comparison Test
echo ================================================
echo.

if not exist "cooppois_p.psarc" (
    echo ERROR: cooppois_p.psarc not found
    pause
    exit /b 1
)

if not exist "CoopPois_from_working_pkg.psarc" (
    echo ERROR: CoopPois_from_working_pkg.psarc not found
    echo Please download from GitHub first
    pause
    exit /b 1
)

echo Analyzing your PC PSARC...
python << EOF
import struct

with open('cooppois_p.psarc', 'rb') as f:
    f.seek(0)
    magic = f.read(4)
    version = struct.unpack('>HH', f.read(4))
    compression = f.read(4)
    toc_length = struct.unpack('>I', f.read(4))[0]
    toc_entry_size = struct.unpack('>I', f.read(4))[0]
    num_files = struct.unpack('>I', f.read(4))[0]
    block_size = struct.unpack('>I', f.read(4))[0]
    archive_flags = struct.unpack('>I', f.read(4))[0]

    print("Your PC PSARC (cooppois_p.psarc):")
    print(f"  Files: {num_files}")
    print(f"  Archive Flags: 0x{archive_flags:08x} ({archive_flags})")
    if archive_flags == 0:
        print("  Format: PC (unpatched)")
    elif archive_flags == 4:
        print("  Format: PS4/Mac (pre-converted)")
    else:
        print("  Format: Unknown")
    print()

with open('CoopPois_from_working_pkg.psarc', 'rb') as f:
    f.seek(0)
    magic = f.read(4)
    version = struct.unpack('>HH', f.read(4))
    compression = f.read(4)
    toc_length = struct.unpack('>I', f.read(4))[0]
    toc_entry_size = struct.unpack('>I', f.read(4))[0]
    num_files = struct.unpack('>I', f.read(4))[0]
    block_size = struct.unpack('>I', f.read(4))[0]
    archive_flags = struct.unpack('>I', f.read(4))[0]

    print("Working PKG PSARC (CoopPois_from_working_pkg.psarc):")
    print(f"  Files: {num_files}")
    print(f"  Archive Flags: 0x{archive_flags:08x} ({archive_flags})")
    if archive_flags == 0:
        print("  Format: PC (vanilla/unpatched)")
    elif archive_flags == 4:
        print("  Format: PS4/Mac (converted)")
    else:
        print("  Format: Unknown")
    print()

print("CONCLUSION:")
print("="*50)
if archive_flags == 0:
    print("Working PKG uses PC-format PSARC (flags=0)")
    print("Your files are PS4-format (flags=4)")
    print("You need to convert PS4-format -> PC-format")
else:
    print("Working PKG uses PS4-format PSARC")
    print("Your files should work if other params match")

EOF

echo.
pause
