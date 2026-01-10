#!/usr/bin/env python3
"""
Detailed analysis of PKG entries - extract all entry data
"""

import struct
from pathlib import Path


ENTRY_NAMES = {
    0x0001: "DIGESTS",
    0x0010: "ENTRY_KEYS",
    0x0020: "IMAGE_KEY",
    0x0080: "GENERAL_DIGESTS",
    0x0100: "METAS",
    0x0200: "ENTRY_NAMES",
    0x0400: "LICENSE",
    0x0401: "LICENSE_INFO",
    0x0402: "UNKNOWN_0402",
    0x0409: "PSRESERVED",
    0x1000: "PARAM_SFO",
    0x1200: "ICON0_PNG",
}


def analyze_pkg_entries(pkg_path: Path, extract_dir: Path = None):
    """Analyze and extract all PKG entries"""

    if extract_dir:
        extract_dir.mkdir(parents=True, exist_ok=True)

    with open(pkg_path, 'rb') as f:
        # Read header
        header = f.read(0x1000)

        magic = struct.unpack('>I', header[0x00:0x04])[0]
        pkg_type = struct.unpack('>I', header[0x04:0x08])[0]
        entry_count = struct.unpack('>I', header[0x10:0x14])[0]
        entry_table_offset = struct.unpack('>I', header[0x18:0x1C])[0]
        entry_table_size = struct.unpack('>I', header[0x1C:0x20])[0]
        body_offset = struct.unpack('>Q', header[0x20:0x28])[0]
        body_size = struct.unpack('>Q', header[0x28:0x30])[0]

        content_id = header[0x40:0x64].decode('ascii', errors='ignore').rstrip('\x00')

        drm_type = struct.unpack('>I', header[0x70:0x74])[0]
        content_type = struct.unpack('>I', header[0x74:0x78])[0]
        content_flags = struct.unpack('>I', header[0x78:0x7C])[0]

        print("="*80)
        print(f"PKG: {pkg_path.name}")
        print("="*80)
        print(f"Content ID: {content_id}")
        print(f"DRM Type: 0x{drm_type:08X}")
        print(f"Content Type: 0x{content_type:08X}")
        print(f"Content Flags: 0x{content_flags:08X}")
        print(f"\nStructure:")
        print(f"  Entry count: {entry_count}")
        print(f"  Entry table: 0x{entry_table_offset:X} ({entry_table_size} bytes)")
        print(f"  Body: 0x{body_offset:X} ({body_size} bytes)")

        # Read entry table
        f.seek(entry_table_offset)
        entries = []

        for i in range(entry_count):
            entry_data = f.read(32)
            entry_id = struct.unpack('>I', entry_data[0:4])[0]
            name_offset = struct.unpack('>I', entry_data[4:8])[0]
            flags1 = struct.unpack('>I', entry_data[8:12])[0]
            flags2 = struct.unpack('>I', entry_data[12:16])[0]
            file_offset = struct.unpack('>I', entry_data[16:20])[0]
            file_size = struct.unpack('>I', entry_data[20:24])[0]

            entries.append({
                'id': entry_id,
                'name': ENTRY_NAMES.get(entry_id, f"UNKNOWN_{entry_id:04X}"),
                'name_offset': name_offset,
                'flags1': flags1,
                'flags2': flags2,
                'offset': file_offset,
                'size': file_size
            })

        # Display entries
        print(f"\nEntries ({len(entries)}):")
        print(f"{'ID':<6} {'Name':<20} {'Offset':<12} {'Size':<10} {'Flags1':<12} {'Flags2':<12}")
        print("-"*80)

        for entry in entries:
            print(f"0x{entry['id']:04X} {entry['name']:<20} "
                  f"0x{entry['offset']:08X}  {entry['size']:<10} "
                  f"0x{entry['flags1']:08X}  0x{entry['flags2']:08X}")

        # Extract entry data
        if extract_dir:
            print(f"\nExtracting entries to: {extract_dir}")

            for entry in entries:
                f.seek(entry['offset'])
                data = f.read(entry['size'])

                filename = f"{entry['id']:04X}_{entry['name']}.bin"
                output_path = extract_dir / filename

                with open(output_path, 'wb') as out:
                    out.write(data)

                # Show first bytes
                preview = data[:32].hex() if len(data) >= 32 else data.hex()
                print(f"  {filename}: {entry['size']} bytes - {preview}...")

        # Calculate what's after the body
        body_end = body_offset + body_size
        f.seek(0, 2)
        pkg_size = f.tell()
        remaining = pkg_size - body_end

        print(f"\nPost-body data:")
        print(f"  Body ends at: 0x{body_end:X}")
        print(f"  Remaining: {remaining} bytes ({remaining/(1024*1024):.2f} MB)")
        print(f"  This is likely the PFS image")

        return entries


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: analyze_pkg_entries.py <input.pkg> [extract_dir]")
        sys.exit(1)

    pkg_path = Path(sys.argv[1])
    extract_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(f"{pkg_path.stem}_entries")

    analyze_pkg_entries(pkg_path, extract_dir)
