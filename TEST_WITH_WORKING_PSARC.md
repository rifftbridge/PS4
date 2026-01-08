# Test with Working PSARC - Simple Steps

## 🎯 Goal

Test if our PKG building process works by using the **exact PSARC from the working Arczi PKG**.

## Critical Discovery

Your PC/Mac PSARCs are **different format** than what's in the working PS4 PKG:

| Your Files | Working PKG |
|------------|-------------|
| 27 files, flags=4 (PS4 format) | 21 files, flags=0 (PC format) |
| 5.0 MB | 4.8 MB |

The working PS4 DLC uses **PC-format PSARCs**, not PS4-format!

---

## 📥 Step 1: Download Files

In PowerShell (`C:\test\`):

```powershell
# Download PSARC from working PKG
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/samples/CoopPois_from_working_pkg.psarc" -OutFile "CoopPois_from_working_pkg.psarc"

# Download icon from working PKG
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/samples/icon0_from_working_pkg.png" -OutFile "icon0_from_working_pkg.png"

# Download rebuild script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/rebuild_arczi_replica.bat" -OutFile "rebuild_arczi_replica.bat"

# Download Python converter (if not already updated)
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/rocksmith_pc_to_ps4_complete.py" -OutFile "rocksmith_pc_to_ps4_complete.py"
```

---

## 🔨 Step 2: Build PKG

```batch
.\rebuild_arczi_replica.bat
```

This will create: `EP0001-CUSA00745_00-RS002SONG0001059.pkg`

---

## 🎮 Step 3: Test on PS4

1. **Uninstall old broken PKG** (if installed)
2. Copy new PKG to USB
3. Install on PS4
4. Launch Rocksmith

---

## ✅ What This Test Tells Us

### If it WORKS:
- ✅ Our PKG building process is **correct**
- ❌ Problem is the **source PSARC format**
- 📝 Solution: Need to convert PC/Mac PSARCs to PC format

### If it FAILS with same error:
- ❌ Something else wrong with our PKG structure
- 🔍 Need to investigate further

---

## 🤔 Next Steps Based on Results

### If Working PSARC Test Succeeds:

We need to figure out how to convert your PC/Mac PSARCs:
1. **Extract** the PC/Mac PSARC (27 files, flags=4)
2. **Remove** 6 files (identify which ones)
3. **Rebuild** as PC format PSARC (21 files, flags=0)
4. **Package** in PS4 PKG

Possible approaches:
- Use Rocksmith Custom Song Toolkit
- Use psarc command-line tools
- Find which 6 files to remove by comparing file lists

### If Working PSARC Test Fails:

Need to investigate PKG structure:
- Compare our PKG binary to working Arczi PKG
- Check PFS encryption/signing
- Verify all metadata fields
- Check firmware requirements

---

## 📊 Files You Have Now

In `C:\test\`:
- `PkgTool.Core.exe` - PKG builder
- `rocksmith_pc_to_ps4_complete.py` - Converter (updated)
- `CoopPois_from_working_pkg.psarc` - Exact PSARC from working PKG (4.8 MB)
- `icon0_from_working_pkg.png` - Exact icon from working PKG (474 KB)
- `rebuild_arczi_replica.bat` - Test script
- `cooppois_p.psarc` - Your original PC file (5.0 MB) - **wrong format**
- `cooppois_m.psarc` - Your Mac file (5.0 MB) - **wrong format**

---

## 🔍 Questions to Answer

1. **Where did you get the PC/Mac PSARCs?**
   - Steam DLC folder?
   - Downloaded from CDLC site?
   - Extracted from somewhere?

2. **Do they work on PC/Mac Rocksmith?**
   - Can you load them in the game?
   - Do they show up in DLC list?

3. **Are there PC-format versions available?**
   - Do you have access to actual PC DLC (flags=0)?
   - Or only the Mac/PS4-format versions (flags=4)?

---

**Let me know the test results!** This will determine our next steps. 🎸
