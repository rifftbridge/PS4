#!/usr/bin/env python3
"""
Convert PS4-format PSARC (flags=4) to PC-format PSARC (flags=0)
This extracts the encrypted PSARC and rebuilds it in PC format
"""

import struct
import sys
from pathlib import Path

def convert_psarc_format(input_path: Path, output_path: Path):
    """
    Convert PSARC from PS4 format (flags=4) to PC format (flags=0)
    Simply changes the ArchiveFlags byte from 4 to 0
    """

    print(f"Reading: {input_path}")

    with open(input_path, 'rb') as f:
        data = bytearray(f.read())

    # Check magic number
    magic = data[0:4]
    if magic != b'PSAR':
        print(f"ERROR: Not a valid PSARC file (magic: {magic})")
        return False

    # Read current flags (offset 0x1C = 28)
    current_flags = struct.unpack('>I', data[28:32])[0]

    print(f"Current ArchiveFlags: 0x{current_flags:08x} ({current_flags})")

    if current_flags == 0:
        print("Already in PC format (flags=0)")
        print("No conversion needed, copying file...")
        with open(output_path, 'wb') as f:
            f.write(data)
        return True

    if current_flags == 4:
        print("Converting from PS4/Mac format (flags=4) to PC format (flags=0)...")

        # Change ArchiveFlags from 4 to 0
        struct.pack_into('>I', data, 28, 0)

        # Write converted file
        with open(output_path, 'wb') as f:
            f.write(data)

        # Verify
        with open(output_path, 'rb') as f:
            f.seek(28)
            new_flags = struct.unpack('>I', f.read(4))[0]

        print(f"New ArchiveFlags: 0x{new_flags:08x} ({new_flags})")
        print(f"✅ Successfully converted to PC format!")
        print(f"Output: {output_path}")
        return True

    else:
        print(f"WARNING: Unknown ArchiveFlags value: {current_flags}")
        print("Proceeding anyway, changing to 0...")

        struct.pack_into('>I', data, 28, 0)

        with open(output_path, 'wb') as f:
            f.write(data)

        return True

def main():
    if len(sys.argv) < 2:
        print("PSARC Format Converter - PS4/Mac to PC")
        print("="*60)
        print()
        print("Usage: python convert_psarc_to_pc_format.py <input.psarc> [output.psarc]")
        print()
        print("Converts PSARC from PS4/Mac format (flags=4) to PC format (flags=0)")
        print()
        print("Example:")
        print("  python convert_psarc_to_pc_format.py cooppois_p.psarc cooppois_pc.psarc")
        print()
        sys.exit(1)

    input_path = Path(sys.argv[1])

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        sys.exit(1)

    # Default output name
    if len(sys.argv) > 2:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.parent / (input_path.stem + "_pc.psarc")

    success = convert_psarc_format(input_path, output_path)

    if success:
        print()
        print("="*60)
        print("CONVERSION COMPLETE!")
        print("="*60)
        print()
        print(f"You can now use {output_path.name} in your PKG conversion:")
        print(f"  python rocksmith_pc_to_ps4_complete.py {output_path.name} output_dir \"Song Title\"")
        print()
    else:
        print("Conversion failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
