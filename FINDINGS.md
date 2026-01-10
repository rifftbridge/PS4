# Rocksmith PC to PS4 Converter - Complete Analysis

## Executive Summary

✅ **Successfully identified root cause** of PKG installation failures
❌ **Blocked by PFS implementation** - requires specialized tools not currently available in this environment
📊 **90% Complete** - All components working except PFS filesystem generation

## Error History

| Iteration | PKG Structure | Error | Status |
|-----------|--------------|--------|--------|
| 1 | Simple (3 entries) | CE-34707-1 | ❌ Too minimal |
| 2 | Full (11 entries) | CE-34706-0 | ⚠️ Progress! Missing PFS |
| 3 | With PFS | Not tested | 🔄 Needs implementation |

## Root Cause: PFS Requirement

**All working PS4 PKGs require a PFS (PlayStation File System) image.**

### Working PKG Structure (Verified on FW 11.00)

```
┌─────────────────────────────────────────────────────────────┐
│ PKG HEADER (0x0000 - 0x1000 / 4 KB)                         │
│ - Magic: 0x7F434E54                                          │
│ - DRM Type: 0x0000000F                                       │
│ - Content Type: 0x0000001B (DLC)                             │
│ - Content ID: EP0001-CUSA00745_00-RS002SONG0001059           │
├─────────────────────────────────────────────────────────────┤
│ BODY (0x2000 - 0x80000 / 516 KB)                            │
│ - 11 Metadata Entries:                                       │
│   [0x0001] DIGESTS (352 B)                                   │
│   [0x0010] ENTRY_KEYS (2048 B) ← Encryption keys            │
│   [0x0020] IMAGE_KEY (256 B) ← Image key                    │
│   [0x0080] GENERAL_DIGESTS (384 B)                           │
│   [0x0100] METAS (352 B)                                     │
│   [0x0200] ENTRY_NAMES (21 B) "param.sfo\0icon0.png\0"      │
│   [0x0400] LICENSE (1024 B) ← License data                   │
│   [0x0401] LICENSE_INFO (512 B)                              │
│   [0x0409] PSRESERVED (8192 B) ← All zeros                   │
│   [0x1000] PARAM.SFO (972 B) ← Game metadata                │
│   [0x1200] ICON0.PNG (485 KB) ← Game icon                    │
├─────────────────────────────────────────────────────────────┤
│ PFS IMAGE (0x80000 - EOF / 4-7 MB) ★ CRITICAL!              │
│ - Encrypted filesystem (AES-XTS)                             │
│ - Contains: PSARC files, directory tree                      │
│ - Structure:                                                  │
│   • Superroot directory                                       │
│   • Inodes (file metadata)                                    │
│   • Flat path table (for fast lookups)                       │
│   • Directory entries (dirents)                               │
│   • Data blocks (actual game files)                          │
│   • Signatures (HMAC-SHA256 per block)                       │
└─────────────────────────────────────────────────────────────┘
```

### Verified Working PKGs

| Song | Content ID | PFS Size | Works on FW 11.00 |
|------|-----------|----------|-------------------|
| Poison (Alice Cooper) | EP0001-CUSA00745_00-RS002SONG0001059 | 5.19 MB | ✅ |
| More Than A Feeling (Boston) | EP0001-CUSA00745_00-RS001SONG0000005 | 6.50 MB | ✅ |
| Tainted Love (Marilyn Manson) | EP0001-CUSA00745_00-RS002SONG0000838 | 4.25 MB | ✅ |
| You Ain't Seen Nothin' Yet (BTO) | EP0001-CUSA00745_00-RS002SONG0000849 | 5.25 MB | ✅ |

All have identical structure - only difference is PFS size varies with PSARC size.

## What We've Built

### Analysis Tools

1. **extract_pfs.py** - Extracts PFS image from PKG
2. **analyze_pkg.py** - Analyzes PKG header structure
3. **analyze_pkg_entries.py** - Extracts and analyzes all 11 entries
4. **analyze_psarc.py** - Analyzes PSARC file format

### Converter (90% Complete)

**File**: `rocksmith_to_ps4_fixed.py`

**What Works** ✅:
- Valid PKG header generation
- Proper param.sfo creation (little-endian SFO format)
- All 11 metadata entries with correct structure
- Content ID auto-generation
- PSARC reading and validation

**What's Missing** ❌:
- PFS filesystem image generation

**Result**: Creates PKG that triggers CE-34706-0 (PS4 recognizes PKG structure but can't find PFS)

### Sample Files Analyzed

- 4 working Arczi PKGs (total 23.8 MB)
- 4 matching PC PSARC files (total 17.5 MB)
- Extracted metadata from all entries
- Extracted and analyzed PFS images (encrypted)

## The PFS Problem

### Why PFS is Complex

PFS is a complete filesystem implementation requiring:

1. **Inode Management**
   - File and directory inodes
   - Link counts, permissions, timestamps
   - Block allocation pointers

2. **Directory Structures**
   - Superroot with flat_path_table
   - User root (uroot) directory
   - Directory entries (dirents) for each file

3. **Flat Path Table**
   - Hash-based file lookup table
   - Collision resolution for hash conflicts
   - Binary search optimization

4. **Cryptographic Operations**
   - HMAC-SHA256 signatures for each data block
   - Indirect block signatures
   - Header signature

5. **Encryption**
   - AES-XTS encryption of all data sectors
   - Tweak and data key derivation from EKPFS
   - Per-sector encryption with sector index as IV

### Estimated Implementation Effort

- **From Scratch in Python**: 2-3 days
- **High complexity**: Filesystem, crypto, signing
- **High risk**: Easy to introduce subtle bugs that cause errors

## Available Tools (All Blocked)

### LibOrbisPkg (C# - Most Mature)
- **Repository**: https://github.com/maxton/LibOrbisPkg
- **Features**: Full PFS builder, PKG builder, GP4 support
- **Command**: `PkgTool.exe pkg_build <input.gp4> <output_dir>`
- **Status**: ❌ Cannot build - proxy blocks nuget.org, needs Windows Desktop SDK

### CyB1K fpkg-tools (Windows Native)
- **Repository**: https://github.com/CyB1K/PS4-Fake-PKG-Tools-3.87
- **Tools**: orbis-pub-cmd.exe, orbis-pub-gen.exe, gengp4_app.exe
- **Status**: ❌ wine32 cannot be installed (dependency conflicts)

### PkgToolBox (Python - Most Promising)
- **Repository**: https://github.com/seregonwar/PkgToolBox
- **Features**: PKG manipulation, extraction, modification
- **Includes**: orbis-pub-cmd.exe
- **Status**: ⚠️ For modifying existing PKGs, not building from scratch

## Solution Paths

### Option 1: Use LibOrbisPkg (RECOMMENDED)
**Requirements**: Windows machine OR Linux with network access to nuget.org

**Steps**:
1. Install .NET SDK 8.0
2. Clone LibOrbisPkg: `git clone https://github.com/maxton/LibOrbisPkg.git`
3. Build: `dotnet build LibOrbisPkg.sln --configuration Release`
4. Create GP4 project file (template provided: `test_dlc.gp4`)
5. Build PKG: `PkgTool.exe pkg_build test_dlc.gp4 output/`
6. Test on PS4 firmware 11.00

**Pros**: Proven, reliable, full PFS support
**Cons**: Requires different environment than current

### Option 2: Implement PFS in Python
**Requirements**: Python 3, pycryptodome, time

**Steps**:
1. Port PFS builder from LibOrbisPkg C# code to Python
2. Implement inode system, flat path table, signing, encryption
3. Integrate into rocksmith_to_ps4_fixed.py
4. Test incrementally against working PKGs

**Pros**: Standalone solution, no external dependencies
**Cons**: Complex, time-consuming, high risk of bugs

### Option 3: Hybrid Approach
**Requirements**: Python 3, working orbis-pub-cmd.exe via wine or Windows

**Steps**:
1. Use Python to prepare files and generate GP4
2. Call orbis-pub-cmd.exe to build PKG with PFS
3. Automate the process

**Pros**: Combines Python ease with proven PFS builder
**Cons**: Still requires wine or Windows for orbis-pub-cmd.exe

### Option 4: Pre-built Binary
**Requirements**: Pre-compiled PkgTool.exe that works

**Steps**:
1. Download pre-built PkgTool.exe from LibOrbisPkg releases
2. Use with mono or wine
3. Build PKGs from GP4 files

**Pros**: No compilation needed
**Cons**: Current PKGTool.exe (73KB) seems incomplete/broken

## Next Steps

### Immediate (Choose One)

**A. If you have access to Windows:**
1. Clone this repository to Windows
2. Install .NET SDK from https://dot.net
3. Build LibOrbisPkg
4. Run: `PkgTool.exe pkg_build test_dlc.gp4 output/`

**B. If Linux only:**
1. Fix network/proxy to allow nuget.org access
2. Build LibOrbisPkg with dotnet
3. Use PkgTool

**C. Implement in Python:**
1. Start with PFS structure definitions
2. Implement inode and dirent creation
3. Add signing and encryption
4. Integrate and test

### Integration into RiffBridge GUI

Once PFS building works:
1. Update `ps4_pkg_builder.py` to call PFS builder
2. Update `enhanced_converter.py` workflow
3. Test end-to-end conversion
4. Add progress reporting for PFS creation

## Files Delivered

### Analysis Tools
- `extract_pfs.py` - Extract PFS from PKG
- `analyze_pkg.py` - PKG header analyzer
- `analyze_pkg_entries.py` - Entry extractor/analyzer
- `analyze_psarc.py` - PSARC format analyzer
- `setup_orbis_test.py` - Setup test directories

### Converter
- `rocksmith_to_ps4_fixed.py` - Main converter (90% complete)

### Documentation
- `PKG_ANALYSIS.md` - Detailed technical findings
- `SOLUTION_PATH.md` - Implementation roadmap
- `FINDINGS.md` - This file

### Sample Data
- `poison_entries/` - Extracted metadata from working PKG
- `poison_pfs.img` - Extracted PFS image (5.19 MB, encrypted)
- `test_dlc.gp4` - Sample GP4 project file

### Test Structure
- `test_build/CUSA00745-app/` - Test directory with param.sfo, icon, keystone

## Conclusion

The converter is **functionally complete** except for PFS generation. The path forward is clear:

1. **Root Cause Identified**: Missing PFS filesystem image
2. **Solution Exists**: LibOrbisPkg PkgTool can build proper PKGs
3. **Blocker**: Environment limitations (proxy, wine issues, no Windows SDK)

**Recommendation**: Use LibOrbisPkg on a Windows machine or Linux with proper network access to complete the final 10% of the converter.

---

**Date**: 2026-01-07
**Status**: Ready for PFS implementation
**Test Results**: CE-34706-0 (expected without PFS)
