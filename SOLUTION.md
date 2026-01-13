# Rocksmith 2014 PC to PS4 DLC Converter - Complete Solution

## 🎸 Overview

This project provides a complete working solution to convert Rocksmith 2014 PC DLC (PSARC files) to PS4 PKG format for installation on jailbroken PS4 consoles running GoldHEN.

**Status**: ✅ **WORKING** - Successfully tested on PS4 11.00 with GoldHEN

---

## 📋 Requirements

### Software Requirements

1. **Python 3.7+** - For running converter scripts
2. **LibOrbisPkg PkgTool.Core.exe** - For building proper PS4 PKG files with PFS encryption
   - Download: [LibOrbisPkg Releases](https://github.com/maxton/LibOrbisPkg/releases)
   - Required for creating installable fake PKGs

3. **PS4 Requirements**:
   - Jailbroken PS4 (firmware 11.00 or compatible)
   - GoldHEN 2.4b17 or higher
   - Rocksmith 2014 Remastered (CUSA00745)

### Input Files

- **PC PSARC files** (Rocksmith DLC files)
- Can be from:
  - Official PC DLC
  - Custom DLC (CDLC) from CustomsForge
  - Extracted from existing PKG files

---

## 🚀 Quick Start

### Single File Conversion

```powershell
cd C:\PS4\final_test
.\convert_song.bat "path\to\song.psarc" "Song Title by Artist"
```

### Batch Conversion

```powershell
python batch_convert_dlc.py "C:\Rocksmith\DLC" "C:\PS4\output"
```

Or use the batch file:

```powershell
.\batch_convert_dlc.bat "C:\Rocksmith\DLC" "C:\PS4\output"
```

---

## 📁 Project Structure

```
PS4/
├── rocksmith_pc_to_ps4_complete.py    # Core converter (creates GP4, param.sfo)
├── ps4_pkg_builder.py                 # Simple PKG builder (for reference)
├── convert_psarc_to_pc_format.py      # Format converter (Steam→PC)
├── batch_convert_dlc.py               # Batch conversion script
├── batch_convert_dlc.bat              # Windows batch wrapper
├── final_test/
│   ├── convert_song.bat               # Single file converter
│   ├── CoopPois_from_working_pkg.psarc # Test file (example)
│   └── build_dir/                     # Temp build directory
└── tools/
    └── LibOrbisPkg/
        └── PkgTool.Core.exe           # LibOrbisPkg tool
```

---

## 🔧 How It Works

### Conversion Pipeline

```
PSARC File
    ↓
[1] rocksmith_pc_to_ps4_complete.py
    ├─→ Generates Content ID (EP0001-CUSA00745_00-RS00XXXXXXXXXXXX)
    ├─→ Creates param.sfo (972 bytes with PUBTOOLINFO/PUBTOOLVER)
    ├─→ Copies icon0.png (if available)
    ├─→ Creates GP4 project file
    ↓
[2] PkgTool.Core.exe (LibOrbisPkg)
    ├─→ Creates inner PFS (DLC files)
    ├─→ Creates outer PFS (encrypted container)
    ├─→ Signs and encrypts
    ├─→ Calculates SHA256
    ↓
PS4 PKG File (ready for installation)
```

### Key Technical Details

1. **Content ID Format**: `EP0001-CUSA00745_00-RS00XXXXXXXXXXXX`
   - Fixed prefix: `EP0001-CUSA00745_00-RS00`
   - Unique ID: 12-character MD5 hash of PSARC filename
   - Total length: 36 characters (required by PS4)

2. **param.sfo Structure**:
   - 9 entries (not 7) - includes PUBTOOLINFO and PUBTOOLVER
   - Little-endian format
   - Total size: 972 bytes
   - CATEGORY: "ac" (additional content)
   - FORMAT: "obs" (observed)

3. **Directory Structure**:
   ```
   /Sc0/
   ├── param.sfo
   └── icon0.png
   /Image0/
   ├── DLC/
   │   └── [song].psarc
   └── sce_sys/  (empty directory)
   ```

4. **PFS Encryption**:
   - Inner PFS: Contains DLC files
   - Outer PFS: Encrypted container with fake PKG keys
   - Signed with modified keys for GoldHEN compatibility

---

## 🎯 Installation on PS4

1. **Copy PKG to USB Drive**:
   ```
   USB:\PS4\PACKAGES\EP0001-CUSA00745_00-RS00XXXXXXXXXXXX.pkg
   ```

2. **Install on PS4**:
   - Settings → Debug Settings → Game → Package Installer
   - Select the PKG file
   - Install

3. **Launch Rocksmith 2014**:
   - Songs should appear in DLC list
   - Ready to play!

---

## 📚 Credits and Acknowledgments

This project builds upon the excellent work of many developers in the PS4 homebrew community:

### Core Tools Used

1. **[LibOrbisPkg](https://github.com/maxton/LibOrbisPkg)** by [@maxton](https://github.com/maxton)
   - Core library for creating PS4 PKG files
   - PkgTool.Core.exe for building proper PFS-encrypted PKGs
   - Essential for creating installable fake PKGs
   - License: LGPL v3

2. **[GoldHEN](https://github.com/GoldHEN/GoldHEN)** by [@SiSTR0](https://github.com/SiSTRo)
   - PS4 jailbreak payload
   - Enables installation of fake PKGs
   - License: GPL v3

3. **[PkgToolBox](https://github.com/seregonwar/PkgToolBox)** by [@seregonwar](https://github.com/seregonwar)
   - Reference implementation for PKG manipulation
   - Includes orbis-pub-cmd.exe integration
   - Used for research and validation

### Research and Documentation

- **[PS4DevWiki](https://www.psdevwiki.com/)** - PS4 file format documentation
- **[OpenOrbis](https://github.com/OpenOrbis/OpenOrbis-PS4-Toolchain)** - PS4 development toolchain
- **PS4 PKG format research** by flatz and the PS4 homebrew community
- **[CustomsForge](https://customsforge.com/)** - Rocksmith custom DLC community

### Special Thanks

- **Arczi** - For creating working PS4 DLC PKG files that served as reference
- **The PS4 Homebrew Community** - For reverse engineering PS4 file formats
- **Rocksmith Community** - For keeping the game alive with custom content

---

## ⚖️ License

This project's source code is released under the **MIT License**:

```
MIT License

Copyright (c) 2026 Rocksmith PC to PS4 Converter Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Note**: This license applies to the converter scripts in this repository. The tools we use (LibOrbisPkg, GoldHEN, etc.) are subject to their own licenses.

---

## ⚠️ Important Notes

### Legal Disclaimer

This tool is for **educational purposes** and for converting legally owned DLC to work on jailbroken PS4 consoles. Users are responsible for ensuring they own the content they convert.

### Content Policy

- ❌ **No PSARC/PKG files included** in this repository
- ❌ **No copyrighted song files** shared
- ✅ **Source code only** - users must provide their own DLC files
- ✅ Designed for **legally owned content**

### Limitations

- Only works on **jailbroken PS4** with GoldHEN
- Requires **Rocksmith 2014 Remastered** (CUSA00745)
- PC/Steam DLC formats supported
- May not work with all custom formats

---

## 🐛 Troubleshooting

### Common Issues

**1. PKG doesn't install (CE-34707-1)**
- **Cause**: Using simplified Python PKG builder instead of LibOrbisPkg
- **Solution**: Use PkgTool.Core.exe from LibOrbisPkg for proper PFS encryption

**2. PKG installs but song doesn't appear**
- **Cause**: Wrong Content ID (BLES01862 instead of CUSA00745)
- **Solution**: Ensure using CUSA00745 in Content ID

**3. PKG installs but song doesn't appear (directory structure)**
- **Cause**: MOGI directory prefix in PKG structure
- **Solution**: Use `/Sc0/` and `/Image0/DLC/` (no prefix)

**4. Missing LibOrbisPkg.Core.dll**
- **Cause**: Incomplete LibOrbisPkg installation
- **Solution**: Download complete release from GitHub

---

## 📖 Technical Background

### Why This Works

Rocksmith 2014 on PS4 loads DLC from:
1. **Content ID**: Must match `EP0001-CUSA00745_00-*` pattern
2. **Directory**: `/Image0/DLC/*.psarc`
3. **param.sfo**: Must have PUBTOOLINFO and PUBTOOLVER fields

The working Arczi PKGs provided the reference structure. By analyzing them, we identified:
- Correct Content ID format
- Required param.sfo fields (9 entries, 972 bytes)
- Proper directory structure (no MOGI prefix)
- Need for PFS encryption (via LibOrbisPkg)

### Evolution of the Solution

1. **Initial Attempts**: Simple Python PKG builder → CE-34707-1 error
2. **TheBigMac Testing**: Proper PKGs but wrong Title ID (BLES01862) → Installed but invisible
3. **LibOrbisPkg Integration**: Proper PFS + Correct Content ID + Correct structure → **SUCCESS**

---

## 🔮 Future Improvements

- [ ] GUI application for easier conversion
- [ ] Automatic icon generation from album art
- [ ] Batch conversion progress tracking
- [ ] Integration with CustomsForge API
- [ ] Support for other rhythm games

---

## 📞 Support and Community

- **GitHub Issues**: For bug reports and feature requests
- **CustomsForge Forums**: For Rocksmith custom content discussion
- **PS4 Homebrew Discord**: For PS4 jailbreak questions

---

## 📜 Version History

### v1.0.0 (January 2026)
- ✅ Initial working solution
- ✅ Single file conversion
- ✅ Batch conversion support
- ✅ Complete documentation
- ✅ Tested on PS4 11.00 GoldHEN

---

**Made with ❤️ for the Rocksmith and PS4 Homebrew communities**

*"Keep rockin' on PS4!"* 🎸
