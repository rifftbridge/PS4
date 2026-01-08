#!/usr/bin/env python3
"""
Complete Rocksmith PC to PS4 DLC Converter
Uses flatz's pkg_pfs_tool workflow
"""

import os
import sys
import shutil
import struct
from pathlib import Path
import subprocess
import hashlib


def create_param_sfo(content_id: str, title: str, title_id: str = "CUSA00745", version: str = "01.00") -> bytes:
    """Create param.sfo file in little-endian format"""
    entries = [
        ("ATTRIBUTE", 0, 4, 0x0404),
        ("CATEGORY", "ac", 4, 0x0204),
        ("CONTENT_ID", content_id, 48, 0x0204),
        ("FORMAT", "obs", 4, 0x0204),
        ("TITLE", title, 128, 0x0204),
        ("TITLE_ID", title_id, 12, 0x0204),
        ("VERSION", version, 8, 0x0204),
    ]

    sfo = bytearray()
    sfo += b'\x00PSF'
    sfo += struct.pack('<I', 0x0101)  # Version

    # Build key table
    key_data = b""
    for key, value, max_len, data_type in entries:
        key_data += key.encode('utf-8') + b'\x00'
    while len(key_data) % 4 != 0:
        key_data += b'\x00'

    key_table_start = 20
    index_table_size = len(entries) * 16
    data_table_start = key_table_start + index_table_size + len(key_data)

    sfo += struct.pack('<I', key_table_start + index_table_size)
    sfo += struct.pack('<I', data_table_start)
    sfo += struct.pack('<I', len(entries))

    # Prepare data values
    data_values = []
    for key, value, max_len, data_type in entries:
        if data_type == 0x0404:
            data_values.append(struct.pack('<I', value))
        else:
            data_values.append(value.encode('utf-8') + b'\x00')

    # Write index table
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

    # Write key table
    sfo += key_data

    # Write data table
    for i, (key, value, max_len, data_type) in enumerate(entries):
        data = data_values[i]
        sfo += data
        padding = max_len - len(data)
        if padding > 0:
            sfo += b'\x00' * padding

    return bytes(sfo)


def create_icon_png() -> bytes:
    """Create minimal PNG icon (1x1 pixel)"""
    return bytes.fromhex(
        '89504e470d0a1a0a0000000d4948445200000001000000010802000000'
        '907753de0000000c4944415478da626000000000050001b5a6b7cd0000'
        '000049454e44ae426082'
    )


def generate_content_id(psarc_name: str, title_id: str = "CUSA00745", region: str = "EP0001") -> str:
    """Generate a unique Content ID based on PSARC filename"""
    # Hash the filename to create unique ID (12 chars to make total 16 with RS00 prefix)
    hash_obj = hashlib.md5(psarc_name.encode())
    unique_id = hash_obj.hexdigest()[:12].upper()

    # Format: EP0001-CUSA00745_00-RS00XXXXXXXXXXXX (total 36 chars)
    return f"{region}-{title_id}_00-RS00{unique_id}"


def create_gp4(psarc_path: Path, output_gp4: Path, content_id: str, title: str):
    """Create GP4 project file"""

    psarc_name = psarc_path.name

    gp4_content = f'''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<psproject fmt="gp4" version="1000">
  <volume>
    <volume_type>pkg_ps4_ac_data</volume_type>
    <volume_id>PS4VOLUME</volume_id>
    <volume_ts>2026-01-07 00:00:00</volume_ts>
    <package content_id="{content_id}" passcode="00000000000000000000000000000000"/>
  </volume>
  <files img_no="0">
      <file targ_path="sce_sys/param.sfo" orig_path="build_dir/Sc0/param.sfo"/>
      <file targ_path="sce_sys/icon0.png" orig_path="build_dir/Sc0/icon0.png"/>
      <file targ_path="DLC/{psarc_name}" orig_path="build_dir/Image0/DLC/{psarc_name}" pfs_compression="enable"/>
  </files>
  <rootdir>
    <dir targ_name="sce_sys"/>
    <dir targ_name="DLC"/>
  </rootdir>
</psproject>
'''

    with open(output_gp4, 'w') as f:
        f.write(gp4_content)


def convert_pc_to_ps4(input_psarc: Path, output_dir: Path, song_title: str = None):
    """
    Convert PC PSARC to PS4 PKG

    This creates the directory structure and GP4 file needed for PKG building.
    Actual PKG building requires LibOrbisPkg PkgTool.exe
    """

    if not input_psarc.exists():
        print(f"ERROR: Input PSARC not found: {input_psarc}")
        return False

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate content ID and title
    psarc_name = input_psarc.stem
    if not song_title:
        song_title = f"Rocksmith2014 - {psarc_name}"

    content_id = generate_content_id(psarc_name)

    print(f"Converting: {input_psarc.name}")
    print(f"Content ID: {content_id}")
    print(f"Title: {song_title}")

    # Create build directory structure
    build_dir = output_dir / "build_dir"
    sc0_dir = build_dir / "Sc0"
    image0_dir = build_dir / "Image0" / "DLC"

    sc0_dir.mkdir(parents=True, exist_ok=True)
    image0_dir.mkdir(parents=True, exist_ok=True)

    # Create param.sfo
    param_sfo = create_param_sfo(content_id, song_title)
    with open(sc0_dir / "param.sfo", 'wb') as f:
        f.write(param_sfo)
    print(f"Created param.sfo: {len(param_sfo)} bytes")

    # Create icon0.png
    icon_png = create_icon_png()
    with open(sc0_dir / "icon0.png", 'wb') as f:
        f.write(icon_png)
    print(f"Created icon0.png: {len(icon_png)} bytes")

    # Copy PSARC to DLC directory
    shutil.copy2(input_psarc, image0_dir / f"{input_psarc.name}")
    print(f"Copied PSARC: {input_psarc.name}")

    # Create GP4 project file
    gp4_path = output_dir / f"{psarc_name}.gp4"
    create_gp4(input_psarc, gp4_path, content_id, song_title)
    print(f"Created GP4: {gp4_path}")

    print("\n" + "="*60)
    print("CONVERSION COMPLETE!")
    print("="*60)
    print(f"\nOutput directory: {output_dir}")
    print(f"GP4 project file: {gp4_path}")
    print(f"\nTo build PKG, use LibOrbisPkg PkgTool:")
    print(f"  PkgTool.exe pkg_build {gp4_path} {output_dir}")
    print("\nOr on Linux (if LibOrbisPkg is built):")
    print(f"  dotnet run --project PkgTool pkg_build {gp4_path} {output_dir}")

    return True


def main():
    if len(sys.argv) < 2:
        print("Rocksmith PC to PS4 DLC Converter")
        print("="*60)
        print("\nUsage: python3 rocksmith_pc_to_ps4_complete.py <input.psarc> [output_dir] [song_title]")
        print("\nExample:")
        print("  python3 rocksmith_pc_to_ps4_complete.py cooppois_p.psarc poison_output \"Poison by Alice Cooper\"")
        print("\nThis creates:")
        print("  - Directory structure for PKG building")
        print("  - param.sfo with proper metadata")
        print("  - icon0.png placeholder")
        print("  - GP4 project file")
        print("\nThen use LibOrbisPkg PkgTool to build the final PKG.")
        sys.exit(1)

    input_psarc = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(input_psarc.stem + "_ps4")
    song_title = sys.argv[3] if len(sys.argv) > 3 else None

    convert_pc_to_ps4(input_psarc, output_dir, song_title)


if __name__ == '__main__':
    main()
