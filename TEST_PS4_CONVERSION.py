#!/usr/bin/env python3
"""
Quick test script to debug PS4 conversion
Run this to see detailed error messages
"""

import sys
import os
from pathlib import Path

def test_ps4_conversion():
    """Test PS4 file conversion"""
    
    print("="*60)
    print("PS4 CONVERSION TEST")
    print("="*60)
    
    # CRITICAL: Change to script's directory!
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Show where we're running from
    print(f"\nScript directory: {script_dir}")
    print(f"Current directory: {os.getcwd()}")
    
    # NOW import the converter (after changing to correct directory)
    try:
        from enhanced_converter import EnhancedRocksmithConverter
        print("✓ Converter imported successfully")
    except Exception as e:
        print(f"✗ Failed to import converter: {e}")
        input("\nPress Enter to exit...")
        return
    
    print(f"\nFiles in this directory:")
    for f in os.listdir('.'):
        print(f"  - {f}")
    
    print("\n" + "="*60)
    
    # Look for any .psarc file
    psarc_files = [f for f in os.listdir('.') if f.endswith('.psarc')]
    
    if not psarc_files:
        print("ERROR: No .psarc files found in this directory!")
        print("\nPlease put a .psarc file in the same folder as this script")
        input("\nPress Enter to exit...")
        return
    
    print(f"Found {len(psarc_files)} .psarc file(s):")
    for f in psarc_files:
        print(f"  - {f}")
    
    # Use the first .psarc file found
    input_file = Path(psarc_files[0])
    output_dir = Path("test_output")
    
    print(f"\nUsing: {input_file}")
    print(f"Output dir: {output_dir}")
    
    # Create converter
    print("\nInitializing converter...")
    converter = EnhancedRocksmithConverter(verbose=True, use_steam_db=True)
    
    # Test conversion
    print("\nStarting PS4 PKG creation...")
    print("-"*60)
    
    try:
        success = converter.create_pkg_from_ps4(
            input_psarc=input_file,
            output_dir=output_dir,
            title_id='CUSA00745',
            region='EP0001',
            auto_steam=True
        )
        
        print("-"*60)
        
        if success:
            print("\n✓ SUCCESS!")
            print(f"\nCheck folder: {output_dir}")
        else:
            print("\n✗ FAILED!")
            print("Converter returned False but no exception")
    
    except Exception as e:
        print("\n✗ EXCEPTION!")
        print(f"Error: {e}")
        print("\nFull traceback:")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    test_ps4_conversion()
