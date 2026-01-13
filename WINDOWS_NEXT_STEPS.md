# Windows - Next Steps to Build Your PKG

## What Happened

You ran PkgTool and got these errors:
```
FATAL ERROR: PKG Content ID must be 36 characters long.
FATAL ERROR: Could not load param.sfo file: Unknown SFO type: 0402
```

## What I Fixed

✅ **Content ID**: Changed from 40 to 36 characters
✅ **param.sfo format**: Changed data type from `0x0402` to `0x0204`

---

## 🔄 How to Rebuild with Fixes

### Step 1: Download Updated Script

**Option A - PowerShell (Recommended):**
```powershell
cd C:\test
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/rocksmith_pc_to_ps4_complete.py" -OutFile "rocksmith_pc_to_ps4_complete.py"
```

**Option B - Manual:**
1. Go to: https://github.com/rifftbridge/PS4/blob/claude/rocksmith-pc-ps4-converter-TlrD1/rocksmith_pc_to_ps4_complete.py
2. Click "Raw" button
3. Save as `rocksmith_pc_to_ps4_complete.py` in `C:\test\`

### Step 2: Download Helper Batch Files

**Download these new files to C:\test:**
```powershell
# Download rebuild script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/rebuild_fixed.bat" -OutFile "rebuild_fixed.bat"

# Download convert_song script
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/rifftbridge/PS4/claude/rocksmith-pc-ps4-converter-TlrD1/convert_song.bat" -OutFile "convert_song.bat"
```

### Step 3: Run the Rebuild

**Easiest way:**
```batch
.\rebuild_fixed.bat
```

**Or manually:**
```powershell
# Clean old files
Remove-Item cooppois_p.gp4 -ErrorAction SilentlyContinue
Remove-Item -Recurse build_dir -ErrorAction SilentlyContinue

# Generate new GP4 with fixes
python rocksmith_pc_to_ps4_complete.py cooppois_p.psarc . "Poison by Alice Cooper"

# Build PKG
.\PkgTool.Core.exe pkg_build cooppois_p.gp4 .
```

---

## ✅ Success Looks Like This

```
Building package...
Parsing GP4...
Loading param.sfo...
Creating PFS image...
  Adding sce_sys/param.sfo
  Adding sce_sys/icon0.png
  Adding DLC/cooppois_p.psarc
Building image...
Creating outer PKG...
Writing PKG...

Package creation successful!
Output: .\cooppois_p.pkg
```

Then check your file:
```powershell
dir cooppois_p.pkg
```

Should be around 30-50 MB.

---

## 📋 Your Files Checklist

Make sure you have these in `C:\test\`:

**Required:**
- ✅ PkgTool.Core.exe (and its DLL files)
- ✅ cooppois_p.psarc (input file)
- ✅ rocksmith_pc_to_ps4_complete.py **(MUST BE UPDATED VERSION)**

**Helper Scripts (optional):**
- rebuild_fixed.bat
- convert_song.bat
- build_pkg.bat

---

## 🎯 After Success

1. **Find your PKG:**
   ```powershell
   dir *.pkg
   ```

2. **Copy to USB:**
   - Format USB as FAT32
   - Create folder: `PS4\PACKAGES\`
   - Copy `cooppois_p.pkg` to that folder

3. **Install on PS4:**
   - Insert USB into PS4
   - Go to Settings → Package Installer
   - Select your PKG file
   - Install

4. **Play:**
   - Launch Rocksmith 2014
   - Check if song appears in DLC list

---

## ❓ If You Still Get Errors

Post the **complete error message** you see, including:
- The exact command you ran
- All output from PkgTool
- Any error messages

---

## 🚀 Next: Convert More Songs

Once this works, you can convert all your songs:

```powershell
# Single song
.\convert_song.bat boststar_p.psarc "More Than A Feeling by Boston"

# Or batch convert (I can help you create this)
```

---

**Current Status:** Ready to rebuild with fixes! 🎉
