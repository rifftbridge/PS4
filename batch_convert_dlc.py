#!/usr/bin/env python3
"""
Rocksmith PC to PS4 DLC Batch Converter
Converts multiple PC/Steam PSARC files to PS4 PKG format

Usage:
    python batch_convert_dlc.py input_folder output_folder

Requirements:
    - PkgTool.Core.exe from LibOrbisPkg in PATH or specify with --pkgtool
    - Python 3.7+
"""

import sys
import subprocess
from pathlib import Path
import argparse
import hashlib
from datetime import datetime


def generate_content_id(psarc_name: str) -> str:
    """Generate unique Content ID for DLC"""
    hash_obj = hashlib.md5(psarc_name.encode())
    unique_id = hash_obj.hexdigest()[:12].upper()
    return f"EP0001-CUSA00745_00-RS00{unique_id}"


def convert_single_dlc(psarc_file: Path, output_dir: Path, pkgtool_path: Path, converter_script: Path):
    """Convert a single PSARC to PKG"""

    print(f"\n{'='*60}")
    print(f"Converting: {psarc_file.name}")
    print(f"{'='*60}")

    # Extract song name from filename
    song_name = psarc_file.stem.replace('_', ' ').replace('-', ' - ')

    # Step 1: Run Python converter
    print("\n[1/2] Creating GP4 and param.sfo...")
    result = subprocess.run([
        sys.executable,
        str(converter_script),
        str(psarc_file),
        str(output_dir),
        song_name
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Conversion failed: {result.stderr}")
        return False

    # Find generated GP4 file
    gp4_files = list(output_dir.glob("*.gp4"))
    if not gp4_files:
        print("❌ No GP4 file generated")
        return False

    gp4_file = gp4_files[-1]  # Get most recent

    # Step 2: Build PKG with LibOrbisPkg
    print("\n[2/2] Building PKG with LibOrbisPkg...")
    result = subprocess.run([
        str(pkgtool_path),
        "pkg_build",
        str(gp4_file),
        str(output_dir)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ PKG build failed: {result.stderr}")
        return False

    # Find generated PKG
    pkg_files = list(output_dir.glob("*.pkg"))
    if not pkg_files:
        print("❌ No PKG file generated")
        return False

    pkg_file = max(pkg_files, key=lambda p: p.stat().st_mtime)
    pkg_size = pkg_file.stat().st_size / (1024 * 1024)

    # Rename PKG to human-readable format
    # Convert "Song Name by Artist" to "Artist-Song_Name_(PS4).pkg"
    clean_name = song_name.replace(' by ', '-').replace(' ', '_').replace('/', '_').replace('\\', '_')
    clean_name = ''.join(c for c in clean_name if c.isalnum() or c in '-_')
    new_pkg_name = f"{clean_name}_(PS4).pkg"
    new_pkg_path = output_dir / new_pkg_name

    # Rename the PKG
    pkg_file.rename(new_pkg_path)

    print(f"\n✅ Success: {new_pkg_name} ({pkg_size:.1f} MB)")

    # Clean up GP4 file
    gp4_file.unlink()

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Batch convert Rocksmith PC PSARC files to PS4 PKG format"
    )
    parser.add_argument("input_folder", type=Path, help="Folder containing PSARC files")
    parser.add_argument("output_folder", type=Path, help="Folder for output PKG files")
    parser.add_argument("--pkgtool", type=Path,
                       default=Path("C:/PS4/tools/LibOrbisPkg/PkgTool.Core.exe"),
                       help="Path to PkgTool.Core.exe")
    parser.add_argument("--converter", type=Path,
                       default=Path("rocksmith_pc_to_ps4_complete.py"),
                       help="Path to converter script")

    args = parser.parse_args()

    # Validate paths
    if not args.input_folder.exists():
        print(f"❌ Input folder not found: {args.input_folder}")
        return 1

    if not args.pkgtool.exists():
        print(f"❌ PkgTool.Core.exe not found: {args.pkgtool}")
        print("Please download LibOrbisPkg from: https://github.com/maxton/LibOrbisPkg/releases")
        return 1

    if not args.converter.exists():
        print(f"❌ Converter script not found: {args.converter}")
        return 1

    # Create output folder
    args.output_folder.mkdir(parents=True, exist_ok=True)

    # Find all PSARC files
    psarc_files = list(args.input_folder.glob("*.psarc"))

    if not psarc_files:
        print(f"❌ No PSARC files found in {args.input_folder}")
        return 1

    print(f"\n{'='*60}")
    print(f"Rocksmith PC to PS4 Batch Converter")
    print(f"{'='*60}")
    print(f"Found {len(psarc_files)} PSARC files")
    print(f"Output: {args.output_folder}")
    print(f"{'='*60}\n")

    # Convert each file
    success_count = 0
    failed_files = []

    for psarc_file in psarc_files:
        if convert_single_dlc(psarc_file, args.output_folder, args.pkgtool, args.converter):
            success_count += 1
        else:
            failed_files.append(psarc_file.name)

    # Summary
    print(f"\n{'='*60}")
    print(f"CONVERSION COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Success: {success_count}/{len(psarc_files)}")

    if failed_files:
        print(f"❌ Failed: {len(failed_files)}")
        for filename in failed_files:
            print(f"   - {filename}")

    print(f"\n📂 PKG files saved to: {args.output_folder}")
    print(f"\nCopy PKG files to USB: PS4\\PACKAGES\\")
    print(f"{'='*60}\n")

    return 0 if success_count == len(psarc_files) else 1


if __name__ == "__main__":
    sys.exit(main())
