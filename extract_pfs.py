#!/usr/bin/env python3
"""
Extract PFS (PlayStation File System) image from PS4 PKG file
"""

import struct
from pathlib import Path


def extract_pfs_from_pkg(pkg_path: Path, output_path: Path):
    """Extract PFS image from PKG file"""

    with open(pkg_path, 'rb') as f:
        # Read PKG header
        header = f.read(0x1000)

        # Parse header
        magic = struct.unpack('>I', header[0x00:0x04])[0]
        if magic != 0x7F434E54:
            print(f"Invalid PKG magic: {magic:08X}")
            return False

        entry_count = struct.unpack('>I', header[0x10:0x14])[0]
        entry_table_offset = struct.unpack('>I', header[0x18:0x1C])[0]
        body_offset = struct.unpack('>Q', header[0x20:0x28])[0]
        body_size = struct.unpack('>Q', header[0x28:0x30])[0]

        print(f"PKG Header:")
        print(f"  Magic: {magic:08X}")
        print(f"  Entry count: {entry_count}")
        print(f"  Entry table offset: 0x{entry_table_offset:X}")
        print(f"  Body offset: 0x{body_offset:X}")
        print(f"  Body size: {body_size} bytes ({body_size/(1024*1024):.2f} MB)")

        # According to analysis, PFS starts at 0x80000 in all working PKGs
        pfs_offset = 0x80000

        # Get file size to determine PFS size
        f.seek(0, 2)  # End of file
        pkg_size = f.tell()
        pfs_size = pkg_size - pfs_offset

        print(f"\nPFS Image:")
        print(f"  Offset: 0x{pfs_offset:X}")
        print(f"  Size: {pfs_size} bytes ({pfs_size/(1024*1024):.2f} MB)")

        # Extract PFS
        f.seek(pfs_offset)
        pfs_data = f.read(pfs_size)

        # Write PFS to file
        with open(output_path, 'wb') as out:
            out.write(pfs_data)

        print(f"\nExtracted PFS to: {output_path}")

        # Analyze PFS header
        print(f"\nPFS Header (first 256 bytes):")
        print(f"  Magic/Signature: {pfs_data[:16].hex()}")

        # Check if it looks like a filesystem
        if b'PFS' in pfs_data[:256] or b'pfs' in pfs_data[:256]:
            print("  Found PFS signature!")
        else:
            print("  No clear PFS signature (may be encrypted)")

        return True


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: extract_pfs.py <input.pkg> [output_pfs.img]")
        sys.exit(1)

    pkg_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(pkg_path.stem + "_pfs.img")

    extract_pfs_from_pkg(pkg_path, output_path)
