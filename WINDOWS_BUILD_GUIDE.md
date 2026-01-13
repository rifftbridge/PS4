# Windows Build Guide - Quick Start

**Time Required**: 10-15 minutes
**Difficulty**: Easy

---

## Prerequisites (One-Time Setup)

### 1. Install .NET SDK 8.0

**Option A - Using Installer (Recommended)**:
1. Go to: https://dotnet.microsoft.com/download/dotnet/8.0
2. Download ".NET SDK 8.0.x" for Windows x64
3. Run installer
4. Click through installation wizard

**Option B - Using winget (If you have Windows Package Manager)**:
```powershell
winget install Microsoft.DotNet.SDK.8
```

**Verify Installation**:
```powershell
dotnet --version
# Should show: 8.0.xxx
```

### 2. Install Git (if not already installed)

Download from: https://git-scm.com/download/win

Or use winget:
```powershell
winget install Git.Git
```

---

## Build LibOrbisPkg (5 minutes)

### Step 1: Clone Repository

Open PowerShell or Command Prompt:

```powershell
cd C:\Users\YourName\Documents
git clone https://github.com/maxton/LibOrbisPkg.git
cd LibOrbisPkg
```

### Step 2: Build PkgTool

```powershell
dotnet build PkgTool\PkgTool.csproj --configuration Release
```

**Expected Output**:
```
Microsoft (R) Build Engine version...
...
Build succeeded.
    0 Warning(s)
    0 Error(s)

Time Elapsed 00:00:XX.XX
```

### Step 3: Locate PkgTool.exe

The compiled tool will be at:
```
LibOrbisPkg\PkgTool\bin\Release\netcoreapp3.0\PkgTool.exe
```

**Verify it works**:
```powershell
cd PkgTool\bin\Release\netcoreapp3.0
.\PkgTool.exe
```

You should see usage information.

---

## Use the Converter (2 minutes per song)

### Step 1: Get Your Files Ready

Copy to a working directory:
- Your PC PSARC files (e.g., `cooppois_p.psarc`)
- `rocksmith_pc_to_ps4_complete.py` from this repository

### Step 2: Convert PSARC to GP4

Open PowerShell in your working directory:

```powershell
python rocksmith_pc_to_ps4_complete.py cooppois_p.psarc poison_output "Poison by Alice Cooper"
```

**Output**:
```
Converting: cooppois_p.psarc
Content ID: EP0001-CUSA00745_00-RS00312AD2D71D4330EB
Title: Poison by Alice Cooper
Created param.sfo: 400 bytes
Created icon0.png: 68 bytes
Copied PSARC: cooppois_p.psarc
Created GP4: poison_output/cooppois_p.gp4

============================================================
CONVERSION COMPLETE!
============================================================
```

### Step 3: Build PKG

```powershell
C:\Path\To\LibOrbisPkg\PkgTool\bin\Release\netcoreapp3.0\PkgTool.exe pkg_build poison_output\cooppois_p.gp4 poison_output
```

**Expected Output**:
```
Building PKG...
Creating PFS filesystem...
Signing blocks...
Encrypting...
Done! Package created: poison_output\cooppois_p.pkg
```

### Step 4: Install on PS4

1. Copy `poison_output\cooppois_p.pkg` to a USB drive (FAT32 formatted)
2. Create folder structure on USB: `USB:\PS4\PACKAGES\`
3. Put the .pkg file there
4. On PS4, go to Package Installer
5. Install the PKG
6. Launch Rocksmith 2014 and enjoy!

---

## Batch Conversion Script

Create `convert_all.ps1` for converting multiple songs:

```powershell
# convert_all.ps1
param(
    [string]$PkgToolPath = "C:\Path\To\PkgTool.exe"
)

$psarcFiles = Get-ChildItem -Filter "*.psarc" -File

foreach ($psarc in $psarcFiles) {
    $baseName = $psarc.BaseName
    $outputDir = "output_$baseName"

    Write-Host "Converting: $($psarc.Name)" -ForegroundColor Cyan

    # Convert to GP4
    python rocksmith_pc_to_ps4_complete.py $psarc.Name $outputDir "Rocksmith2014 - $baseName"

    # Build PKG
    & $PkgToolPath pkg_build "$outputDir\$baseName.gp4" $outputDir

    Write-Host "Complete: $outputDir\$baseName.pkg" -ForegroundColor Green
}

Write-Host "`nAll conversions complete!" -ForegroundColor Green
```

**Usage**:
```powershell
.\convert_all.ps1 -PkgToolPath "C:\LibOrbisPkg\PkgTool\bin\Release\netcoreapp3.0\PkgTool.exe"
```

---

## Troubleshooting

### "python is not recognized"

**Fix**: Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### "dotnet is not recognized"

**Fix**: Restart PowerShell after installing .NET SDK
- Or add to PATH manually: `C:\Program Files\dotnet\`

### Build Error: "Could not find Windows SDK"

**Fix**: Use `dotnet build` instead of `msbuild`
```powershell
dotnet build --configuration Release
```

### PKG Error CE-34707-1

**Cause**: GP4 file has incorrect paths

**Fix**: Make sure you're using the Python converter which generates correct paths automatically

### PKG Error CE-34706-0

**Cause**: Didn't use PkgTool (used Python PKG builder instead)

**Fix**: Always use PkgTool.exe for the final PKG building step

---

## Directory Structure Example

```
C:\Rocksmith\
├── LibOrbisPkg\                           # Cloned repo
│   └── PkgTool\
│       └── bin\
│           └── Release\
│               └── netcoreapp3.0\
│                   └── PkgTool.exe        # Your tool
│
├── Converter\                             # Working directory
│   ├── rocksmith_pc_to_ps4_complete.py   # Converter script
│   ├── cooppois_p.psarc                  # Input PSARC
│   ├── boststar_p.psarc                  # Input PSARC
│   │
│   ├── poison_output\                     # Output
│   │   ├── cooppois_p.gp4                # GP4 project
│   │   ├── cooppois_p.pkg                # Final PKG ✅
│   │   └── build_dir\                    # Build files
│   │
│   └── boston_output\
│       ├── boststar_p.gp4
│       ├── boststar_p.pkg                # Final PKG ✅
│       └── build_dir\
│
└── USB_Drive\
    └── PS4\
        └── PACKAGES\
            ├── cooppois_p.pkg            # Copy here
            └── boststar_p.pkg            # Copy here
```

---

## Integration with RiffBridge GUI

After building PkgTool, update your GUI config:

```python
# In your config/settings
PKGTOOL_PATH = r"C:\LibOrbisPkg\PkgTool\bin\Release\netcoreapp3.0\PkgTool.exe"

# In your conversion code
import subprocess
from rocksmith_pc_to_ps4_complete import convert_pc_to_ps4

def build_pkg(gp4_file, output_dir):
    result = subprocess.run([
        PKGTOOL_PATH,
        "pkg_build",
        str(gp4_file),
        str(output_dir)
    ], capture_output=True, text=True)

    return result.returncode == 0
```

---

## Quick Reference Commands

```powershell
# One-time: Install .NET SDK
winget install Microsoft.DotNet.SDK.8

# One-time: Clone and build LibOrbisPkg
git clone https://github.com/maxton/LibOrbisPkg.git
cd LibOrbisPkg
dotnet build PkgTool\PkgTool.csproj --configuration Release

# For each song: Convert
python rocksmith_pc_to_ps4_complete.py song.psarc output "Song Title"

# For each song: Build PKG
.\PkgTool.exe pkg_build output\song.gp4 output

# Result: output\song.pkg ready to install!
```

---

## Next Steps After Build

1. ✅ Build PkgTool (you're doing this now)
2. ✅ Convert a test PSARC
3. ✅ Build test PKG
4. ✅ Test install on PS4
5. ✅ Integrate into RiffBridge GUI
6. ✅ Convert your entire Rocksmith library!

---

**Time to Complete**: ~15 minutes
**Result**: Fully working PC to PS4 DLC converter!

🎉 **You're almost there!**
