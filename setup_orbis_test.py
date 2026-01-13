#!/usr/bin/env python3
"""
Setup test directory for orbis-pub tools
"""

import struct
from pathlib import Path


def create_param_sfo(content_id: str, title: str,
                     title_id: str = "CUSA00745", version: str = "01.00") -> bytes:
    """Create param.sfo file"""
    entries = [
        ("ATTRIBUTE", 0, 4, 0x0404),
        ("CATEGORY", "ac", 4, 0x0402),
        ("CONTENT_ID", content_id, 48, 0x0402),
        ("FORMAT", "obs", 4, 0x0402),
        ("TITLE", title, 128, 0x0402),
        ("TITLE_ID", title_id, 12, 0x0402),
        ("VERSION", version, 8, 0x0402),
    ]

    sfo = bytearray()
    sfo += b'\x00PSF'
    sfo += struct.pack('<I', 0x0101)

    key_data = b""
    for key, value, max_len, data_type in entries:
        key_data += key.encode('utf-8') + b'\x00'
    while len(key_data) % 4 != 0:
        key_data += b'\x00'

    key_table_start = 20
    index_table_size = len(entries) * 16
    data_table_start = key_table_start + index_table_size + len(key_data)

    sfo += struct.pack('<I', key_table_start + index_table_size)
    sfo += struct.pack('<I', data_table_start)
    sfo += struct.pack('<I', len(entries))

    data_values = []
    for key, value, max_len, data_type in entries:
        if data_type == 0x0404:
            data_values.append(struct.pack('<I', value))
        else:
            data_values.append(value.encode('utf-8') + b'\x00')

    key_offset = 0
    data_offset = 0
    for i, (key, value, max_len, data_type) in enumerate(entries):
        sfo += struct.pack('<H', key_offset)
        sfo += struct.pack('<H', data_type)
        sfo += struct.pack('<I', len(data_values[i]))
        sfo += struct.pack('<I', max_len)
        sfo += struct.pack('<I', data_offset)
        key_offset += len(key) + 1
        data_offset += max_len

    sfo += key_data

    for i, (key, value, max_len, data_type) in enumerate(entries):
        data = data_values[i]
        sfo += data
        padding = max_len - len(data)
        if padding > 0:
            sfo += b'\x00' * padding

    return bytes(sfo)


def create_icon_png() -> bytes:
    """Create minimal PNG icon"""
    return bytes.fromhex(
        '89504e470d0a1a0a0000000d4948445200000001000000010802000000'
        '907753de0000000c4944415478da626000000000050001b5a6b7cd0000'
        '000049454e44ae426082'
    )


# Create test structure
test_dir = Path("test_build/CUSA00745-app")
sce_sys = test_dir / "sce_sys"
sce_sys.mkdir(parents=True, exist_ok=True)

# Create param.sfo
content_id = "EP0001-CUSA00745_00-RS002SONG0001059"
title = "Rocksmith2014 - Poison"
param_sfo = create_param_sfo(content_id, title, "CUSA00745")

with open(sce_sys / "param.sfo", 'wb') as f:
    f.write(param_sfo)

print(f"Created param.sfo: {len(param_sfo)} bytes")

# Create icon0.png
icon_png = create_icon_png()
with open(sce_sys / "icon0.png", 'wb') as f:
    f.write(icon_png)

print(f"Created icon0.png: {len(icon_png)} bytes")

# Copy keystone (create dummy for now)
# According to README, keystone is required for base apps
keystone_data = bytes(96)  # Dummy keystone
with open(sce_sys / "keystone", 'wb') as f:
    f.write(keystone_data)

print(f"Created keystone: {len(keystone_data)} bytes")

print(f"\nTest structure created in: {test_dir}")
print(f"Files:")
for file in sorted(test_dir.rglob('*')):
    if file.is_file():
        size = file.stat().st_size
        print(f"  {file.relative_to(test_dir)}: {size} bytes")
