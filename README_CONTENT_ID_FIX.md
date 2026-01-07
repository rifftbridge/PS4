# RiffBridge - Content ID Fix for PS4 Installation

## Quick Fix for CE-34707-1 Error

If you're getting **error CE-34707-1** when installing PKG files on your PS4, the Content ID is incorrect.

---

## The Fix

### Option 1: Manual Content ID (Fastest)

**Step 1:** Find the official Content ID at https://serialstation.com/titles/CUSA/00745

**Step 2:** Convert with the correct ID:

```bash
python enhanced_converter.py song.psarc ./output --content-id EP0001-CUSA00745_00-RS0020000000SONG
```

Replace `EP0001-CUSA00745_00-RS0020000000SONG` with the actual Content ID from SerialStation.

---

### Option 2: Use Mapping Database (Best for Multiple DLCs)

**Step 1:** Add your DLCs to `ps4_content_id_mapping.json`:

```json
{
  "mappings": [
    {
      "steam_app_id": "222120",
      "song_code": "AliceCooper",
      "artist": "Alice Cooper",
      "song": "Poison",
      "content_id": "EP0001-CUSA00745_00-ACTUAL_ID_HERE",
      "region": "EP"
    }
  ]
}
```

**Step 2:** Convert normally - the tool will auto-detect and use the official ID:

```bash
python enhanced_converter.py song.psarc ./output
```

The converter will now:
1. ✓ Check the mapping database for official IDs
2. ✓ Use the official ID automatically if found
3. ⚠ Warn you if generating an ID (which likely won't work)

---

## What Changed?

### Before (Generated IDs - didn't work):
- Auto-generated Content IDs based on Steam App ID or hash
- Result: **CE-34707-1 error** on PS4

### After (Official IDs - works):
- **Prioritizes official Content IDs** from mapping database
- Warns when generating IDs that may not work
- Clear instructions on how to fix

---

## Conversion Priority Order

The converter now uses this priority:

1. **User-specified ID** (`--content-id` parameter) ← **Highest Priority**
2. **Mapping database** (`ps4_content_id_mapping.json`)
3. **Generated from Steam App ID** (⚠ warning shown)
4. **Generated from hash/song code** (⚠ warning shown) ← **Lowest Priority**

---

## Finding Official Content IDs

### SerialStation (Recommended)
- URL: https://serialstation.com/titles/CUSA/00745
- Complete list of all Rocksmith 2014 DLC with Content IDs

### From Existing PKG Files
```bash
# Extract Content ID from an official PKG
hexdump -C official_dlc.pkg | head -10
# Look at offset 0x40 for the Content ID string
```

---

## Examples

### Example 1: Single DLC Conversion
```bash
# Find Content ID from SerialStation first
python enhanced_converter.py "Alice_Cooper_Poison.psarc" ./output \
  --content-id EP0001-CUSA00745_00-RS002000ALICECOOP
```

### Example 2: Batch with Mapping File
```json
// ps4_content_id_mapping.json
{
  "mappings": [
    {
      "steam_app_id": "222120",
      "content_id": "EP0001-CUSA00745_00-RS002000ALICECOOP"
    },
    {
      "steam_app_id": "222121",
      "content_id": "EP0001-CUSA00745_00-RS002000BLACKKEY"
    }
  ]
}
```

Then just convert normally:
```bash
python enhanced_converter.py *.psarc ./output
# The tool auto-detects Steam App IDs and uses the correct Content IDs
```

### Example 3: Custom/Unofficial Song
```bash
# For custom songs not in SerialStation, use CUSTOM prefix
python enhanced_converter.py "My_Custom_Song.psarc" ./output \
  --content-id EP0001-CUSA00745_00-CUSTOM0000000001
```

---

## Warning Messages

When converting, you may see:

### ✓ Good (Will Work)
```
✓ Using OFFICIAL Content ID from mapping database
Final Content ID: EP0001-CUSA00745_00-RS002000ALICECOOP
```
This PKG will install correctly on PS4!

### ⚠ Warning (May Not Work)
```
⚠ WARNING: Generated Content ID - may cause CE-34707-1 error on PS4!
⚠ Add official Content ID to ps4_content_id_mapping.json for this DLC
Final Content ID: EP0001-CUSA00745_00-APPID22212000000
```
This PKG will **likely fail** with CE-34707-1. Get the official ID!

---

## Files Added

1. **`ps4_content_id_mapping.json`** - Database of official Content IDs
2. **`CONTENT_ID_FIX.md`** - Detailed troubleshooting guide
3. **`README_CONTENT_ID_FIX.md`** - This quick reference
4. **Updated `enhanced_converter.py`** - Now checks mapping database

---

## Region Codes

| Your PS4 Region | Use This Code |
|----------------|---------------|
| Europe (EU) | EP0001 |
| USA/Americas | UP0001 |
| Japan | JP0001 |
| Asia | HP0001 |

Most jailbroken PS4s accept any region, but match your game region when possible.

---

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| CE-34707-1 | Wrong Content ID | Use official ID from SerialStation |
| CE-34788-0 | Already installed | Uninstall existing DLC first |
| CE-30002-5 | Corrupted PKG | Re-build the PKG file |
| Installs but not in game | Wrong ID or corrupt files | Verify Content ID and source files |

---

## Quick Checklist

- [ ] Find your DLC on https://serialstation.com/titles/CUSA/00745
- [ ] Copy the exact Content ID
- [ ] Add to `ps4_content_id_mapping.json` OR use `--content-id` parameter
- [ ] Convert your PSARC
- [ ] Install on PS4 (should work now!)

---

## Need More Help?

See **CONTENT_ID_FIX.md** for:
- Detailed troubleshooting
- How to extract IDs from existing PKGs
- Custom song guidelines
- Batch conversion workflows
