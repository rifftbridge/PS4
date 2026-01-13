# PSARC Conversion Research Findings

**Date:** January 13, 2026

## Summary

Successfully building PKGs from **Arczi PSARC** (CoopPois) that work on PS4. **Cannot** successfully convert Steam DLC PSARCs - all converted files crash Rocksmith with CE-34878-0.

---

## What Works ✅

### Working PSARC: `CoopPois_from_working_pkg.psarc`
- **Source:** Extracted from working Arczi PKG
- **archiveFlags:** 0 (PC format)
- **File Count:** 21 files
- **TOC Length:** 856 bytes (0x358)
- **Bytes 32-47:** All zeros
- **Result:** PKG installs, song appears in Rocksmith, plays without crashes

### PKG Building Process
1. Use PSARC with archiveFlags=0
2. Create GP4 with `rocksmith_pc_to_ps4_complete.py`
3. Build PKG with `LibOrbisPkg/PkgTool.Core.exe pkg_build`
4. Result: Working PKG that installs and runs on PS4 11.00 + GoldHEN

---

## What Doesn't Work ❌

### Steam DLC PSARCs
- **archiveFlags:** 4 (PS4/Mac encrypted format)
- **File Count:** 23 files (vs Arczi's 21)
- **TOC Length:** 920 bytes (0x398) (vs Arczi's 856)
- **Bytes 32-64:** Contains encryption/signature data

### Attempted Conversions - All Failed

#### Attempt 1: Change archiveFlags only
```python
struct.pack_into('>I', data, 28, 0)  # Change flags 4→0
```
**Result:** PKG builds but crashes Rocksmith with CE-34878-0

#### Attempt 2: Change archiveFlags + Clear encryption bytes
```python
struct.pack_into('>I', data, 28, 0)  # Change flags 4→0
for i in range(32, 48):
    data[i] = 0  # Clear encryption data
```
**Result:** Corrupts TOC (Table of Contents), PSARC becomes unreadable

#### Attempt 3: Use converted PSARC in PKG
- Audioslave - Cochise: Crashes with CE-34878-0
- 311 - Amber: Crashes with CE-34878-0

---

## Key Differences: Arczi vs Steam PSARCs

### Header Comparison (First 64 bytes)

**Working Arczi PSARC (CoopPois):**
```
Magic:         PSAR
Version:       1.4
Compression:   zlib
TOC Length:    856 (0x358)
TOC Entry:     30 bytes
Num Files:     21
Block Size:    65536
ArchiveFlags:  0
Bytes 32-48:   00000000000000000000000000000000 (all zeros)
Bytes 48-64:   00000000000000031b0000000358edba (TOC data)
```

**Steam PSARC (cooppois_p.psarc - same song!):**
```
Magic:         PSAR
Version:       1.4
Compression:   zlib
TOC Length:    920 (0x398)
TOC Entry:     30 bytes
Num Files:     23 files
Block Size:    65536
ArchiveFlags:  4
Bytes 32-48:   4e3a0a91b5ba6a24f914e46e640118c4 (encryption data)
Bytes 48-64:   ea101cd83090307ccd23c72fa8cbb88b (more encryption)
```

**Critical Observations:**
1. **Different file count:** 21 vs 23 - Arczi removed/excluded 2 files
2. **Different TOC size:** 856 vs 920 bytes
3. **Encryption data:** Steam has 32+ bytes of encryption starting at offset 32
4. **Archive structure:** Completely different internal structure

---

## PSARC Unpacking/Repacking Tools Tested

### UnPSARC v2.7
- **Source:** https://github.com/rm-NoobInCoding/UnPSARC
- **Can read:** Working Arczi PSARC (archiveFlags=0)
- **Cannot read:** Steam PSARC (archiveFlags=4) - crashes with IndexOutOfRangeException
- **Cannot read:** Converted PSARC - corrupted TOC
- **Bug:** Cannot create subdirectories on Windows, all extractions fail

### PSArcInterface v1.0
- **Source:** https://github.com/MilchRatchet/PSArcInterface
- **Status:** Not yet tested
- **Download:** https://github.com/MilchRatchet/PSArcInterface/releases/tag/v1.0

---

## Conclusion

**Arczi PSARCs were COMPLETELY REPACKED, not just header-modified:**
- Different file count (21 vs 23)
- Different TOC structure
- No encryption data
- Clean PC format

**Simply modifying Steam PSARC headers does NOT work** because:
1. The internal file structure is different
2. There's encryption throughout the file, not just in headers
3. The TOC (Table of Contents) is in a different format
4. File count differs (possibly platform-specific files removed)

**To successfully convert Steam DLCs, we would need to:**
1. Fully unpack the encrypted Steam PSARC
2. Repack in clean PC format (archiveFlags=0)
3. Match the Arczi structure (21 files, proper TOC)

**Current Status:**
- ✅ Can build PKGs from existing Arczi PSARCs
- ❌ Cannot convert Steam DLCs to working PSARCs
- 🔄 Need proper PSARC unpacker for encrypted (archiveFlags=4) PSARCs
- 🔄 Need to understand which files Arczi excluded (23→21 files)

---

## Files Available

### Working PSARCs (from Arczi)
- `samples/CoopPois_from_working_pkg.psarc` (archiveFlags=0, 21 files) ✅

### Steam PSARCs (need conversion)
- `dlc/audcoch_p.psarc` (Audioslave - Cochise) archiveFlags=4
- `dlc/audcoch_m.psarc` (Audioslave - Cochise Mac) archiveFlags=4
- `dlc/cooppois_p.psarc` (Alice Cooper - Poison) archiveFlags=4
- `dlc/cooppois_m.psarc` (Alice Cooper - Poison Mac) archiveFlags=4
- `samples/boststar_p.psarc` (Boston - More Than A Feeling) archiveFlags=4
- `samples/maritain_p.psarc` (Marilyn Manson - Tainted Love) archiveFlags=4
- `samples/bachyoua_p.psarc` (Bachman-Turner Overdrive) archiveFlags=4
- `samples/cherubrock_p.psarc` (reference file, not real song) archiveFlags=4

---

## Next Steps

1. **Research PS4 PKG format** to understand if there are other differences
2. **Find working PSARC unpacker** that can handle archiveFlags=4 encryption
3. **Analyze Arczi method:** How did they create those working PSARCs?
4. **Compare file lists:** What 2 files did Arczi exclude from Steam PSARCs?
5. **Test PSArcInterface** as alternative unpacker

---

## Tools & Scripts Created

### Working Scripts
- `convert_psarc_to_pc_format.py` - Changes archiveFlags and clears encryption (doesn't work for full conversion)
- `rocksmith_pc_to_ps4_complete.py` - Creates GP4 and param.sfo for PKG building
- `batch_convert_dlc.py` - Batch converter (works for Arczi PSARCs only)

### Tools Used
- `LibOrbisPkg/PkgTool.Core.exe` - PKG building (works perfectly)
- `UnPSARC.exe` - PSARC unpacker (has bugs, can't handle encryption)
- `PSArc-cl.exe` - Alternative unpacker (not yet tested)

---

## Error Log

- **CE-34878-0:** Application crash (Rocksmith crashes when loading converted Steam PSARC)
- **CE-34707-1:** DRM signature error (solved - use LibOrbisPkg)
- **UnPSARC IndexOutOfRangeException:** Cannot unpack encrypted PSARCs (archiveFlags=4)
- **UnPSARC path errors:** Cannot create subdirectories on Windows
