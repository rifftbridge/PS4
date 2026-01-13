# PKG Analysis Findings - CE-34706-0 Root Cause

## Problem Summary

**Error Evolution:**
- Simple PKG (3 entries) → CE-34707-1 (corrupted data)
- Fixed PKG (11 entries) → CE-34706-0 (different error - PROGRESS!)

## Root Cause Identified

All 4 working PKGs from Arczi have **PFS (PlayStation File System) image**:

### Working PKG Structure:
```
Offset 0x0000: PKG Header (4KB)
Offset 0x2000: Body with metadata entries (516KB)
Offset 0x80000: PFS Image (4-7MB) ← CRITICAL DIFFERENCE!
  └─ Contains: PSARC files, param.sfo, icon0.png inside encrypted filesystem
```

### Our PKG Structure:
```
Offset 0x0000: PKG Header (4KB)
Offset 0x2000: Body with 11 metadata entries (516KB)
Offset 0x2XXX: Raw files (PSARC, param.sfo, icon0.png) ← NO PFS!
```

## Analysis of All 4 Working PKGs

| PKG | Content ID | PFS Offset | PFS Size | Entry Count |
|-----|-----------|------------|----------|-------------|
| Poison | EP0001-CUSA00745_00-RS002SONG0001059 | 0x80000 | 5.19 MB | 11 |
| Boston | EP0001-CUSA00745_00-RS001SONG0000005 | 0x80000 | 6.50 MB | 11 |
| Tainted Love | EP0001-CUSA00745_00-RS002SONG0000838 | 0x80000 | 4.25 MB | 11 |
| Bachman-Turner | EP0001-CUSA00745_00-RS002SONG0000849 | 0x80000 | 5.25 MB | 11 |

**Consistent across ALL working PKGs:**
- PFS always starts at 0x80000 (524,288 bytes)
- All have exactly 11 entries
- DRM type: 0x0000000F
- Content type: 0x0000001B (DLC)
- Content flags: 0x0A000000
- Body offset: 0x2000
- Body size: 516,096 bytes

## Why CE-34706-0 Occurs

Firmware 11.00 requires:
1. ✅ Proper PKG header (we have this)
2. ✅ All 11 metadata entries (we have this)
3. ❌ **PFS filesystem image** (WE DON'T HAVE THIS!)

The PS4 expects to mount the PFS image as a filesystem, but our PKG has raw files instead.

## Solution Options

### Option 1: Use LibOrbisPkg (C# implementation)
- Includes full PFS builder
- Requires .NET/Mono
- Most compatible approach
- **Issue:** Path problems on Linux, needs Windows or proper mono setup

### Option 2: Extract & Repack PFS
- Take working Arczi PKG
- Extract PFS image (decrypt)
- Replace PSARC inside PFS
- Rebuild PKG with new PFS
- **Issue:** PFS is encrypted, need encryption keys

### Option 3: Build PFS in Python
- Implement PFS filesystem builder
- Complex: need PFS format spec, encryption, signatures
- **Estimate:** Several days of work

### Option 4: Firmware Downgrade
- Simple PKGs may work on firmware 9.00 or earlier
- Firmware 11.00 is stricter
- **Issue:** Requires jailbreaking older firmware

## Recommended Path Forward

**Test on Windows:**
1. Run LibOrbisPkg PkgTool.exe on Windows (where .NET works better)
2. Create GP4 project with proper paths
3. Build PKG with full PFS support
4. Test on PS4

If Windows approach fails, implement Option 2 (extract/modify working PKG).

## Files Analyzed

- 4 working PKG files from Arczi
- 4 matching PC .psarc files
- Total data: ~41MB of samples

## Next Steps

1. Determine best approach (Windows build vs PFS extraction)
2. Implement chosen solution
3. Test generated PKG on PS4 firmware 11.00
4. Validate DLC appears in Rocksmith

---

**Status:** Blocked on PFS implementation
**Updated:** 2026-01-07
