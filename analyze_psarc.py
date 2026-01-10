#!/usr/bin/env python3
"""
PSARC Analyzer - Analyze structure of PSARC archive files
"""

import struct
import sys
from pathlib import Path


def analyze_psarc(psarc_path: Path):
    """Analyze PSARC file structure"""

    print(f"\n{'='*80}")
    print(f"PSARC ANALYZER: {psarc_path.name}")
    print(f"{'='*80}\n")

    with open(psarc_path, 'rb') as f:
        # Read magic (4 bytes)
        magic = f.read(4)

        if magic != b'PSAR':
            print(f"✗ ERROR: Not a valid PSARC file (magic: {magic})")
            return

        print(f"✓ Valid PSARC file (magic: {magic.decode('ascii')})\n")

        # Read header
        version_major = struct.unpack('>H', f.read(2))[0]
        version_minor = struct.unpack('>H', f.read(2))[0]
        compression_type = f.read(4).decode('ascii', errors='ignore').rstrip('\x00')
        toc_length = struct.unpack('>I', f.read(4))[0]
        toc_entry_size = struct.unpack('>I', f.read(4))[0]
        num_files = struct.unpack('>I', f.read(4))[0]
        block_size = struct.unpack('>I', f.read(4))[0]
        archive_flags = struct.unpack('>I', f.read(4))[0]

        print("HEADER INFORMATION:")
        print(f"  Version:         {version_major}.{version_minor}")
        print(f"  Compression:     {compression_type}")
        print(f"  TOC Length:      {toc_length} bytes")
        print(f"  TOC Entry Size:  {toc_entry_size} bytes")
        print(f"  Number of Files: {num_files}")
        print(f"  Block Size:      {block_size} bytes")
        print(f"  Archive Flags:   0x{archive_flags:08X} ({archive_flags})")

        # Check platform flags
        print(f"\nPLATFORM FLAGS:")
        if archive_flags == 0:
            print("  Platform: PC (flags = 0)")
        elif archive_flags == 4:
            print("  Platform: PS4/Mac (flags = 4)")
        else:
            print(f"  Platform: Unknown (flags = {archive_flags})")

        # File size
        file_size = psarc_path.stat().st_size
        print(f"\nFILE SIZE:")
        print(f"  Total Size:      {file_size} bytes ({file_size/(1024*1024):.2f} MB)")

        print(f"\n{'='*80}\n")


def compare_psarcs(psarc1_path: Path, psarc2_path: Path):
    """Compare two PSARC files"""
    print(f"\n{'='*80}")
    print("COMPARING PSARC FILES")
    print(f"{'='*80}\n")
    print(f"PSARC 1: {psarc1_path.name}")
    print(f"PSARC 2: {psarc2_path.name}\n")

    with open(psarc1_path, 'rb') as f1, open(psarc2_path, 'rb') as f2:
        # Read headers
        f1.read(4)  # magic
        f2.read(4)  # magic

        # Version
        v1_major = struct.unpack('>H', f1.read(2))[0]
        v1_minor = struct.unpack('>H', f1.read(2))[0]
        v2_major = struct.unpack('>H', f2.read(2))[0]
        v2_minor = struct.unpack('>H', f2.read(2))[0]

        # Compression
        comp1 = f1.read(4).decode('ascii', errors='ignore').rstrip('\x00')
        comp2 = f2.read(4).decode('ascii', errors='ignore').rstrip('\x00')

        # Skip TOC info
        f1.read(12)
        f2.read(12)

        # Flags
        flags1 = struct.unpack('>I', f1.read(4))[0]
        flags2 = struct.unpack('>I', f2.read(4))[0]

        print("DIFFERENCES:")
        if (v1_major, v1_minor) != (v2_major, v2_minor):
            print(f"  Version:     {v1_major}.{v1_minor} vs {v2_major}.{v2_minor}")
        else:
            print(f"  Version:     Same ({v1_major}.{v1_minor})")

        if comp1 != comp2:
            print(f"  Compression: {comp1} vs {comp2}")
        else:
            print(f"  Compression: Same ({comp1})")

        if flags1 != flags2:
            print(f"  Flags:       0x{flags1:08X} ({flags1}) vs 0x{flags2:08X} ({flags2})")
            print(f"               ^^ KEY DIFFERENCE! This determines platform ^^")
        else:
            print(f"  Flags:       Same (0x{flags1:08X})")

        print(f"\n{'='*80}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Analyze single PSARC:  python analyze_psarc.py <psarc_file>")
        print("  Compare two PSARCs:    python analyze_psarc.py <psarc1> <psarc2>")
        sys.exit(1)

    psarc1 = Path(sys.argv[1])
    if not psarc1.exists():
        print(f"Error: File not found: {psarc1}")
        sys.exit(1)

    analyze_psarc(psarc1)

    if len(sys.argv) > 2:
        psarc2 = Path(sys.argv[2])
        if psarc2.exists():
            print("\n")
            analyze_psarc(psarc2)
            compare_psarcs(psarc1, psarc2)
