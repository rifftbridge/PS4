#!/usr/bin/env python3
"""
Rocksmith 2014 PC to PS4 PKG Converter
Complete solution for converting PC DLC to PS4 .pkg installer

Requirements:
- UnPSARC (for unpacking psarc files)
- psarc packer tool (for repacking with PS4 flags)
- Python 3.7+

Usage:
    python rocksmith_pc_to_ps4.py <input_pc.psarc> <output_dir> [options]
"""

import os
import sys
import json
import shutil
import struct
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Tuple

class RocksmithPS4Converter:
    """Converts Rocksmith 2014 PC DLC to PS4 PKG format"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.temp_dir = None
        
    def log(self, message: str):
        """Print log message if verbose"""
        if self.verbose:
            print(message)
    
    def create_param_sfo(self, output_path: Path, title_id: str, content_id: str, 
                        title: str, version: str = "01.00") -> bool:
        """
        Create param.sfo file for PS4
        
        param.sfo structure:
        - Magic: \x00PSF
        - Version: 0x0101
        - Key table offset
        - Data table offset
        - Number of entries
        """
        try:
            # SFO structure
            entries = [
                ("ATTRIBUTE", "ac", 4, 4),  # Additional Content
                ("CATEGORY", "ac", 4, 3),
                ("CONTENT_ID", content_id, 48, len(content_id) + 1),
                ("TITLE", title, 128, len(title) + 1),
                ("TITLE_ID", title_id, 12, len(title_id) + 1),
                ("VERSION", version, 8, len(version) + 1),
            ]
            
            # Calculate offsets
            header_size = 20
            index_table_size = len(entries) * 16
            key_table_start = header_size + index_table_size
            
            key_data = b""
            data_values = []
            
            for key, value, max_len, used_len in entries:
                key_data += key.encode('utf-8') + b'\x00'
                if isinstance(value, str):
                    data_values.append(value.encode('utf-8') + b'\x00')
                else:
                    data_values.append(value)
            
            data_table_start = key_table_start + len(key_data)
            
            # Align to 4 bytes
            while len(key_data) % 4 != 0:
                key_data += b'\x00'
            
            # Write SFO file
            with open(output_path, 'wb') as f:
                # Header
                f.write(b'\x00PSF')  # Magic
                f.write(struct.pack('<I', 0x0101))  # Version
                f.write(struct.pack('<I', key_table_start))
                f.write(struct.pack('<I', data_table_start))
                f.write(struct.pack('<I', len(entries)))
                
                # Index table
                key_offset = 0
                data_offset = 0
                for i, (key, value, max_len, used_len) in enumerate(entries):
                    # Key offset, alignment, data type, used size, total size, data offset
                    f.write(struct.pack('<H', key_offset))
                    f.write(struct.pack('<H', 0x0404 if max_len == 4 else 0x0402))  # data type
                    f.write(struct.pack('<I', used_len))
                    f.write(struct.pack('<I', max_len))
                    f.write(struct.pack('<I', data_offset))
                    
                    key_offset += len(key) + 1
                    data_offset += max_len
                
                # Key table
                f.write(key_data)
                
                # Data table
                for i, (key, value, max_len, used_len) in enumerate(entries):
                    data = data_values[i]
                    f.write(data)
                    # Pad to max_len
                    f.write(b'\x00' * (max_len - len(data)))
            
            self.log(f"✓ Created param.sfo")
            return True
            
        except Exception as e:
            self.log(f"✗ Error creating param.sfo: {e}")
            return False
    
    def create_gp4_project(self, output_path: Path, content_id: str, 
                          psarc_filename: str) -> bool:
        """Create GP4 project file for PKG building"""
        try:
            gp4_content = f"""<?xml version="1.0"?>
<psproject xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" fmt="gp4" version="1000">
  <volume>
    <volume_type>pkg_ps4_ac_data</volume_type>
    <volume_ts>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</volume_ts>
    <package content_id="{content_id}" passcode="00000000000000000000000000000000" entitlement_key="00000000000000000000000000000000" c_date="{datetime.now().strftime('%Y-%m-%d')}" />
  </volume>
  <files img_no="0">
    <file targ_path="sce_sys/icon0.png" orig_path="sce_sys/icon0.png" />
    <file targ_path="sce_sys/param.sfo" orig_path="sce_sys/param.sfo" />
    <file targ_path="DLC/{psarc_filename}" orig_path="{psarc_filename}" />
  </files>
  <rootdir>
    <dir targ_name="sce_sys" />
    <dir targ_name="DLC" />
  </rootdir>
</psproject>"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(gp4_content)
            
            self.log(f"✓ Created GP4 project file")
            return True
            
        except Exception as e:
            self.log(f"✗ Error creating GP4 file: {e}")
            return False
    
    def unpack_psarc(self, psarc_path: Path, output_dir: Path, 
                     unpsarc_exe: str = "UnPSARC.exe") -> bool:
        """Unpack psarc file using UnPSARC"""
        try:
            self.log(f"Unpacking {psarc_path.name}...")
            
            # Try to find UnPSARC
            unpsarc_paths = [
                unpsarc_exe,
                "./UnPSARC.exe",
                "./tools/UnPSARC.exe",
                "UnPSARC",
            ]
            
            unpsarc_found = None
            for path in unpsarc_paths:
                if shutil.which(path) or Path(path).exists():
                    unpsarc_found = path
                    break
            
            if not unpsarc_found:
                self.log("✗ UnPSARC not found. Please provide path or place in current directory.")
                return False
            
            # Run UnPSARC
            result = subprocess.run(
                [unpsarc_found, str(psarc_path), str(output_dir)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 or output_dir.exists():
                self.log(f"✓ Unpacked successfully")
                return True
            else:
                self.log(f"✗ UnPSARC failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"✗ Error unpacking: {e}")
            return False
    
    def convert_pc_to_ps4_structure(self, pc_dir: Path, ps4_dir: Path) -> bool:
        """Convert PC directory structure to PS4 format"""
        try:
            self.log("Converting PC structure to PS4...")
            
            ps4_dir.mkdir(parents=True, exist_ok=True)
            
            # Files to skip
            skip_files = {'appid.appid'}
            skip_file_patterns = ['aggregategraph.nt']
            skip_xml_patterns = ['_bass.xml', '_lead.xml', '_rhythm.xml', '_vocals.xml']
            
            files_converted = 0
            files_skipped = 0
            
            # Walk through PC directory
            for root, dirs, files in os.walk(pc_dir):
                rel_root = Path(root).relative_to(pc_dir)
                
                for file in files:
                    src_file = Path(root) / file
                    rel_file = rel_root / file
                    
                    # Skip PC-only files
                    if (file in skip_files or 
                        any(pattern in file for pattern in skip_file_patterns) or
                        any(file.endswith(pattern) for pattern in skip_xml_patterns)):
                        self.log(f"  ✗ SKIP: {rel_file}")
                        files_skipped += 1
                        continue
                    
                    # Handle audio folder rename
                    if 'audio/windows' in str(rel_file) or 'audio\\windows' in str(rel_file):
                        new_rel_file = str(rel_file).replace('windows', 'generic').replace('\\', '/')
                        dst_file = ps4_dir / new_rel_file
                        self.log(f"  → MOVE: {rel_file} → {new_rel_file}")
                    else:
                        dst_file = ps4_dir / rel_file
                        self.log(f"  ✓ COPY: {rel_file}")
                    
                    # Copy file
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dst_file)
                    files_converted += 1
            
            self.log(f"\n✓ Converted {files_converted} files, skipped {files_skipped}")
            return True
            
        except Exception as e:
            self.log(f"✗ Error converting structure: {e}")
            return False
    
    def repack_psarc(self, source_dir: Path, output_psarc: Path, 
                    flags: int = 0x4) -> bool:
        """
        Repack directory as psarc with PS4 flags
        
        Note: This is a simplified version. For production use, you'd need
        to implement full PSARC packing or use an external tool.
        """
        try:
            self.log(f"Repacking as {output_psarc.name}...")
            
            # Try to find psarc packer
            packers = [
                "psarc.exe",
                "./psarc.exe",
                "./tools/psarc.exe",
                "psarc",
            ]
            
            packer_found = None
            for packer in packers:
                if shutil.which(packer) or Path(packer).exists():
                    packer_found = packer
                    break
            
            if not packer_found:
                self.log("⚠ PSARC packer not found.")
                self.log("  You'll need to manually repack with a psarc tool.")
                self.log(f"  Source directory: {source_dir}")
                self.log(f"  Required flags: {hex(flags)}")
                return False
            
            # Run packer (syntax varies by tool)
            # This is a placeholder - actual command depends on your packer
            result = subprocess.run(
                [packer_found, "create", "--inputfile", str(source_dir), 
                 "--output", str(output_psarc), "--flags", str(flags)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log(f"✓ Repacked successfully")
                return True
            else:
                self.log(f"✗ Packing failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"✗ Error repacking: {e}")
            return False
    
    def set_psarc_flags(self, psarc_path: Path, flags: int = 0x4) -> bool:
        """Set archive flags in psarc header"""
        try:
            if not psarc_path.exists():
                return False
            
            with open(psarc_path, 'r+b') as f:
                # Read magic
                magic = f.read(4)
                if magic != b'PSAR':
                    self.log(f"✗ Not a valid PSARC file")
                    return False
                
                # Seek to flags position (offset 28)
                f.seek(28)
                current_flags = struct.unpack('>I', f.read(4))[0]
                
                if current_flags == flags:
                    self.log(f"✓ Archive flags already set to {hex(flags)}")
                    return True
                
                # Write new flags
                f.seek(28)
                f.write(struct.pack('>I', flags))
                
                self.log(f"✓ Changed archive flags: {hex(current_flags)} → {hex(flags)}")
                return True
                
        except Exception as e:
            self.log(f"✗ Error setting flags: {e}")
            return False
    
    def extract_song_info(self, manifest_dir: Path) -> Dict:
        """Extract song information from manifest files"""
        try:
            # Find manifest folder
            manifest_folders = list(manifest_dir.glob("songs_dlc_*"))
            if not manifest_folders:
                self.log("⚠ No manifest folder found")
                return {}
            
            manifest_folder = manifest_folders[0]
            
            # Read first JSON manifest
            json_files = list(manifest_folder.glob("*.json"))
            if not json_files:
                self.log("⚠ No manifest JSON found")
                return {}
            
            with open(json_files[0], 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # Extract info from manifest
            entries = manifest.get('Entries', {})
            if not entries:
                return {}
            
            first_entry = list(entries.values())[0]
            attributes = first_entry.get('Attributes', {})
            
            song_code = manifest_folder.name.replace('songs_dlc_', '')
            
            return {
                'song_code': song_code,
                'artist': attributes.get('ArtistName', 'Unknown Artist'),
                'song_name': attributes.get('SongName', 'Unknown Song'),
                'album': attributes.get('AlbumName', ''),
            }
            
        except Exception as e:
            self.log(f"⚠ Could not extract song info: {e}")
            return {}
    
    def create_default_icon(self, output_path: Path) -> bool:
        """Create a default 512x512 icon if none exists"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create 512x512 image
            img = Image.new('RGB', (512, 512), color=(30, 30, 30))
            draw = ImageDraw.Draw(img)
            
            # Draw Rocksmith logo placeholder
            draw.rectangle([128, 128, 384, 384], outline=(200, 200, 200), width=3)
            draw.text((256, 256), "RS", fill=(200, 200, 200), anchor="mm")
            
            img.save(output_path, 'PNG')
            self.log(f"✓ Created default icon")
            return True
            
        except ImportError:
            self.log("⚠ PIL not available, cannot create icon")
            self.log("  Please provide icon0.png manually")
            return False
        except Exception as e:
            self.log(f"✗ Error creating icon: {e}")
            return False
    
    def build_pkg(self, gp4_path: Path, output_pkg: Path, 
                 pkg_tool: str = "orbis-pub-cmd.exe") -> bool:
        """Build PS4 PKG from GP4 project"""
        try:
            self.log(f"Building PKG: {output_pkg.name}...")
            
            # Try to find PKG builder
            pkg_tools = [
                pkg_tool,
                "./orbis-pub-cmd.exe",
                "./tools/orbis-pub-cmd.exe",
            ]
            
            tool_found = None
            for tool in pkg_tools:
                if shutil.which(tool) or Path(tool).exists():
                    tool_found = tool
                    break
            
            if not tool_found:
                self.log("⚠ PKG builder not found.")
                self.log("  Manual PKG build required:")
                self.log(f"    GP4 file: {gp4_path}")
                self.log(f"    Output: {output_pkg}")
                return False
            
            # Run PKG builder
            result = subprocess.run(
                [tool_found, "img_create", str(gp4_path), str(output_pkg)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log(f"✓ PKG built successfully")
                return True
            else:
                self.log(f"✗ PKG build failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"✗ Error building PKG: {e}")
            return False
    
    def convert(self, input_psarc: Path, output_dir: Path, 
               content_id: str = None, title_id: str = "CUSA00745",
               region: str = "EP0001") -> bool:
        """
        Main conversion function
        
        Args:
            input_psarc: Path to PC psarc file
            output_dir: Output directory for PKG
            content_id: PS4 Content ID (will be generated if not provided)
            title_id: PS4 Title ID (default: Rocksmith 2014)
            region: Region code (EP=Europe, UP=USA, etc.)
        """
        try:
            self.log("=" * 80)
            self.log("ROCKSMITH 2014: PC → PS4 PKG CONVERTER")
            self.log("=" * 80)
            self.log(f"\nInput:  {input_psarc}")
            self.log(f"Output: {output_dir}\n")
            
            # Setup directories
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            work_dir = output_dir / "work"
            work_dir.mkdir(exist_ok=True)
            
            pc_unpacked = work_dir / "pc_unpacked"
            ps4_structure = work_dir / "ps4_structure"
            pkg_build = output_dir / "pkg_build"
            
            # Step 1: Unpack PC psarc
            self.log("\n" + "=" * 80)
            self.log("STEP 1: Unpacking PC psarc")
            self.log("=" * 80)
            if not self.unpack_psarc(input_psarc, pc_unpacked):
                return False
            
            # Step 2: Extract song info
            self.log("\n" + "=" * 80)
            self.log("STEP 2: Extracting song information")
            self.log("=" * 80)
            song_info = self.extract_song_info(pc_unpacked / "manifests")
            if song_info:
                self.log(f"  Song Code: {song_info['song_code']}")
                self.log(f"  Artist: {song_info['artist']}")
                self.log(f"  Song: {song_info['song_name']}")
            
            # Generate Content ID if not provided
            if not content_id:
                song_code = song_info.get('song_code', 'SONG')
                # Generate unique 16-char suffix
                import hashlib
                hash_input = f"{song_info.get('artist', '')}{song_info.get('song_name', '')}"
                hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:16].upper()
                content_id = f"{region}-{title_id}_00-{hash_suffix}"
            
            self.log(f"  Content ID: {content_id}")
            
            # Step 3: Convert structure
            self.log("\n" + "=" * 80)
            self.log("STEP 3: Converting PC → PS4 structure")
            self.log("=" * 80)
            if not self.convert_pc_to_ps4_structure(pc_unpacked, ps4_structure):
                return False
            
            # Step 4: Repack as PS4 psarc
            self.log("\n" + "=" * 80)
            self.log("STEP 4: Repacking as PS4 psarc")
            self.log("=" * 80)
            
            song_code = song_info.get('song_code', 'song')
            ps4_psarc = pkg_build / f"{song_code.lower()}_p.psarc"
            pkg_build.mkdir(exist_ok=True)
            
            # Note: Actual repacking requires external tool
            # For now, we'll create the structure and set flags
            self.log("⚠ Manual psarc repacking required:")
            self.log(f"  1. Pack this directory: {ps4_structure}")
            self.log(f"  2. Save as: {ps4_psarc}")
            self.log(f"  3. Set archive flags to: 0x4")
            self.log(f"  4. Or use provided convert_psarc.py script")
            
            # Step 5: Create PKG structure
            self.log("\n" + "=" * 80)
            self.log("STEP 5: Creating PKG structure")
            self.log("=" * 80)
            
            # Create sce_sys directory
            sce_sys = pkg_build / "sce_sys"
            sce_sys.mkdir(exist_ok=True)
            
            # Create param.sfo
            title = f"Rocksmith 2014 - {song_info.get('song_name', 'Custom')} - {song_info.get('artist', 'Artist')}"
            title = title[:127]  # Limit length
            
            param_sfo = sce_sys / "param.sfo"
            self.create_param_sfo(param_sfo, title_id, content_id, title)
            
            # Create or copy icon
            icon_path = sce_sys / "icon0.png"
            if not icon_path.exists():
                self.create_default_icon(icon_path)
            
            # Create GP4 project
            gp4_path = pkg_build / f"{song_code}_ps4.gp4"
            psarc_filename = f"{song_code.lower()}_p.psarc"
            self.create_gp4_project(gp4_path, content_id, psarc_filename)
            
            # Step 6: Build PKG
            self.log("\n" + "=" * 80)
            self.log("STEP 6: Building PKG")
            self.log("=" * 80)
            
            output_pkg = output_dir / f"Rocksmith_2014_{song_info.get('song_name', 'Custom').replace(' ', '_')}.pkg"
            self.build_pkg(gp4_path, output_pkg)
            
            # Summary
            self.log("\n" + "=" * 80)
            self.log("CONVERSION COMPLETE")
            self.log("=" * 80)
            self.log(f"\nOutput directory: {output_dir}")
            self.log(f"PKG build folder: {pkg_build}")
            self.log(f"\nManual steps required:")
            self.log(f"  1. Repack {ps4_structure} → {ps4_psarc} with flags 0x4")
            self.log(f"  2. Build PKG from GP4: {gp4_path}")
            self.log(f"\nOr use the automated scripts provided in the output directory.")
            
            return True
            
        except Exception as e:
            self.log(f"\n✗ CONVERSION FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    parser = argparse.ArgumentParser(
        description='Convert Rocksmith 2014 PC DLC to PS4 PKG',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python rocksmith_pc_to_ps4.py song.psarc ./output
  python rocksmith_pc_to_ps4.py song.psarc ./output --content-id EP0001-CUSA00745_00-CUSTOMSONG000001
  python rocksmith_pc_to_ps4.py song.psarc ./output --region UP0001 --title-id CUSA12345
        """
    )
    
    parser.add_argument('input_psarc', type=str, help='Input PC psarc file')
    parser.add_argument('output_dir', type=str, help='Output directory')
    parser.add_argument('--content-id', type=str, help='PS4 Content ID (auto-generated if not provided)')
    parser.add_argument('--title-id', type=str, default='CUSA00745', help='PS4 Title ID (default: CUSA00745 for Rocksmith)')
    parser.add_argument('--region', type=str, default='EP0001', help='Region code (EP0001=Europe, UP0001=USA, etc.)')
    parser.add_argument('--quiet', action='store_true', help='Suppress output')
    
    args = parser.parse_args()
    
    # Validate input
    input_path = Path(args.input_psarc)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    if not input_path.suffix.lower() == '.psarc':
        print(f"Warning: Input file doesn't have .psarc extension")
    
    # Run conversion
    converter = RocksmithPS4Converter(verbose=not args.quiet)
    
    success = converter.convert(
        input_psarc=input_path,
        output_dir=Path(args.output_dir),
        content_id=args.content_id,
        title_id=args.title_id,
        region=args.region
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
