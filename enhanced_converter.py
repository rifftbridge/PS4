#!/usr/bin/env python3
"""
Enhanced Rocksmith PC to PS4 Converter with Steam DLC Integration

This version can:
- Auto-detect Steam App IDs from PC psarc files
- Fetch DLC information from Steam
- Generate accurate Content IDs based on Steam data
- Create better titles and metadata
"""

import sys
import struct
from pathlib import Path
from typing import Optional

# Import the base converter
try:
    from rocksmith_pc_to_ps4 import RocksmithPS4Converter
    from steam_dlc_database import SteamDLCDatabase
except ImportError:
    print("Error: Make sure rocksmith_pc_to_ps4.py and steam_dlc_database.py are in the same directory")
    sys.exit(1)

# Import Python PKG builder
try:
    from ps4_pkg_builder import build_pkg_from_gp4
    HAS_PYTHON_PKG_BUILDER = True
except ImportError:
    HAS_PYTHON_PKG_BUILDER = False
    build_pkg_from_gp4 = None

class EnhancedRocksmithConverter(RocksmithPS4Converter):
    """Enhanced converter with Steam DLC database integration"""
    
    def __init__(self, verbose: bool = True, use_steam_db: bool = True):
        super().__init__(verbose)
        self.use_steam_db = use_steam_db
        self.steam_db = SteamDLCDatabase() if use_steam_db else None
    
    def detect_steam_app_id(self, pc_unpacked_dir: Path) -> Optional[int]:
        """
        Detect Steam App ID from unpacked PC psarc
        
        The appid.appid file contains the Steam App ID
        """
        try:
            appid_file = pc_unpacked_dir / "appid.appid"
            
            if not appid_file.exists():
                self.log("⚠ No appid.appid file found")
                return None
            
            with open(appid_file, 'r') as f:
                app_id_str = f.read().strip()
                app_id = int(app_id_str)
                
                self.log(f"✓ Detected Steam App ID: {app_id}")
                return app_id
                
        except Exception as e:
            self.log(f"⚠ Could not detect Steam App ID: {e}")
            return None
    
    def get_enhanced_metadata(self, app_id: int, fallback_info: dict) -> dict:
        """Get enhanced metadata from Steam DB with fallback to manifest data"""
        
        if not self.steam_db:
            return fallback_info
        
        # Try to get from cache first
        steam_info = self.steam_db.find_by_app_id(app_id)
        
        if not steam_info:
            self.log(f"  Fetching Steam data for App ID {app_id}...")
            self.steam_db.add_dlc(app_id)
            steam_info = self.steam_db.find_by_app_id(app_id)
        
        if steam_info:
            self.log(f"✓ Using Steam data: {steam_info['artist']} - {steam_info['song']}")
            
            # Merge Steam data with fallback
            return {
                'app_id': app_id,
                'song_code': fallback_info.get('song_code', ''),
                'artist': steam_info.get('artist') or fallback_info.get('artist', 'Unknown Artist'),
                'song_name': steam_info.get('song') or fallback_info.get('song_name', 'Unknown Song'),
                'album': fallback_info.get('album', ''),
                'steam_name': steam_info.get('name', ''),
                'release_date': steam_info.get('release_date', ''),
            }
        else:
            self.log("⚠ Steam data not available, using manifest data")
            return fallback_info
    
    def generate_steam_content_id(self, app_id: int, region: str, title_id: str) -> str:
        """
        Generate Content ID based on Steam App ID
        
        Format: REGION-TITLEID_00-APPID00000000000
        """
        # Convert app_id to 16-character suffix
        app_id_str = str(app_id)
        suffix = f"APPID{app_id_str}".ljust(16, '0')[:16]
        
        content_id = f"{region}-{title_id}_00-{suffix}"
        
        self.log(f"  Generated Content ID from App ID: {content_id}")
        return content_id
    
    def convert_enhanced(self, input_psarc: Path, output_dir: Path,
                        content_id: str = None, title_id: str = "CUSA00745",
                        region: str = "EP0001", auto_steam: bool = True,
                        build_pkg: bool = True, pkg_tool: Path = None) -> bool:
        """
        Enhanced conversion with Steam DLC integration
        
        Args:
            input_psarc: Path to PC psarc file
            output_dir: Output directory
            content_id: Custom Content ID (will auto-generate if not provided)
            title_id: PS4 Title ID
            region: Region code
            auto_steam: Auto-detect and use Steam App ID
            build_pkg: Whether to build final .pkg file (requires PkgTool.exe or orbis-pub-cmd.exe)
            pkg_tool: Path to PKG building tool (optional, will search if not provided)
        """
        try:
            self.log("=" * 80)
            self.log("ROCKSMITH 2014: ENHANCED PC → PS4 CONVERTER")
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
            
            # Step 2: Detect Steam App ID
            app_id = None
            if auto_steam and self.use_steam_db:
                self.log("\n" + "=" * 80)
                self.log("STEP 2: Detecting Steam App ID")
                self.log("=" * 80)
                app_id = self.detect_steam_app_id(pc_unpacked)
            
            # Step 3: Extract and enhance song info
            self.log("\n" + "=" * 80)
            self.log("STEP 3: Extracting song information")
            self.log("=" * 80)
            
            # Get basic info from manifest
            manifest_info = self.extract_song_info(pc_unpacked / "manifests")
            
            # Enhance with Steam data if available
            if app_id and self.use_steam_db:
                song_info = self.get_enhanced_metadata(app_id, manifest_info)
            else:
                song_info = manifest_info
            
            if song_info:
                self.log(f"  Song Code: {song_info.get('song_code', 'N/A')}")
                self.log(f"  Artist: {song_info.get('artist', 'N/A')}")
                self.log(f"  Song: {song_info.get('song_name', 'N/A')}")
                if app_id:
                    self.log(f"  Steam App ID: {app_id}")
            
            # Generate Content ID
            if not content_id:
                if app_id and auto_steam:
                    # Use Steam-based Content ID
                    content_id = self.generate_steam_content_id(app_id, region, title_id)
                else:
                    # Use hash-based Content ID (fallback)
                    import hashlib
                    hash_input = f"{song_info.get('artist', '')}{song_info.get('song_name', '')}"
                    hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:16].upper()
                    content_id = f"{region}-{title_id}_00-{hash_suffix}"
                    self.log(f"  Generated Content ID from hash: {content_id}")
            
            self.log(f"\n  Final Content ID: {content_id}")
            
            # Step 4: Convert structure
            self.log("\n" + "=" * 80)
            self.log("STEP 4: Converting PC → PS4 structure")
            self.log("=" * 80)
            if not self.convert_pc_to_ps4_structure(pc_unpacked, ps4_structure):
                return False
            
            # Step 5: Create PKG structure
            self.log("\n" + "=" * 80)
            self.log("STEP 5: Creating PKG structure")
            self.log("=" * 80)
            
            song_code = song_info.get('song_code', 'song')
            ps4_psarc = pkg_build / f"{song_code.lower()}_p.psarc"
            pkg_build.mkdir(exist_ok=True)
            
            # Create sce_sys directory
            sce_sys = pkg_build / "sce_sys"
            sce_sys.mkdir(exist_ok=True)
            
            # Create param.sfo with enhanced title
            artist = song_info.get('artist', 'Unknown Artist')
            song_name = song_info.get('song_name', 'Custom Song')
            title = f"Rocksmith 2014 - {song_name} - {artist}"
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
            
            # Save metadata
            metadata_path = pkg_build / "metadata.json"
            import json
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(song_info, f, indent=2, ensure_ascii=False)
            self.log(f"✓ Saved metadata to {metadata_path.name}")
            
            # Summary
            self.log("\n" + "=" * 80)
            self.log("CONVERSION COMPLETE")
            self.log("=" * 80)
            self.log(f"\nSong: {artist} - {song_name}")
            if app_id:
                self.log(f"Steam App ID: {app_id}")
            self.log(f"Content ID: {content_id}")
            self.log(f"\nOutput directory: {output_dir}")
            self.log(f"PKG build folder: {pkg_build}")
            self.log(f"\nNext steps:")
            self.log(f"  1. Repack {ps4_structure} as {ps4_psarc} with flags 0x4")
            self.log(f"     OR use Song Creator Toolkit: PC → Mac conversion")
            self.log(f"  2. Build PKG from: {gp4_path}")
            
            return True
            
        except Exception as e:
            self.log(f"\n✗ CONVERSION FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
    def find_pkg_tool(self) -> Optional[Path]:
        """
        Find PkgTool.exe (LibOrbisPkg) in common locations
        
        Returns:
            Path to PkgTool.exe if found, None otherwise
        """
        # Common locations to check
        possible_locations = [
            Path("PkgTool.exe"),  # Current directory
            Path("tools/PkgTool.exe"),  # tools subdirectory
            Path("LibOrbisPkg/PkgTool.exe"),
            Path("Pkg-Editor-2023/PkgTool.exe"),
            Path.home() / "LibOrbisPkg" / "PkgTool.exe",
            Path.home() / "Pkg-Editor-2023" / "PkgTool.exe",
            Path("C:/LibOrbisPkg/PkgTool.exe"),
            Path("C:/Pkg-Editor-2023/PkgTool.exe"),
            # Also check for orbis-pub-cmd as fallback
            Path("orbis-pub-cmd.exe"),
            Path("tools/orbis-pub-cmd.exe"),
        ]
        
        # Check each location
        for location in possible_locations:
            if location.exists():
                self.log(f"✓ Found PKG builder at: {location}")
                return location
        
        # Check in PATH
        import shutil
        for tool_name in ["PkgTool.exe", "PkgTool", "orbis-pub-cmd.exe"]:
            cmd_in_path = shutil.which(tool_name)
            if cmd_in_path:
                self.log(f"✓ Found PKG builder in PATH: {cmd_in_path}")
                return Path(cmd_in_path)
        
        return None
    
    def build_pkg_from_gp4(self, gp4_file: Path, output_dir: Path, 
                           pkg_tool: Path = None) -> bool:
        """
        Build PKG file from GP4 project using built-in Python PKG builder
        
        Args:
            gp4_file: Path to .gp4 project file
            output_dir: Directory for output .pkg file
            pkg_tool: Path to external PKG tool (optional, for fallback)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.log(f"\n[7/7] Building PKG file...")
            self.log(f"GP4 project: {gp4_file.name}")
            self.log(f"Working directory: {output_dir}")
            
            # Try Python PKG builder first (built-in, no external dependencies!)
            if HAS_PYTHON_PKG_BUILDER and build_pkg_from_gp4:
                self.log("Using built-in Python PKG builder (no external tools needed!)")
                
                # Call Python PKG builder
                result_pkg = build_pkg_from_gp4(gp4_file, output_dir)
                
                if result_pkg and result_pkg.exists():
                    size_mb = result_pkg.stat().st_size / (1024 * 1024)
                    self.log(f"✓ PKG built successfully!")
                    self.log(f"  File: {result_pkg.name}")
                    self.log(f"  Size: {size_mb:.1f} MB")
                    self.log(f"  Location: {result_pkg}")
                    return True
                else:
                    self.log("✗ Python PKG builder failed")
                    # Fall through to try external tool
            
            # Fallback to external PKG tool if Python builder not available or failed
            if not pkg_tool:
                pkg_tool = self.find_pkg_tool()
                
            if not pkg_tool or not pkg_tool.exists():
                self.log("\n⚠ PKG building failed!")
                self.log("   Python PKG builder not available or failed")
                self.log("   No external PKG tool found")
                self.log("   Download LibOrbisPkg from: https://github.com/maxton/LibOrbisPkg")
                self.log("   Place PkgTool.exe in same folder as RiffBridge")
                return False
            
            self.log(f"Trying external PKG tool: {pkg_tool.name}...")
            
            # Determine which tool we're using
            tool_name = pkg_tool.name.lower()
            
            if "pkgtool" in tool_name:
                # LibOrbisPkg PkgTool.exe
                cmd = [
                    str(pkg_tool.absolute()),
                    "pkg_build",
                    gp4_file.name,
                    "."
                ]
                self.log(f"Using LibOrbisPkg (open source)")
            else:
                # orbis-pub-cmd.exe
                cmd = [
                    str(pkg_tool.absolute()),
                    "img_create",
                    gp4_file.name,
                    f"{gp4_file.stem}.pkg"
                ]
                self.log(f"Using orbis-pub-cmd (proprietary)")
            
            self.log(f"Command: {' '.join(cmd)}")
            
            # Run external PKG builder
            import subprocess
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(output_dir)
            )
            
            self.log(f"Return code: {result.returncode}")
            
            # Check for PKG file
            pkg_files = list(output_dir.glob("*.pkg"))
            
            if pkg_files and len(pkg_files) > 0:
                pkg_file = pkg_files[0]
                size_mb = pkg_file.stat().st_size / (1024 * 1024)
                self.log(f"✓ PKG built successfully!")
                self.log(f"  File: {pkg_file.name}")
                self.log(f"  Size: {size_mb:.1f} MB")
                self.log(f"  Location: {pkg_file}")
                return True
            else:
                self.log(f"✗ PKG build failed!")
                if result.stdout:
                    self.log(f"  stdout: {result.stdout.strip()}")
                if result.stderr:
                    self.log(f"  stderr: {result.stderr.strip()}")
                return False
                
        except Exception as e:
            self.log(f"✗ Error building PKG: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_pkg_from_ps4(self, 
                            input_psarc: Path, 
                            output_dir: Path,
                            content_id: str = None,
                            title_id: str = 'CUSA00745',
                            region: str = 'EP0001',
                            auto_steam: bool = True,
                            build_pkg: bool = True,
                            pkg_tool: Path = None) -> bool:
        """
        Create PKG files for an already-PS4 format .psarc file
        Skips conversion since the file is already PS4 format
        
        Args:
            input_psarc: PS4 format .psarc file
            output_dir: Output directory for PKG files
            content_id: Custom Content ID (optional)
            title_id: PS4 Title ID
            region: Region code
            auto_steam: Try to detect Steam App ID and fetch metadata
            build_pkg: Whether to build final .pkg file (requires PkgTool.exe or orbis-pub-cmd.exe)
            pkg_tool: Path to PKG building tool (optional, will search if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.log(f"\n{'='*60}")
            self.log("CREATING PKG FOR PS4 FILE (NO CONVERSION NEEDED)")
            self.log(f"{'='*60}")
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get song code from filename
            song_code = input_psarc.stem.replace('_p', '').replace('_m', '')
            self.log(f"Song code: {song_code}")
            
            # Try to detect Steam App ID if enabled
            steam_info = None
            app_id = None
            
            if auto_steam and self.steam_db:
                self.log("\n[1/5] Attempting to detect Steam App ID...")
                # We can't unpack to detect app_id since it's already PS4
                # Instead, try to search Steam database by filename
                steam_info = self.steam_db.search_by_filename(song_code)
                if steam_info:
                    app_id = steam_info.get('app_id')
                    self.log(f"✓ Found Steam DLC: {steam_info.get('title', 'Unknown')}")
                    self.log(f"  App ID: {app_id}")
                else:
                    self.log("✓ No Steam match found - will use generic metadata")
            else:
                self.log("\n[1/5] Skipping Steam detection")
            
            # Generate Content ID
            self.log("\n[2/5] Generating Content ID...")
            if not content_id:
                if app_id:
                    # Use Steam-based content ID
                    content_id = self.generate_steam_content_id(
                        app_id=app_id,
                        region=region,
                        title_id=title_id
                    )
                else:
                    # Generate generic content ID from song code
                    # Format: REGION-TITLEID_00-SONGCODE0000000
                    song_suffix = f"SONG{song_code.upper()}".ljust(16, '0')[:16]
                    content_id = f"{region}-{title_id}_00-{song_suffix}"
                    self.log(f"  Generated generic Content ID: {content_id}")
            
            self.log(f"Content ID: {content_id}")
            
            # Copy PS4 psarc to output (rename with proper naming)
            self.log("\n[3/5] Copying PS4 psarc file...")
            ps4_psarc_name = f"{song_code}_ps4.psarc"
            ps4_psarc_path = output_dir / ps4_psarc_name
            
            import shutil
            shutil.copy2(input_psarc, ps4_psarc_path)
            self.log(f"✓ Copied to: {ps4_psarc_path.name}")
            
            # Create param.sfo
            self.log("\n[4/5] Creating param.sfo...")
            title = steam_info.get('title', song_code.replace('_', ' ').title()) if steam_info else song_code.replace('_', ' ').title()
            
            # Create sce_sys directory for proper PKG structure
            sce_sys_dir = output_dir / 'sce_sys'
            sce_sys_dir.mkdir(exist_ok=True)
            
            param_sfo_path = sce_sys_dir / 'param.sfo'
            self.create_param_sfo(
                output_path=param_sfo_path,
                title_id=title_id,
                content_id=content_id,
                title=title[:128],  # PS4 title limit
                version='01.00'
            )
            self.log(f"✓ Created: sce_sys/{param_sfo_path.name}")
            
            # Create icon
            self.log("\n[5/5] Creating icon0.png...")
            icon_path = sce_sys_dir / 'icon0.png'
            self.create_default_icon(icon_path)  # Use create_default_icon method
            self.log(f"✓ Created: sce_sys/{icon_path.name}")
            
            # Create GP4 project file
            gp4_path = output_dir / f"{song_code}_ps4.gp4"
            self.create_gp4_project(
                output_path=gp4_path,
                content_id=content_id,
                psarc_filename=ps4_psarc_name
            )
            self.log(f"✓ Created: {gp4_path.name}")
            
            # [7/7] Build PKG file if requested
            pkg_path = None
            if build_pkg:
                pkg_built = self.build_pkg_from_gp4(
                    gp4_file=gp4_path,
                    output_dir=output_dir,
                    pkg_tool=pkg_tool
                )
                
                if pkg_built:
                    # Find the created PKG file
                    pkg_files = list(output_dir.glob("*.pkg"))
                    if pkg_files:
                        pkg_path = pkg_files[0]
                
                if not pkg_built:
                    self.log("\n⚠ PKG file was not built (tool not found)")
                    self.log("   You can build it manually with:")
                    self.log(f"   PkgTool.exe pkg_build {gp4_path.name} .")
            
            # Success summary
            self.log(f"\n{'='*60}")
            if build_pkg and pkg_path and pkg_path.exists():
                self.log("✓ COMPLETE PS4 PKG CREATED SUCCESSFULLY!")
            else:
                self.log("✓ PKG FILES CREATED SUCCESSFULLY!")
            self.log(f"{'='*60}\n")
            self.log("Output files:")
            self.log(f"  • {ps4_psarc_path.name} (PS4 format psarc)")
            self.log(f"  • sce_sys/param.sfo")
            self.log(f"  • sce_sys/icon0.png")
            self.log(f"  • {gp4_path.name}")
            if pkg_path and pkg_path.exists():
                size_mb = pkg_path.stat().st_size / (1024 * 1024)
                self.log(f"  • {pkg_path.name} ({size_mb:.1f} MB) ← READY TO INSTALL!")
            
            if pkg_path and pkg_path.exists():
                self.log(f"\n✓ Your PS4 PKG is ready!")
                self.log(f"   Location: {pkg_path}")
                self.log(f"   Install on PS4: Copy to USB → Install from Package Installer")
            else:
                self.log(f"\nNext steps:")
                self.log(f"  1. Use orbis-pub-cmd or similar tool to build PKG")
                self.log(f"  2. Install PKG on PS4")
                self.log(f"  3. Enjoy!")
            
            return True
            
        except Exception as e:
            self.log(f"\n✗ PKG CREATION FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Enhanced Rocksmith PC to PS4 Converter with Steam integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic conversion with auto Steam detection
  python enhanced_converter.py song.psarc ./output

  # Without Steam integration
  python enhanced_converter.py song.psarc ./output --no-steam

  # Custom Content ID
  python enhanced_converter.py song.psarc ./output --content-id EP0001-CUSA00745_00-CUSTOMSONG000001

Steam DLC Database:
  The converter can automatically fetch DLC info from Steam.
  First run may be slow as it fetches data.
  Subsequent runs use cached data.
        """
    )
    
    parser.add_argument('input_psarc', type=str, help='Input PC psarc file')
    parser.add_argument('output_dir', type=str, help='Output directory')
    parser.add_argument('--content-id', type=str, help='Custom PS4 Content ID')
    parser.add_argument('--title-id', type=str, default='CUSA00745', help='PS4 Title ID')
    parser.add_argument('--region', type=str, default='EP0001', help='Region code')
    parser.add_argument('--no-steam', action='store_true', help='Disable Steam integration')
    parser.add_argument('--quiet', action='store_true', help='Suppress output')
    
    args = parser.parse_args()
    
    # Validate input
    input_path = Path(args.input_psarc)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    # Run conversion
    converter = EnhancedRocksmithConverter(
        verbose=not args.quiet,
        use_steam_db=not args.no_steam
    )
    
    success = converter.convert_enhanced(
        input_psarc=input_path,
        output_dir=Path(args.output_dir),
        content_id=args.content_id,
        title_id=args.title_id,
        region=args.region,
        auto_steam=not args.no_steam
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
