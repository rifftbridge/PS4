#!/usr/bin/env python3
"""
Test image loading
"""

import os
from pathlib import Path

print("="*60)
print("IMAGE FILE TEST")
print("="*60)

print(f"\nCurrent directory: {os.getcwd()}")
print("\nFiles in current directory:")
for f in os.listdir('.'):
    print(f"  - {f}")

print("\n" + "="*60)
print("Checking for artwork files:")

artwork_files = [
    'Riff_Bridge_cover_art.jpg',
    'Rifft_Bridge_square_artwork_02_copy.jpg',
    'artwork.jpg',
    'logo.jpg'
]

for filename in artwork_files:
    exists = os.path.exists(filename)
    status = "✓ FOUND" if exists else "✗ NOT FOUND"
    print(f"  {status}: {filename}")

print("="*60)
input("\nPress Enter to exit...")
