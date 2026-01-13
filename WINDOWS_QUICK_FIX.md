# Windows PowerShell - Quick Fix Guide

## Your Current Error

```
PkgTool.Core.exe : The term 'PkgTool.Core.exe' is not recognized...
```

**Why this happens:** PowerShell requires `.\` prefix for local executables.

---

## THE FIX - Run This Command

You are in `C:\test\` with all your files. Here's the **exact command** to run:

### PowerShell:
```powershell
.\PkgTool.Core.exe pkg_build cooppois_p.gp4 .
```

### Command Prompt (cmd.exe):
```batch
PkgTool.Core.exe pkg_build cooppois_p.gp4 .
```

**Important:** Notice the `.` (dot) at the end - this is the output directory!

---

## Complete Workflow

### If you already have the GP4 file:
```powershell
.\PkgTool.Core.exe pkg_build cooppois_p.gp4 .
```

### If you need to create the GP4 first:
```powershell
# Step 1: Create GP4 project
python rocksmith_pc_to_ps4_complete.py cooppois_p.psarc cooppois_p_ps4 "Poison by Alice Cooper"

# Step 2: Build PKG
.\PkgTool.Core.exe pkg_build cooppois_p_ps4\cooppois_p.gp4 cooppois_p_ps4
```

### Using the batch script (easiest):
```batch
.\convert_song.bat cooppois_p.psarc "Poison by Alice Cooper"
```

---

## What Each Part Means

```powershell
.\PkgTool.Core.exe pkg_build cooppois_p.gp4 .
│                  │          │                │
│                  │          │                └─ Output directory (. = current dir)
│                  │          └─────────────────── GP4 input file
│                  └────────────────────────────── Command (build PKG)
└───────────────────────────────────────────────── .\ = run local executable
```

---

## Common PowerShell Mistakes

❌ **WRONG:**
```powershell
PkgTool.Core.exe pkg_build cooppois_p.gp4          # Missing .\ and output dir
convert_song.bat cooppois_p.psarc                   # Missing .\ prefix
```

✅ **CORRECT:**
```powershell
.\PkgTool.Core.exe pkg_build cooppois_p.gp4 .      # Has .\ and output dir
.\convert_song.bat cooppois_p.psarc                 # Has .\ prefix
```

---

## After Running the Command

### Success looks like:
```
Building PKG...
Creating PFS filesystem...
Adding file: sce_sys/param.sfo
Adding file: sce_sys/icon0.png
Adding file: DLC/cooppois_p.psarc
Signing blocks...
Encrypting...
Done! Package created: cooppois_p.pkg
```

### Then check for your PKG:
```powershell
dir *.pkg
```

You should see `cooppois_p.pkg` (about 30-50 MB depending on song size)

---

## If It Still Fails

### Check your files are in place:
```powershell
dir
```

You should see:
- ✅ PkgTool.Core.exe
- ✅ PkgTool.Core.dll
- ✅ cooppois_p.gp4
- ✅ cooppois_p.psarc (in build_dir/Image0/DLC/)
- ✅ param.sfo (in build_dir/Sc0/)
- ✅ icon0.png (in build_dir/Sc0/)

### Try with dotnet:
```powershell
dotnet .\PkgTool.Core.dll pkg_build cooppois_p.gp4 .
```

---

## Next Steps After Success

1. **Find your PKG:** `dir *.pkg`
2. **Copy to USB:** Format USB as FAT32, create folder `PS4\PACKAGES\`
3. **Copy PKG:** Put `cooppois_p.pkg` in that folder
4. **Install:** On PS4, use Package Installer
5. **Play:** Launch Rocksmith 2014!

---

## Quick Commands Summary

```powershell
# If starting fresh:
.\convert_song.bat cooppois_p.psarc "Poison by Alice Cooper"

# If you just need to build PKG from existing GP4:
.\PkgTool.Core.exe pkg_build cooppois_p.gp4 .

# Check for PKG file:
dir *.pkg
```

🎉 **You're literally one command away from success!**
