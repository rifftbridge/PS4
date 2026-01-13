# Rocksmith PC to PS4 Converter - Solution Path

## Status: BLOCKED on PFS Implementation

### What We've Learned

**Root Cause of Errors:**
- **CE-34707-1**: PKG missing required metadata entries (FIXED by adding 11 entries)
- **CE-34706-0**: PKG missing PFS (PlayStation File System) image - **CURRENT BLOCKER**

### PKG Structure Required for Firmware 11.00

All working PS4 PKGs have this structure:

```
Offset 0x0000: PKG Header (4 KB)
  - Magic: 0x7F434E54
  - DRM Type: 0x0000000F
  - Content Type: 0x0000001B (DLC)
  - Content Flags: 0x0A000000

Offset 0x2000: Body with 11 metadata entries (516 KB)
  - 0x0001: DIGESTS (352 bytes)
  - 0x0010: ENTRY_KEYS (2048 bytes) - encryption keys
  - 0x0020: IMAGE_KEY (256 bytes) - image encryption key
  - 0x0080: GENERAL_DIGESTS (384 bytes)
  - 0x0100: METAS (352 bytes)
  - 0x0200: ENTRY_NAMES (21 bytes) - "param.sfo\0icon0.png\0"
  - 0x0400: LICENSE (1024 bytes) - license data
  - 0x0401: LICENSE_INFO (512 bytes)
  - 0x0409: PSRESERVED (8192 bytes) - zeros
  - 0x1000: PARAM_SFO (972 bytes) - game metadata
  - 0x1200: ICON0_PNG (485 KB) - game icon

Offset 0x80000: PFS Image (4-7 MB) ← CRITICAL!
  - Encrypted PlayStation File System
  - Contains: PSARC files, directory structure
  - Uses AES-XTS encryption
  - Includes inodes, flat_path_table, signatures
```

### Analysis of Working PKGs

Analyzed 4 working Rocksmith DLC PKGs from Arczi:
| Song | Content ID | PFS Size | Verified |
|------|-----------|----------|----------|
| Poison | EP0001-CUSA00745_00-RS002SONG0001059 | 5.19 MB | ✅ Works on FW 11.00 |
| Boston | EP0001-CUSA00745_00-RS001SONG0000005 | 6.50 MB | ✅ Works on FW 11.00 |
| Tainted Love | EP0001-CUSA00745_00-RS002SONG0000838 | 4.25 MB | ✅ Works on FW 11.00 |
| Bachman-Turner | EP0001-CUSA00745_00-RS002SONG0000849 | 5.25 MB | ✅ Works on FW 11.00 |

All have identical structure:
- PFS offset: 0x80000 (524,288 bytes)
- Entry count: 11
- Body size: 516,096 bytes

### What PFS Contains

PFS is a complete filesystem with:
1. **Superroot directory** - contains flat_path_table and uroot
2. **Inodes** - file/directory metadata
3. **Flat Path Table** - for fast file lookups
4. **Directory entries (dirents)** - file listings
5. **Data blocks** - actual game files (PSARC)
6. **Signatures** - HMAC-SHA256 signatures for each block
7. **Encryption** - AES-XTS encryption of data

### Tools That Can Build PFS

#### 1. LibOrbisPkg (C# - Recommended)
- **Repository**: https://github.com/maxton/LibOrbisPkg
- **Tool**: PkgTool.exe
- **Command**: `PkgTool.exe pkg_build <input.gp4> <output_dir>`
- **Status**: ❌ Has path resolution issues on Linux with mono
- **Solution**: Need to compile from source with dotnet, or run on Windows

#### 2. CyB1K fpkg-tools (Windows Executables)
- **Repository**: https://github.com/CyB1K/PS4-Fake-PKG-Tools-3.87
- **Tools**: gengp4_app.exe, orbis-pub-gen.exe
- **Status**: ❌ Requires wine32, which has dependency conflicts on this system
- **Solution**: Need Windows or properly configured wine environment

### Current Python Implementation

**File**: `rocksmith_to_ps4_fixed.py`

What it does:
- ✅ Creates valid PKG header
- ✅ Generates proper param.sfo
- ✅ Adds all 11 required metadata entries
- ❌ Does NOT create PFS image (puts PSARC directly in body)

**Result**: CE-34706-0 error (PS4 expects PFS image, not raw files)

### Solution Options

#### Option A: Use LibOrbisPkg on Windows
1. Install .NET SDK on Windows machine
2. Clone LibOrbisPkg repository
3. Build with: `dotnet build LibOrbisPkg.sln`
4. Use PkgTool.exe to build PKG from GP4 project
5. Test on PS4

**Pros**: Most reliable, full PFS support
**Cons**: Requires Windows or proper .NET environment

#### Option B: Implement PFS in Python
1. Port PFS builder logic from LibOrbisPkg C# code
2. Implement:
   - Inode creation
   - Flat path table generation
   - HMAC-SHA256 signing
   - AES-XTS encryption
   - Directory entry structures

**Pros**: Standalone Python solution
**Cons**: Very complex, 2-3 days of work, high risk of bugs

#### Option C: Modify Working PKG
1. Extract PFS from working Arczi PKG (encrypted)
2. Decrypt PFS image
3. Replace PSARC inside PFS
4. Re-encrypt and re-sign PFS
5. Rebuild PKG

**Pros**: Uses known-good PFS structure
**Cons**: Need decryption keys (EKPFS), complex encryption handling

#### Option D: Template-Based Approach
1. Use working Poison PKG as exact template
2. Only change: Content ID, param.sfo Title, and PSARC data
3. Recalculate signatures and hashes
4. Keep all encryption keys/licenses from template

**Pros**: Simpler than full PFS rebuild
**Cons**: May not work if encryption keys are validated per-content

### Recommended Next Steps

1. **Try Option A** - Get LibOrbisPkg building properly:
   - Install dotnet SDK: `apt-get install dotnet-sdk-8.0`
   - Build LibOrbisPkg
   - Create GP4 project file (sample included: `test_dlc.gp4`)
   - Build PKG and test

2. **If Option A fails** - Try Option D:
   - Extract encryption keys from working PKG
   - Use as template for new PKGs
   - Modify only metadata and PSARC

3. **Last resort** - Implement Option B:
   - Port PFS builder to Python
   - Test incrementally
   - Validate against working PKGs

### Files Created

- `extract_pfs.py` - Extract PFS image from PKG
- `analyze_pkg.py` - Analyze PKG header
- `analyze_pkg_entries.py` - Extract and analyze all PKG entries
- `analyze_psarc.py` - Analyze PSARC files
- `rocksmith_to_ps4_fixed.py` - PKG builder (no PFS)
- `test_dlc.gp4` - Sample GP4 project file
- `PKG_ANALYSIS.md` - Detailed analysis findings
- `poison_entries/` - Extracted entries from working PKG
- `poison_pfs.img` - Extracted PFS image (5.19 MB, encrypted)

### References

- **LibOrbisPkg PFS Implementation**: `LibOrbisPkg/LibOrbisPkg/PFS/PFSBuilder.cs`
- **GP4 Format**: XML-based project format for PKG building
- **PS4 PKG Specification**: See `LibOrbisPkg/PS4PKG.bt` (010 Editor template)
- **PFS Specification**: See `LibOrbisPkg/PS4PFS.bt`

---

**Conclusion**: The converter is 90% complete. The only missing piece is PFS image creation, which requires either using existing C# tools (LibOrbisPkg) or implementing a complex filesystem builder in Python.

**Updated**: 2026-01-07
