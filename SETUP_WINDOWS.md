# Windows Setup - Quick Start

## Step 1: Download the Python Converter

Save this content as `rocksmith_pc_to_ps4_complete.py` in your working directory (e.g., `C:\test\`):

You can get it from the repository:
https://github.com/rifftbridge/PS4/blob/claude/rocksmith-pc-ps4-converter-TlrD1/rocksmith_pc_to_ps4_complete.py

Or create it manually - see the file content in the repository.

## Step 2: Setup Your Working Directory

Create this structure:
```
C:\test\
├── rocksmith_pc_to_ps4_complete.py   ← The converter script
├── convert_song.bat                   ← Batch script (see below)
├── cooppois_p.psarc                   ← Your PC PSARC files
├── boststar_p.psarc
└── ... (more PSARC files)
```

## Step 3: Update convert_song.bat

Edit the `PKGTOOL` path in convert_song.bat to point to your actual PkgTool.Core.exe location:

```batch
set "PKGTOOL=C:\Path\To\Your\LibOrbisPkg\PkgTool.Core\bin\Release\netcoreapp3.0\PkgTool.Core.exe"
```

Replace with the actual path you found earlier.

## Step 4: Test It

```batch
cd C:\test
convert_song.bat cooppois_p.psarc "Poison by Alice Cooper"
```

## Troubleshooting

### Python script not found
- Make sure `rocksmith_pc_to_ps4_complete.py` is in the same directory as your batch file
- Check the filename is exactly `rocksmith_pc_to_ps4_complete.py` (no .txt extension)

### PkgTool not found
- Update the PKGTOOL path in convert_song.bat
- Or use the full path in the command

### No .pkg created
- Check if the GP4 was created: `dir cooppois_p_ps4\cooppois_p.gp4`
- If no GP4, the Python script failed
- If GP4 exists but no PKG, PkgTool failed
