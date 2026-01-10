#!/usr/bin/env python3
"""
PS4 PKG Analyzer - Analyze structure of PKG files
Helps debug PKG format issues
"""

import struct
import sys
from pathlib import Path


def analyze_pkg_header(pkg_path: Path):
    """Analyze PS4 PKG header structure"""

    print(f"\n{'='*80}")
    print(f"PS4 PKG ANALYZER: {pkg_path.name}")
    print(f"{'='*80}\n")

    with open(pkg_path, 'rb') as f:
        # Read header
        header = f.read(0x1000)

        # Parse header (Big Endian)
        magic = struct.unpack('>I', header[0x00:0x04])[0]
        pkg_type = struct.unpack('>I', header[0x04:0x08])[0]
        pkg_flags = struct.unpack('>I', header[0x08:0x0C])[0]
        file_count = struct.unpack('>I', header[0x0C:0x10])[0]
        entry_count = struct.unpack('>I', header[0x10:0x14])[0]
        sc_entry_count = struct.unpack('>H', header[0x14:0x16])[0]
        entry_count_2 = struct.unpack('>H', header[0x16:0x18])[0]
        table_offset = struct.unpack('>I', header[0x18:0x1C])[0]
        entry_data_size = struct.unpack('>I', header[0x1C:0x20])[0]
        body_offset = struct.unpack('>Q', header[0x20:0x28])[0]
        body_size = struct.unpack('>Q', header[0x28:0x30])[0]
        content_offset = struct.unpack('>Q', header[0x30:0x38])[0]
        content_size = struct.unpack('>Q', header[0x38:0x40])[0]

        # Content ID (36 bytes at 0x40)
        content_id = header[0x40:0x64].decode('ascii', errors='ignore').rstrip('\x00')

        # More metadata
        drm_type = struct.unpack('>I', header[0x70:0x74])[0]
        content_type = struct.unpack('>I', header[0x74:0x78])[0]
        content_flags = struct.unpack('>I', header[0x78:0x7C])[0]

        print("HEADER INFORMATION:")
        print(f"  Magic:           0x{magic:08X} {'✓ VALID' if magic == 0x7F434E54 else '✗ INVALID'}")
        print(f"  PKG Type:        0x{pkg_type:08X} ({pkg_type})")
        print(f"  PKG Flags:       0x{pkg_flags:08X}")
        print(f"  File Count:      {file_count}")
        print(f"  Entry Count:     {entry_count}")
        print(f"  SC Entry Count:  {sc_entry_count}")
        print(f"  Entry Count 2:   {entry_count_2}")
        print(f"  Table Offset:    0x{table_offset:08X} ({table_offset})")
        print(f"  Entry Data Size: 0x{entry_data_size:08X} ({entry_data_size} bytes)")
        print(f"  Body Offset:     0x{body_offset:08X} ({body_offset})")
        print(f"  Body Size:       0x{body_size:08X} ({body_size} bytes, {body_size/(1024*1024):.2f} MB)")
        print(f"  Content Offset:  0x{content_offset:08X} ({content_offset})")
        print(f"  Content Size:    0x{content_size:08X} ({content_size} bytes, {content_size/(1024*1024):.2f} MB)")
        print(f"  Content ID:      '{content_id}'")
        print(f"  DRM Type:        0x{drm_type:08X} ({drm_type})")
        print(f"  Content Type:    0x{content_type:08X} ({content_type})")
        print(f"  Content Flags:   0x{content_flags:08X}")

        # Read entry table
        print(f"\n{'='*80}")
        print("ENTRY TABLE:")
        print(f"{'='*80}\n")

        f.seek(table_offset)
        for i in range(entry_count):
            entry_data = f.read(32)

            entry_id = struct.unpack('>I', entry_data[0x00:0x04])[0]
            filename_offset = struct.unpack('>I', entry_data[0x04:0x08])[0]
            flags1 = struct.unpack('>I', entry_data[0x08:0x0C])[0]
            flags2 = struct.unpack('>I', entry_data[0x0C:0x10])[0]
            file_offset = struct.unpack('>Q', entry_data[0x10:0x18])[0]
            file_size = struct.unpack('>Q', entry_data[0x18:0x20])[0]

            # Determine entry type
            entry_type = "UNKNOWN"
            if entry_id == 0x0001:
                entry_type = "DIGESTS"
            elif entry_id == 0x0400:
                entry_type = "LICENSE"
            elif entry_id == 0x1000:
                entry_type = "PARAM.SFO"
            elif entry_id == 0x1200:
                entry_type = "ICON0.PNG"
            elif entry_id >= 0x1201:
                entry_type = "DATA FILE"

            print(f"Entry {i+1:2d}:")
            print(f"  Entry ID:        0x{entry_id:04X} ({entry_type})")
            print(f"  Filename Offset: 0x{filename_offset:08X}")
            print(f"  Flags 1:         0x{flags1:08X}")
            print(f"  Flags 2:         0x{flags2:08X}")
            print(f"  File Offset:     0x{file_offset:08X} ({file_offset})")
            print(f"  File Size:       0x{file_size:08X} ({file_size} bytes, {file_size/(1024*1024):.2f} MB)")
            print()

        # File info
        pkg_file_size = pkg_path.stat().st_size
        print(f"{'='*80}")
        print("FILE INFORMATION:")
        print(f"{'='*80}\n")
        print(f"  Total PKG Size: {pkg_file_size} bytes ({pkg_file_size/(1024*1024):.2f} MB)")
        print(f"  Expected Size:  ~{body_offset + body_size} bytes")

        # Validation
        print(f"\n{'='*80}")
        print("VALIDATION:")
        print(f"{'='*80}\n")

        issues = []
        if magic != 0x7F434E54:
            issues.append("✗ Invalid magic number")
        else:
            print("✓ Magic number is valid")

        if content_id.startswith(('EP', 'UP', 'JP', 'HP')):
            print(f"✓ Content ID format looks valid")
        else:
            issues.append(f"✗ Content ID format may be invalid: '{content_id}'")

        if table_offset < 0x1000:
            issues.append(f"✗ Table offset too small: 0x{table_offset:08X}")
        else:
            print(f"✓ Table offset is reasonable")

        if body_offset < table_offset + entry_data_size:
            issues.append("✗ Body offset overlaps entry table")
        else:
            print("✓ Body offset doesn't overlap entry table")

        if issues:
            print("\nISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
        else:
            print("\n✓ No major issues detected in PKG structure")

        print(f"\n{'='*80}\n")


def compare_pkgs(pkg1_path: Path, pkg2_path: Path):
    """Compare two PKG files"""
    print(f"\n{'='*80}")
    print("COMPARING PKG FILES")
    print(f"{'='*80}\n")
    print(f"PKG 1: {pkg1_path.name}")
    print(f"PKG 2: {pkg2_path.name}\n")

    with open(pkg1_path, 'rb') as f1, open(pkg2_path, 'rb') as f2:
        header1 = f1.read(0x100)
        header2 = f2.read(0x100)

        print("Header Comparison (first 256 bytes):")
        for offset in range(0, 0x100, 16):
            bytes1 = header1[offset:offset+16]
            bytes2 = header2[offset:offset+16]

            if bytes1 != bytes2:
                print(f"  0x{offset:04X}: DIFFERENT")
                print(f"    PKG1: {bytes1.hex(' ')}")
                print(f"    PKG2: {bytes2.hex(' ')}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Analyze single PKG:  python analyze_pkg.py <pkg_file>")
        print("  Compare two PKGs:    python analyze_pkg.py <pkg1> <pkg2>")
        sys.exit(1)

    pkg1 = Path(sys.argv[1])
    if not pkg1.exists():
        print(f"Error: File not found: {pkg1}")
        sys.exit(1)

    analyze_pkg_header(pkg1)

    if len(sys.argv) > 2:
        pkg2 = Path(sys.argv[2])
        if pkg2.exists():
            print("\n" + "="*80 + "\n")
            analyze_pkg_header(pkg2)
            compare_pkgs(pkg1, pkg2)
