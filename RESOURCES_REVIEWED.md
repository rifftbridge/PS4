# Additional Resources Review

## Summary

Reviewed 9+ additional repositories and tools related to Rocksmith and PS4 PKG handling. **Key finding**: None of these provide a solution for building PS4 PKGs with PFS for firmware 11.00.

## Resources Reviewed

### 1. Rocksmith Custom Song Toolkit
- **URL**: https://github.com/rscustom/rocksmith-custom-song-toolkit
- **Language**: C#
- **Purpose**: CDLC (Custom DLC) creation for Rocksmith
- **Platforms Supported**: PC, Mac, Xbox 360, PS3
- **PS4 Support**: ❌ NO - Only old-gen consoles
- **Verdict**: Not useful for PS4 PKG building

**Key Code**:
```csharp
public enum GamePlatform { Pc, Mac, XBox360, PS3, None };
```

### 2. PS4_Tools / PS4_PKG_Viewer
- **URL**: https://github.com/xXxTheDarkprogramerxXx/PS4_Tools
- **Purpose**: PKG viewer/analyzer (similar to what we built)
- **Capabilities**: View PKG contents, extract files
- **Building**: ❌ NO - Viewer only, not a builder
- **Verdict**: Analysis tool, not helpful for PKG creation

### 3. PkgToolBox
- **URL**: https://github.com/seregonwar/PkgToolBox
- **Language**: Python
- **Purpose**: PKG manipulation (extract, inject, modify)
- **Building**: ⚠️ LIMITED - Can modify existing PKGs, not build from scratch
- **Includes**: orbis-pub-cmd.exe (but wine issues)
- **Verdict**: Good for modifying PKGs, not for creating new ones

### 4. rsrtools (Rust)
- **URL**: https://github.com/BuongiornoTexas/rsrtools
- **Language**: Rust
- **Purpose**: Rocksmith PSARC tools
- **Scope**: PSARC handling only, no PKG building
- **Verdict**: Useful for PSARC, but we already can read PSARCs

### 5. rsgt (Go)
- **URL**: https://github.com/JustinAiken/rsgt
- **Language**: Go
- **Purpose**: Rocksmith tools
- **Scope**: PSARC/manifest manipulation
- **Verdict**: PSARC tools, no PKG building

### 6. psarcjs (JavaScript)
- **URL**: https://github.com/sandiz/psarcjs
- **Language**: JavaScript/Node.js
- **Purpose**: PSARC extraction
- **Scope**: PSARC only
- **Verdict**: Limited to PSARC extraction

### 7. Rocksmith2014PsarcLib (C#)
- **URL**: https://github.com/kokolihapihvi/Rocksmith2014PsarcLib
- **Language**: C#
- **Purpose**: PSARC library for Rocksmith 2014
- **Scope**: PSARC reading/writing
- **Verdict**: PSARC-focused, no PKG support

### 8. rockysmithereens (Rust)
- **URL**: https://github.com/tversteeg/rockysmithereens
- **Language**: Rust
- **Purpose**: Rocksmith file tools
- **Scope**: Game file manipulation
- **Verdict**: No PKG building

### 9. FPKGi
- **URL**: https://github.com/ItsJokerZz/FPKGi
- **Purpose**: PS4/PS5 PKG installer (runs on console)
- **Capabilities**: Install PKGs from server
- **Building**: ❌ NO - Installer only, not a builder
- **Verdict**: For installing PKGs, not creating them

## Analysis

### What These Tools CAN Do:
✅ Extract/read PSARC files
✅ Modify PSARC contents
✅ View PKG files
✅ Extract files from PKGs
✅ Modify existing PKGs

### What These Tools CANNOT Do:
❌ Build PS4 PKGs from scratch with PFS
❌ Create PFS (PlayStation File System) images
❌ Generate proper PKG signatures for firmware 11.00
❌ Encrypt PFS with AES-XTS

## Why These Tools Don't Help

All reviewed tools fall into these categories:

1. **PSARC Tools Only**: Focus on PSARC files, which we already handle
2. **Old-Gen Console Support**: Support PS3, not PS4
3. **PKG Viewers**: Can analyze PKGs but not build them
4. **PKG Modifiers**: Can modify existing PKGs but not create new ones with PFS

## The Real Issue: PFS Generation

**None of the reviewed tools can generate PFS filesystem images.**

PFS requires:
- Inode filesystem structures
- Flat path table with collision resolution
- HMAC-SHA256 signatures for each block
- AES-XTS encryption with EKPFS key derivation
- Proper directory entries (dirents) and superroot setup

## Tools That CAN Build PKGs with PFS

Only these tools have full PFS support:

### 1. LibOrbisPkg (✅ CONFIRMED)
- **URL**: https://github.com/maxton/LibOrbisPkg
- **Already Downloaded**: Yes (in our repo)
- **Status**: Cannot build due to proxy/network issues
- **Solution**: Need Windows or Linux with nuget.org access

### 2. Sony Official Tools (Not Available)
- orbis-pub-cmd.exe (official SDK)
- Available in fpkg-tools and PkgToolBox
- **Status**: Requires wine32 (dependency issues)

## Recommendation

**Stick with LibOrbisPkg as the solution.**

The additional resources don't provide any new paths forward. LibOrbisPkg remains the only viable open-source tool that can:
1. Build PKGs from scratch
2. Generate proper PFS images
3. Support firmware 11.00

### Next Steps (Unchanged):

**Option A - Build LibOrbisPkg on Windows**:
1. Use Windows machine with .NET SDK
2. Build LibOrbisPkg solution
3. Use PkgTool.exe to build PKGs

**Option B - Build LibOrbisPkg on Linux with Network**:
1. Get network access to nuget.org (bypass proxy)
2. Build with dotnet SDK
3. Use PkgTool

**Option C - Implement PFS in Python** (Last Resort):
1. Port PFS builder from LibOrbisPkg C# code
2. Estimated 2-3 days of complex work
3. High risk of bugs

## Files in Repository

After reviewing all resources, our repository now contains:

**Analysis Tools** (Created):
- extract_pfs.py
- analyze_pkg.py
- analyze_pkg_entries.py
- analyze_psarc.py

**Converter** (90% Complete):
- rocksmith_to_ps4_fixed.py

**Documentation**:
- PKG_ANALYSIS.md
- SOLUTION_PATH.md
- FINDINGS.md
- RESOURCES_REVIEWED.md (this file)

**External Tools** (Downloaded, in .gitignore):
- LibOrbisPkg/
- fpkg-tools/
- pkgtoolbox/
- rocksmith-custom-song-toolkit/
- FPKGi/

## Conclusion

**No new solutions found.** LibOrbisPkg is still the only path forward for building proper PS4 PKGs with PFS for firmware 11.00.

The reviewed tools are either:
- PSARC-focused (we already handle this)
- PS3-only (old generation)
- Viewers/analyzers (we built this)
- Modifiers (can't create from scratch)

---

**Date**: 2026-01-07
**Status**: LibOrbisPkg remains the solution
