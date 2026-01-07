# RiffBridge Build Files Checklist

## Core Application Files (REQUIRED)

### Python Source Files
- **rocksmith_gui.py** - Main GUI application
- **enhanced_converter.py** - Enhanced PC to PS4 converter with Steam integration
- **rocksmith_pc_to_ps4.py** - Base converter module
- **steam_dlc_database.py** - Steam API integration for DLC metadata
- **ps4_pkg_builder.py** - Python-based PKG builder

### Configuration Files
- **RiffBridge.spec** - PyInstaller build configuration
- **requirements.txt** - Runtime dependencies (UPDATED with latest versions)
- **requirements-dev.txt** - Development/build dependencies
- **ps4_content_id_mapping.json** - Official PS4 Content ID mappings (NEW - fixes CE-34707-1)

### Assets
- **RiffBridge_icon.ico** - Application icon
- **Riff_Bridge_cover_art.jpg** - Artwork displayed in GUI

---

## Build Dependencies

### Python Packages (Install First)
```bash
pip install -r requirements-dev.txt
```

This installs:
- **tkinterdnd2** ≥0.4.3 - Drag-and-drop GUI support
- **pillow** ≥12.1.0 - Image processing
- **requests** ≥2.32.5 - HTTP/Steam API
- **pyinstaller** ≥6.17.0 - Executable builder

---

## How to Build

### Option 1: Using PyInstaller (Recommended)

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Build the executable
pyinstaller RiffBridge.spec

# Output will be in: dist/RiffBridge.exe
```

### Option 2: Quick Build Script

```bash
# Windows
BUILD_COMPLETE.bat

# This runs PyInstaller and creates the executable
```

---

## Complete File List for Distribution

After building, distribute these files together:

### Essential Files for End Users
```
RiffBridge.exe                       # The built application (in dist/ folder)
ps4_content_id_mapping.json          # Content ID database (place next to .exe)
PKGTool.exe                          # PS4 PKG building tool (optional, improves compatibility)
README_CONTENT_ID_FIX.md             # Quick fix guide for CE-34707-1 errors
```

### Optional but Recommended
```
CONTENT_ID_FIX.md                    # Detailed troubleshooting guide
QUICK_SETUP.txt                      # Setup instructions
```

---

## Files Included in the .exe (Bundled by PyInstaller)

The following files are embedded inside RiffBridge.exe:
- All Python source files (.py)
- tkinterdnd2 library
- PIL/Pillow libraries
- requests library
- RiffBridge_icon.ico
- Riff_Bridge_cover_art.jpg

---

## External Files Needed at Runtime

These files must be in the same directory as RiffBridge.exe:

### Required
- **ps4_content_id_mapping.json** - For official Content ID lookup
  * Place next to RiffBridge.exe
  * Users can edit this to add their DLC mappings

### Optional (Enhances Functionality)
- **PKGTool.exe** - Windows PKG builder
  * Place in same directory as RiffBridge.exe OR
  * Add to system PATH OR
  * Specify location in GUI settings

- **orbis-pub-cmd.exe** - Alternative PKG builder (Sony official tools)
  * If you have access to Sony's tools

---

## Build Output Structure

```
PS4/
├── dist/
│   └── RiffBridge.exe              ← Main executable (distribute this)
├── build/                          ← Temporary build files (can delete)
└── work/                           ← Temporary conversion files (auto-created)
```

---

## Minimal Distribution Package

For end users, create a ZIP with:

```
RiffBridge-v1.0/
├── RiffBridge.exe
├── ps4_content_id_mapping.json
├── PKGTool.exe (optional)
├── README_CONTENT_ID_FIX.md
└── QUICK_SETUP.txt
```

---

## Development Files (NOT needed for building)

These are documentation/debug files, not required for the build:
- TEST_*.py - Test scripts
- *_FIX.txt, *_INTEGRATED.txt - Development notes
- psarc_checker.py - Diagnostic tool
- requirements_gui.txt - Old requirements file (use requirements.txt instead)

---

## Important Notes

### Content ID Mapping File
**NEW REQUIREMENT:** The `ps4_content_id_mapping.json` file is essential for fixing CE-34707-1 errors. Users need to:
1. Keep this file next to RiffBridge.exe
2. Add official Content IDs from https://serialstation.com/titles/CUSA/00745
3. Edit the JSON to add their DLC mappings

### PKG Building Tools
The application will work with:
- **Python-based PKG builder** (built-in, always available)
- **PKGTool.exe** (optional, Windows-only, better compatibility)
- **orbis-pub-cmd.exe** (optional, requires Sony dev tools)

### Platform Support
- **Windows**: Full support with PyInstaller
- **Linux/Mac**: Run from source (Python 3.8+)

---

## Quick Build Commands

```bash
# 1. Install dependencies
pip install -r requirements-dev.txt

# 2. Build executable
pyinstaller RiffBridge.spec

# 3. Test the build
dist/RiffBridge.exe

# 4. Create distribution package
mkdir RiffBridge-Release
copy dist\RiffBridge.exe RiffBridge-Release\
copy ps4_content_id_mapping.json RiffBridge-Release\
copy PKGTool.exe RiffBridge-Release\
copy README_CONTENT_ID_FIX.md RiffBridge-Release\
copy QUICK_SETUP.txt RiffBridge-Release\
```

---

## Troubleshooting Build Issues

### Missing modules error
```bash
# Re-install dependencies
pip install --upgrade -r requirements-dev.txt
```

### PyInstaller not found
```bash
pip install pyinstaller>=6.17.0
```

### Icon not embedded
- Verify RiffBridge_icon.ico exists
- Check RiffBridge.spec has correct icon path

### Import errors in built exe
- Check hiddenimports in RiffBridge.spec
- Test in clean environment

---

## Summary

**Minimum files needed to BUILD:**
1. All 5 Python source files (.py)
2. RiffBridge.spec
3. RiffBridge_icon.ico
4. Riff_Bridge_cover_art.jpg
5. requirements-dev.txt (to install dependencies)
6. ps4_content_id_mapping.json (NEW)

**Minimum files needed to DISTRIBUTE:**
1. RiffBridge.exe (from dist/ folder after build)
2. ps4_content_id_mapping.json
3. README_CONTENT_ID_FIX.md (user guide)

The executable is self-contained and includes all Python dependencies!
