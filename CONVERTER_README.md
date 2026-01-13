# Rocksmith PC to PS4 Converter

**Complete standalone converter for Rocksmith 2014 DLC**

Converts PC .psarc files to PS4 .pkg installers for jailbroken PS4 consoles.

## Features

✓ **No external tools required** - Pure Python implementation
✓ **Single file converter** - Everything in one script
✓ **Automatic metadata generation** - Creates proper param.sfo and icon files
✓ **Valid PKG format** - Generates installable PS4 packages

## Requirements

- Python 3.7 or higher
- PC Rocksmith 2014 DLC (.psarc files)
- Jailbroken PS4 (firmware 9.00+)

## Usage

### Basic Conversion

```bash
python rocksmith_to_ps4.py input.psarc output.pkg
```

### With Custom Title

```bash
python rocksmith_to_ps4.py cooppois_p.psarc poison.pkg --title "Poison by Alice Cooper"
```

### With Custom Content ID

```bash
python rocksmith_to_ps4.py song.psarc song.pkg --content-id "EP0001-CUSA00745_00-MYCUSTOMID000001"
```

### Region Codes

- `EP0001` - Europe (default)
- `UP0001` - USA
- `JP0001` - Japan

```bash
python rocksmith_to_ps4.py song.psarc song.pkg --region UP0001
```

## Installation on PS4

1. Copy the generated `.pkg` file to a USB drive (formatted as FAT32 or exFAT)
2. Insert USB drive into PS4
3. Go to **Settings** → **Package Installer**
4. Select the PKG file and install
5. Launch Rocksmith 2014 - the DLC will appear in your song list

## Technical Details

### PKG Format

The converter creates "fake PKG" files compatible with jailbroken PS4 consoles:

- **PKG Type**: 0x00000001 (Fake/Homebrew)
- **Content Type**: 0x0000001B (Additional Content/DLC)
- **DRM Type**: 0x0000000F (PS4)

### File Structure

Generated PKG contains:
- `param.sfo` - PS4 metadata (title, content ID, etc.)
- `icon0.png` - 512x512 icon (minimal PNG)
- PSARC data - The actual DLC content

### Content ID Format

`REGION-TITLEID_00-UNIQUEID16CHARS`

Example: `EP0001-CUSA00745_00-RS002SONG0001059`

- `EP0001` = Europe region
- `CUSA00745` = Rocksmith 2014 Title ID
- `RS002SONG0001059` = Unique 16-character identifier

## Tested With

✓ Alice Cooper - Poison (cooppois_p.psarc)
✓ Steam App ID: 899802
✓ Working Content ID: EP0001-CUSA00745_00-RS002SONG0001059

## Troubleshooting

### Error: CE-34707-1 on PS4

This error means corrupted PKG. Causes:
- Incorrect file paths in source
- Wrong Content ID format
- Missing required metadata

**Solution**: Ensure your .psarc file is valid and try regenerating the PKG.

### PKG Won't Install

- Check PS4 firmware is jailbroken (9.00+)
- Verify USB drive format (FAT32 or exFAT)
- Try a different USB port
- Regenerate PKG with different Content ID

### DLC Doesn't Appear in Rocksmith

- Ensure PKG installed successfully
- Restart Rocksmith 2014
- Check Content ID doesn't conflict with existing DLC

## Known Limitations

- **Jailbroken PS4 only** - Does not work on official firmware
- **Basic icon** - Uses minimal PNG (install PIL for better icons)
- **No encryption** - Fake PKG format (adequate for homebrew)

## Advanced Options

```bash
# All options
python rocksmith_to_ps4.py INPUT OUTPUT \
  --title "Song Title" \
  --content-id "EP0001-CUSA00745_00-CUSTOMID00000001" \
  --title-id "CUSA00745" \
  --region "EP0001" \
  --quiet
```

## Source Files

- `rocksmith_to_ps4.py` - Main converter (standalone)
- `analyze_pkg.py` - PKG file analyzer tool
- `analyze_psarc.py` - PSARC file analyzer tool

## Credits

- Based on LibOrbisPkg PKG format specification
- PS4 PKG binary template (PS4PKG.bt)
- Rocksmith2014.NET PSARC implementation
- Analysis of working PKG from Arczi

## License

MIT License - Free to use and modify

## Disclaimer

This tool is for educational purposes and personal use only. Only use with DLC you legally own. The author does not condone piracy.

---

**Version**: 1.0
**Created**: January 2026
**Built with**: Claude Code
