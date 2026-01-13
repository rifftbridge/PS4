#!/usr/bin/env python3
"""
Check if PKG has proper keystone file
Based on PS4DevWiki keystone documentation
"""

import sys
import struct
from pathlib import Path

def check_keystone_in_pkg(pkg_path: Path):
    """Check if PKG contains keystone file"""

    with open(pkg_path, 'rb') as f:
        # Read PKG header
        magic = f.read(4)
        if magic != b'\x7fCNT':
            print(f"❌ Not a valid PKG file (magic: {magic})")
            return False

        print(f"✅ Valid PKG magic: {magic}")

        # Skip to entry table
        f.seek(0x18)
        num_entries = struct.unpack('>I', f.read(4))[0]

        print(f"Entries: {num_entries}")

        # Read entry table
        f.seek(0x20)

        found_keystone = False

        for i in range(num_entries):
            entry_offset = 0x20 + (i * 0x20)
            f.seek(entry_offset)

            entry_id = struct.unpack('>I', f.read(4))[0]
            entry_name_offset = struct.unpack('>I', f.read(4))[0]
            entry_data_offset = struct.unpack('>I', f.read(4))[0]
            entry_data_size = struct.unpack('>I', f.read(4))[0]

            # Entry ID 0x100 = DIGESTS
            # Entry ID 0x110 = ENTRY_KEYS
            # Entry ID 0x140 = KEYSTONE (?)

            if entry_id == 0x140:
                print(f"✅ Found potential keystone entry at offset 0x{entry_data_offset:x}")

                # Read keystone data
                f.seek(entry_data_offset)
                keystone_data = f.read(min(96, entry_data_size))

                # Check keystone magic
                if keystone_data[:8] == b'keystone':
                    print(f"✅ Valid keystone magic found!")
                    print(f"   Keystone size: {entry_data_size} bytes")
                    print(f"   Expected size: 96 bytes")
                    found_keystone = True
                else:
                    print(f"⚠️  Entry 0x140 found but no keystone magic")
                    print(f"   First 16 bytes: {keystone_data[:16].hex()}")

        if not found_keystone:
            print("❌ No keystone file found in PKG!")
            print("   This might cause CE-34707-1 signature errors")

        return found_keystone

def main():
    if len(sys.argv) < 2:
        print("PKG Keystone Checker")
        print("="*60)
        print()
        print("Usage: python check_keystone.py <pkg_file>")
        print()
        print("Checks if PKG contains proper keystone file")
        sys.exit(1)

    pkg_path = Path(sys.argv[1])

    if not pkg_path.exists():
        print(f"ERROR: PKG file not found: {pkg_path}")
        sys.exit(1)

    print(f"Analyzing: {pkg_path}")
    print("="*60)
    print()

    has_keystone = check_keystone_in_pkg(pkg_path)

    print()
    print("="*60)
    if has_keystone:
        print("✅ PKG has keystone - signature should be OK")
    else:
        print("❌ PKG missing keystone - might fail with CE-34707-1")
    print("="*60)

if __name__ == '__main__':
    main()
