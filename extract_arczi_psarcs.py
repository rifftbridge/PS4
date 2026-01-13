#!/usr/bin/env python3
"""
Extract PSARCs from working Arczi PKG files
These PSARCs are proven to work on PS4
"""

import subprocess
import sys
from pathlib import Path

def extract_psarc_from_pkg(pkg_path: Path, output_dir: Path):
    """Extract PSARC from PKG using LibOrbisPkg"""

    pkg_name = pkg_path.stem
    extract_dir = output_dir / f"{pkg_name}_extracted"

    print(f"\n{'='*60}")
    print(f"Extracting: {pkg_path.name}")
    print(f"{'='*60}")

    # Extract PKG using PkgTool
    extract_dir.mkdir(parents=True, exist_ok=True)

    # Use pkg_makegp4 to extract contents
    result = subprocess.run([
        "C:/PS4/tools/LibOrbisPkg/PkgTool.Core.exe",
        "pkg_makegp4",
        str(pkg_path),
        str(extract_dir)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ Extraction failed: {result.stderr}")
        return None

    # Find the extracted PSARC
    psarc_files = list(extract_dir.rglob("*.psarc"))

    if not psarc_files:
        print("❌ No PSARC found in extracted PKG")
        return None

    psarc_file = psarc_files[0]

    # Copy to output directory with clean name
    output_psarc = output_dir / psarc_file.name
    psarc_file.rename(output_psarc)

    # Clean up extraction directory
    import shutil
    shutil.rmtree(extract_dir)

    print(f"✅ Extracted: {output_psarc.name} ({output_psarc.stat().st_size / (1024*1024):.1f} MB)")

    return output_psarc


def main():
    samples_dir = Path("C:/PS4/samples")
    output_dir = Path("C:/PS4/arczi_extracted")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all Arczi PKGs
    arczi_pkgs = list(samples_dir.glob("*Arczi*.pkg"))

    if not arczi_pkgs:
        print("❌ No Arczi PKG files found in C:/PS4/samples/")
        return 1

    print(f"\n{'='*60}")
    print(f"Extracting PSARCs from {len(arczi_pkgs)} Arczi PKGs")
    print(f"{'='*60}")

    extracted = []

    for pkg_path in arczi_pkgs:
        psarc = extract_psarc_from_pkg(pkg_path, output_dir)
        if psarc:
            extracted.append(psarc)

    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"✅ Extracted {len(extracted)} PSARCs")
    print(f"📂 Location: {output_dir}")
    print(f"\nPSARC files:")
    for psarc in extracted:
        print(f"  - {psarc.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
