"""
PS4 PKG Builder - Pure Python Implementation
Based on PS4 PKG format specification and LibOrbisPkg
Creates fake PKG files for PS4 homebrew/DLC
"""

import struct
import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Optional
import io


class PS4PkgBuilder:
    """Build PS4 PKG files from GP4 projects"""
    
    # PKG Constants
    PKG_MAGIC = 0x7F434E54  # 0x7F 'CNT'
    PKG_TYPE_FAKE = 0x0001  # Fake PKG type
    PKG_CONTENT_TYPE_GD = 0x1A  # Additional Content (DLC)
    
    # Entry IDs
    ENTRY_DIGESTS = 0x0001
    ENTRY_CONTENT_INFO = 0x0002
    ENTRY_LICENSE = 0x0400
    ENTRY_PARAM_SFO = 0x1000
    ENTRY_ICON0 = 0x1200
    
    def __init__(self):
        self.files = []
        self.content_id = ""
        self.passcode = bytes(32)  # All zeros for fake PKG
        
    def parse_gp4(self, gp4_path: Path) -> bool:
        """
        Parse GP4 project file
        
        Args:
            gp4_path: Path to .gp4 file
            
        Returns:
            True if successful
        """
        try:
            tree = ET.parse(gp4_path)
            root = tree.getroot()
            
            # Get content ID
            package = root.find('.//package')
            if package is not None:
                self.content_id = package.get('content_id', '')
            
            # Get file list
            files_elem = root.find('.//files')
            if files_elem is not None:
                base_dir = gp4_path.parent
                for file_elem in files_elem.findall('file'):
                    targ_path = file_elem.get('targ_path')
                    orig_path = file_elem.get('orig_path')
                    
                    # Resolve actual file path
                    actual_path = base_dir / orig_path
                    if actual_path.exists():
                        self.files.append({
                            'target': targ_path,
                            'source': actual_path,
                            'size': actual_path.stat().st_size
                        })
            
            return len(self.files) > 0
            
        except Exception as e:
            print(f"Error parsing GP4: {e}")
            return False
    
    def _get_entry_id_for_file(self, target_path: str) -> int:
        """Determine entry ID based on file path"""
        target_lower = target_path.lower()
        
        if 'param.sfo' in target_lower:
            return self.ENTRY_PARAM_SFO
        elif 'icon0.png' in target_lower:
            return self.ENTRY_ICON0
        else:
            # Data files get sequential IDs starting at 0x1201
            return 0x1201
    
    def build_pkg(self, output_path: Path) -> bool:
        """
        Build PKG file
        
        Args:
            output_path: Path for output .pkg file
            
        Returns:
            True if successful
        """
        try:
            # Calculate sizes
            header_size = 0x1000  # 4KB header
            entry_table_size = len(self.files) * 32  # 32 bytes per entry
            data_offset = header_size + entry_table_size
            
            # Align to 16 bytes
            data_offset = (data_offset + 15) & ~15
            
            # Calculate total data size
            total_data_size = 0
            file_offsets = []
            for file_info in self.files:
                file_offsets.append(total_data_size)
                # Align each file to 16 bytes
                aligned_size = (file_info['size'] + 15) & ~15
                total_data_size += aligned_size
            
            pkg_size = data_offset + total_data_size
            
            # Create PKG
            with open(output_path, 'wb') as pkg:
                # Write header
                self._write_header(pkg, header_size, entry_table_size, 
                                 data_offset, total_data_size, pkg_size)
                
                # Write entry table
                self._write_entry_table(pkg, data_offset, file_offsets)
                
                # Pad to data offset
                pkg.seek(data_offset)
                
                # Write file data
                for i, file_info in enumerate(self.files):
                    with open(file_info['source'], 'rb') as f:
                        data = f.read()
                        pkg.write(data)
                        
                        # Pad to 16-byte alignment
                        aligned_size = (len(data) + 15) & ~15
                        padding = aligned_size - len(data)
                        if padding > 0:
                            pkg.write(bytes(padding))
            
            return True
            
        except Exception as e:
            print(f"Error building PKG: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _write_header(self, pkg, header_size: int, entry_table_size: int,
                     data_offset: int, data_size: int, pkg_size: int):
        """Write PKG header (Big Endian)"""
        
        # Main header (0x000 - 0x0FF)
        pkg.write(struct.pack('>I', self.PKG_MAGIC))  # 0x000: Magic
        pkg.write(struct.pack('>I', self.PKG_TYPE_FAKE))  # 0x004: Type
        pkg.write(struct.pack('>I', 0))  # 0x008: Unknown
        pkg.write(struct.pack('>I', len(self.files)))  # 0x00C: File count
        pkg.write(struct.pack('>I', len(self.files)))  # 0x010: Entry count
        pkg.write(struct.pack('>H', 0))  # 0x014: SC entry count
        pkg.write(struct.pack('>H', len(self.files)))  # 0x016: Entry count 2
        pkg.write(struct.pack('>I', header_size))  # 0x018: Table offset
        pkg.write(struct.pack('>I', entry_table_size))  # 0x01C: Entry data size
        pkg.write(struct.pack('>Q', data_offset))  # 0x020: Body offset
        pkg.write(struct.pack('>Q', data_size))  # 0x028: Body size
        pkg.write(struct.pack('>Q', data_offset))  # 0x030: Content offset
        pkg.write(struct.pack('>Q', data_size))  # 0x038: Content size
        
        # Content ID (36 bytes) + padding (12 bytes) = 0x040 - 0x06F
        content_id_bytes = self.content_id.encode('ascii')[:36]
        content_id_bytes = content_id_bytes.ljust(36, b'\x00')
        pkg.write(content_id_bytes)  # 0x040: Content ID
        pkg.write(bytes(12))  # 0x064: Padding
        
        # DRM and content info (0x070 - 0x0FF)
        pkg.write(struct.pack('>I', 0))  # 0x070: DRM type (free/fake)
        pkg.write(struct.pack('>I', self.PKG_CONTENT_TYPE_GD))  # 0x074: Content type
        pkg.write(struct.pack('>I', 0))  # 0x078: Content flags
        pkg.write(struct.pack('>I', 0))  # 0x07C: Promote size
        pkg.write(struct.pack('>I', 0))  # 0x080: Version date
        pkg.write(struct.pack('>I', 0))  # 0x084: Version hash
        pkg.write(struct.pack('>I', 0))  # 0x088: Unknown
        pkg.write(struct.pack('>I', 0))  # 0x08C: Unknown
        pkg.write(struct.pack('>I', 0))  # 0x090: Unknown
        pkg.write(struct.pack('>I', 0))  # 0x094: Unknown
        pkg.write(struct.pack('>I', 0))  # 0x098: Unknown
        pkg.write(struct.pack('>I', 0))  # 0x09C: Unknown
        
        # IROTag (0x0A0 - 0x0FF) - all zeros for fake PKG
        pkg.write(bytes(0x60))
        
        # Digest table (0x100 - 0xFFF) - simplified for fake PKG
        pkg.write(bytes(header_size - 0x100))
    
    def _write_entry_table(self, pkg, data_offset: int, file_offsets: List[int]):
        """Write PKG entry table"""
        
        for i, file_info in enumerate(self.files):
            entry_id = self._get_entry_id_for_file(file_info['target'])
            file_offset = data_offset + file_offsets[i]
            file_size = file_info['size']
            
            # Entry format (32 bytes, big endian):
            # 0x00: Entry ID (4 bytes)
            # 0x04: Filename offset (4 bytes) - not used in fake PKG
            # 0x08: Flags (4 bytes)
            # 0x0C: Padding (4 bytes)
            # 0x10: File offset (8 bytes)
            # 0x18: File size (8 bytes)
            
            pkg.write(struct.pack('>I', entry_id))  # Entry ID
            pkg.write(struct.pack('>I', 0))  # Filename offset (unused)
            pkg.write(struct.pack('>I', 0))  # Flags
            pkg.write(struct.pack('>I', 0))  # Padding
            pkg.write(struct.pack('>Q', file_offset))  # File offset
            pkg.write(struct.pack('>Q', file_size))  # File size


def build_pkg_from_gp4(gp4_file: Path, output_dir: Path) -> Optional[Path]:
    """
    Build a PS4 PKG from a GP4 project file
    
    Args:
        gp4_file: Path to .gp4 project file
        output_dir: Directory for output .pkg file
        
    Returns:
        Path to created PKG file, or None if failed
    """
    try:
        # Parse GP4
        builder = PS4PkgBuilder()
        if not builder.parse_gp4(gp4_file):
            print("Failed to parse GP4 file")
            return None
        
        # Generate output filename from content ID
        pkg_filename = f"{builder.content_id}.pkg"
        output_path = output_dir / pkg_filename
        
        # Build PKG
        print(f"Building PKG: {pkg_filename}")
        print(f"Content ID: {builder.content_id}")
        print(f"Files: {len(builder.files)}")
        
        if builder.build_pkg(output_path):
            print(f"✓ PKG created: {output_path}")
            print(f"  Size: {output_path.stat().st_size / (1024*1024):.1f} MB")
            return output_path
        else:
            print("✗ Failed to build PKG")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None


# CLI usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ps4_pkg_builder.py <gp4_file> [output_dir]")
        sys.exit(1)
    
    gp4_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else gp4_file.parent
    
    result = build_pkg_from_gp4(gp4_file, output_dir)
    sys.exit(0 if result else 1)
