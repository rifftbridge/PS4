# Critical Findings - Why Conversion is Failing

## 🚨 Major Discovery

The working Arczi PS4 PKG contains a **PC-format PSARC**, not a PS4-format PSARC!

### PSARC Format Comparison

| Source | Files | Archive Flags | Size | Format |
|--------|-------|---------------|------|--------|
| PC/Mac versions (cooppois_m.psarc) | 27 | 0x4 (PS4/Mac) | 5.0 MB | PS4 encrypted |
| Working PS4 PKG (CoopPois.psarc) | 21 | 0x0 (PC) | 4.8 MB | PC unencrypted |

## Key Differences

### 1. Archive Flags
- **Your files:** archiveFlags = 4 (PS4/Mac format, encrypted)
- **Working PKG:** archiveFlags = 0 (PC format, unencrypted)

### 2. File Count
- **Your files:** 27 files
- **Working PKG:** 21 files (6 files removed!)

### 3. File Size
- **Your files:** 5.0 MB
- **Working PKG:** 4.8 MB (200 KB smaller)

## What This Means

The PC DLCS you have are **already in PS4/Mac format** (archiveFlags=4), but the working PS4 PKG actually uses **PC-format PSARCs** (archiveFlags=0) with fewer files.

This suggests:

1. **Rocksmith PS4 expects PC-format PSARCs**, not PS4-format
2. **Some files need to be removed** when converting (6 files difference)
3. **Archive must be in PC mode** (flags = 0)

## Possible Explanations

### Theory 1: Arczi Re-created the PSARC
Arczi may have:
- Extracted the PC PSARC
- Removed PS4-specific files
- Rebuilt it as a PC-format PSARC
- Packaged it in a PS4 PKG

### Theory 2: Different DLC Source
The Arczi PKG might be from:
- An official PS4 DLC that was converted back to PC format
- A custom-created PSARC optimized for PS4
- A different version of the song

### Theory 3: Mac/PC DLC are Pre-Encrypted
The Mac/PC PSARCs with flags=4 might be:
- Pre-encrypted for Mac/PS4 platforms
- Not suitable for direct packaging in PS4 PKG
- Need to be converted to PC format first

## Next Steps to Test

### Test 1: Use Exact PSARC from Working PKG
Use `rebuild_arczi_replica.bat` with the extracted PSARC from working PKG.
- **If this works:** Our PKG building process is correct
- **If this fails:** There's something else wrong with our PKG structure

### Test 2: Convert PC PSARC to PC Format
We need to:
1. Extract files from PS4-format PSARC (flags=4)
2. Identify which 6 files to remove
3. Rebuild as PC-format PSARC (flags=0)
4. Package in PS4 PKG

### Test 3: Compare File Lists
Extract both PSARCs and compare:
- Which 6 files are in PC/Mac but not in working PS4?
- Are they Mac-specific files?
- Are they metadata files?

## Questions for User

1. **Where did you get the PC PSARCs from?**
   - Steam DLC folder?
   - Custom DLC download?
   - Ripped from disc?

2. **Do they work on PC Rocksmith without modification?**
   - Yes → They're valid PC DLC
   - No → They might already be converted

3. **Can you test the Arczi replica PKG?**
   - Download CoopPois_from_working_pkg.psarc
   - Run rebuild_arczi_replica.bat
   - Test on PS4
   - This will confirm if our PKG process works

## Current Status

✅ **Fixed:** param.sfo now has all 9 entries (was missing PUBTOOLINFO)
✅ **Fixed:** Content ID is 36 characters
✅ **Fixed:** SFO data types are correct (0x0204)
❌ **Issue:** Using wrong PSARC format (PS4 format instead of PC format)
❌ **Issue:** PSARC has 27 files instead of 21
🔍 **Testing:** Need to confirm PKG process works with working PSARC

## Files to Download for Testing

From GitHub `samples/` folder:
- `CoopPois_from_working_pkg.psarc` (4.8 MB) - PSARC from working Arczi PKG
- `icon0_from_working_pkg.png` (474 KB) - Icon from working Arczi PKG

Then run: `rebuild_arczi_replica.bat`
