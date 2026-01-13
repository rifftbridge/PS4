# Arczi Replica Test - Clean Setup

## 🎯 What This Does

Tests if our PKG building process works by rebuilding the working Arczi PKG.

Uses the **exact PSARC file** from the working Arczi PKG that you know works on your PS4.

---

## 📁 Files in This Folder

**Essential (included):**
- `rocksmith_pc_to_ps4_complete.py` - Python converter (creates GP4 and param.sfo)
- `rebuild_arczi_replica.bat` - Test script
- `CoopPois_from_working_pkg.psarc` - PSARC extracted from working Arczi PKG
- `icon0_from_working_pkg.png` - Icon from working PKG (optional)

**You need to add:**
- `PkgTool.Core.exe` - PKG builder (you have this in C:\test)
- `PkgTool.Core.dll` and other DLL files (copy all from C:\test)

---

## 🚀 Quick Start

### Step 1: Download This Folder

```powershell
# Clone or download the repository
cd C:\
git clone https://github.com/rifftbridge/PS4.git
cd PS4\final_test
```

Or download as ZIP from GitHub and extract.

### Step 2: Copy PkgTool Files

```powershell
# Copy PkgTool.Core.exe and all DLL files from your C:\test folder
Copy-Item C:\test\PkgTool.Core.* -Destination .
Copy-Item C:\test\*.dll -Destination .
```

### Step 3: Run the Test

```batch
.\rebuild_arczi_replica.bat
```

---

## ✅ What Should Happen

1. **Creates GP4 project** with proper param.sfo (972 bytes, 9 entries)
2. **Builds PKG file** named: `EP0001-CUSA00745_00-RS00XXXXXXXX.pkg`
3. **PKG size**: ~5-6 MB

---

## 🎮 Test on PS4

1. Copy the PKG to USB drive (FAT32 format)
2. Put in folder: `PS4\PACKAGES\`
3. On PS4: Settings → Package Installer
4. Install the PKG
5. Launch Rocksmith 2014

---

## 📊 Possible Results

### ✅ SUCCESS: PKG Installs and Works
**Meaning:** Our PKG building process is correct!
**Problem:** Steam DLC files have DRM issues
**Next step:** Use different source files (CDLC, PS3, or other)

### ❌ FAIL: CE-34707-1 (DRM Signature Error)
**Meaning:** PkgTool.Core.exe isn't signing correctly
**Problem:** PKG builder tool incompatible with PS4 firmware 11.00
**Next step:** Try different PKG builder

### ❌ FAIL: CE-34878-0 (App Crashes)
**Meaning:** PKG structure still has issues
**Problem:** Something wrong with param.sfo or PSARC packaging
**Next step:** Further debugging needed

---

## 🔧 Troubleshooting

### Script stops immediately
- Missing files - check you have PkgTool.Core.exe
- Run: `dir` to see all files in folder

### "Cannot find Python"
- Install Python: https://www.python.org/downloads/
- Or run commands manually (see below)

### Manual commands:
```powershell
python rocksmith_pc_to_ps4_complete.py CoopPois_from_working_pkg.psarc . "Rocksmith2014 - Poison by Alice Cooper"
.\PkgTool.Core.exe pkg_build CoopPois_from_working_pkg.gp4 .
```

---

## 📝 Files You'll Get

After running, you'll have:
- `build_dir/` - Directory with param.sfo, icon, and PSARC
- `CoopPois_from_working_pkg.gp4` - GP4 project file
- `EP0001-CUSA00745_00-RS00XXXXXXXX.pkg` - The PKG to test!

---

## ❓ Questions to Answer

After testing, report:
1. ✅/❌ Did PKG install without errors?
2. ✅/❌ Did Rocksmith load without crash?
3. ✅/❌ Does song appear in DLC list?
4. ✅/❌ Is song playable?

This tells us if the problem is with the PKG builder or the source files!

---

**This is the cleanest test possible - uses files we KNOW work on PS4!** 🎸
