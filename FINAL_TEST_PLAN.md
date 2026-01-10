# Final Test Plan - Two Approaches to Test

## 🎯 Goal

Determine which approach creates working PS4 PKGs for your Rocksmith DLC.

---

## 📊 What We Know

### Working Arczi PKG:
- ✅ Installs and plays on PS4
- Format: PC PSARC (archiveFlags=0)
- Files: 21 files inside PSARC
- Size: 4.8 MB PSARC

### Your PC DLC Files:
- ❌ Crashes Rocksmith (CE-34878-0)
- Format: PS4/Mac PSARC (archiveFlags=4)
- Files: 27 files inside PSARC
- Size: 5.0 MB PSARC
- Note: "Cherub Rock" patched for CDLC enablement

### Key Discovery:
The Rocksmith toolkit source code shows:
```csharp
_header.ArchiveFlags = encrypt ? 4U : 0U;
```
- `archiveFlags=4` = PS4/Mac encrypted format
- `archiveFlags=0` = PC unencrypted format

**Working PKG uses PC format (0), your files are PS4 format (4)!**

---

## 🧪 Test 1: Use Exact PSARC from Working PKG

This tests if our PKG building process is correct.

### Download Files:

```powershell
cd C:\test

# Download working PSARC
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/samples/CoopPois_from_working_pkg.psarc" -OutFile "CoopPois_from_working_pkg.psarc"

# Download icon
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/samples/icon0_from_working_pkg.png" -OutFile "icon0_from_working_pkg.png"

# Download rebuild script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/rebuild_arczi_replica.bat" -OutFile "rebuild_arczi_replica.bat"

# Download Python converter (updated)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/rocksmith_pc_to_ps4_complete.py" -OutFile "rocksmith_pc_to_ps4_complete.py"
```

### Build and Test:

```batch
.\rebuild_arczi_replica.bat
```

This creates: `EP0001-CUSA00745_00-RS002SONG0001059.pkg`

### Test on PS4:
1. Uninstall old PKG if installed
2. Copy new PKG to USB
3. Install on PS4
4. Test in Rocksmith

### Expected Result:
- ✅ **Should work** - This uses exact files from working PKG
- If this fails, our PKG process has other issues

---

## 🧪 Test 2: Convert Your PSARC Format

This tests if converting flags 4→0 is sufficient.

### Download Converter:

```powershell
cd C:\test

# Download format converter
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/convert_psarc_to_pc_format.py" -OutFile "convert_psarc_to_pc_format.py"

# Download complete conversion script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/convert_and_build.bat" -OutFile "convert_and_build.bat"
```

### Build and Test:

```batch
.\convert_and_build.bat cooppois_p.psarc "Poison by Alice Cooper"
```

This will:
1. Check PSARC format (currently flags=4)
2. Convert to PC format (flags 4→0)
3. Build GP4 project
4. Create PKG file

### Test on PS4:
1. Uninstall old PKG
2. Install new PKG
3. Test in Rocksmith

### Expected Result:
- ✅ **Might work** - If flags conversion is enough
- ❌ **Might fail** - If 27 files vs 21 files is the issue

---

## 📝 Comparison Matrix

| Test | PSARC Source | Format | Files | Should Work? |
|------|-------------|--------|-------|--------------|
| Test 1 | Working PKG | PC (0) | 21 | ✅ High confidence |
| Test 2 | Your PC file | PC (0) converted | 27 | ⚠️ Unknown |
| Original | Your PC file | PS4 (4) | 27 | ❌ Confirmed fails |

---

## 🔍 What Test Results Tell Us

### If Test 1 Works + Test 2 Fails:
**Problem:** The 6 extra files (27 vs 21)

**Solution needed:**
- Identify which 6 files to remove
- Extract PSARC, remove files, rebuild
- Possible files to remove:
  - Mac-specific files
  - Metadata files
  - Cherub Rock patch files

### If Test 1 Works + Test 2 Works:
**Problem solved!** ✅

**Solution:**
- Just convert archiveFlags from 4→0
- Use `convert_and_build.bat` for all songs

### If Test 1 Fails:
**Problem:** Our PKG building process

**Next steps:**
- Binary compare our PKG vs working Arczi PKG
- Check PFS encryption/signing differences
- Investigate firmware requirements

---

## 🎸 Batch Convert All Songs

Once you know which approach works, use it for all songs:

### If Test 1 Approach (using working PSARCs):
You need the original working PSARCs from Arczi PKGs

### If Test 2 Approach (format conversion):
```batch
REM Convert all your PC DLC
convert_and_build.bat boststar_p.psarc "More Than A Feeling by Boston"
convert_and_build.bat maritain_p.psarc "Tainted Love by Marilyn Manson"
convert_and_build.bat bachyoua_p.psarc "You Ain't Seen Nothing Yet"
REM ... etc for all your DLC
```

---

## 📚 Files Reference

### In C:\test\ you should have:

**Required:**
- `PkgTool.Core.exe` - PKG builder
- `rocksmith_pc_to_ps4_complete.py` - Converter (updated with PUBTOOLINFO)
- `convert_psarc_to_pc_format.py` - Format converter
- `convert_and_build.bat` - Complete conversion script

**For Test 1:**
- `CoopPois_from_working_pkg.psarc` - Working PSARC
- `icon0_from_working_pkg.png` - Working icon
- `rebuild_arczi_replica.bat` - Test 1 script

**Your Source Files:**
- `cooppois_p.psarc`, `cooppois_m.psarc` - PC/Mac DLC
- `boststar_p.psarc`, `maritain_p.psarc`, etc. - Other songs

---

## 🚨 Important Notes

1. **Always uninstall old broken PKG before testing new one**
2. **Test one PKG at a time**
3. **Note exact error codes if it fails**
4. **Cherub Rock patching is for PC CDLC only** - PS4 jailbreak doesn't need it

---

## 📊 Report Back

After testing, please report:

**Test 1 (Working PSARC):**
- ✅ or ❌ Did it install?
- ✅ or ❌ Did Rocksmith crash?
- ✅ or ❌ Does song appear in DLC list?
- ✅ or ❌ Is song playable?

**Test 2 (Converted PSARC):**
- Same questions as above

This will tell us exactly what needs to be done for your full DLC library!

---

**Ready to test!** 🎸 Let me know the results!
