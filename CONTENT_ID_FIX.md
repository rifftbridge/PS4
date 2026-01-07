# Fixing PS4 Content ID Error (CE-34707-1)

## The Problem

When trying to install converted DLC packages on a jailbroken PS4, you may encounter:

```
An error has occurred (CE-34707-1)
```

**Root Cause:** The PKG file contains an incorrect Content ID. The PS4 firmware checks Content IDs against Sony/Ubisoft's official DLC database, and generated/random IDs are rejected.

---

## The Solution

### Understanding Content IDs

Every official Rocksmith 2014 DLC has a specific Content ID assigned by Sony/Ubisoft:

**Format:** `REGION-CUSA00745_00-XXXXXXXXXXXXXXXX`

- **REGION**: Region code (EP0001=Europe, UP0001=USA, etc.)
- **CUSA00745**: Rocksmith 2014 Remastered Title ID
- **_00**: DLC indicator
- **XXXXXXXXXXXXXXXX**: 16-character unique identifier for the DLC

**Example:** `EP0001-CUSA00745_00-RS0020000000SONG`

---

## How to Fix

### Method 1: Use the Official Content ID (Recommended)

**Step 1:** Find the official Content ID

1. Visit SerialStation: https://serialstation.com/titles/CUSA/00745
2. Search for your DLC song
3. Copy the **Content ID** exactly as shown

**Step 2:** Convert with the correct Content ID

```bash
# Using enhanced_converter.py
python enhanced_converter.py song.psarc ./output \
  --content-id EP0001-CUSA00745_00-RS0020000000SONG \
  --region EP0001

# Using rocksmith_gui.py
# Paste the Content ID in the "Custom Content ID" field before converting
```

**Step 3:** Install the PKG on your PS4

The PKG filename will match the Content ID:
```
EP0001-CUSA00745_00-RS0020000000SONG.pkg
```

---

### Method 2: Update the Mapping Database

For frequently converted DLCs, add them to `ps4_content_id_mapping.json`:

```json
{
  "mappings": [
    {
      "steam_app_id": "222120",
      "song_code": "AliceCooper",
      "artist": "Alice Cooper",
      "song": "Poison",
      "content_id": "EP0001-CUSA00745_00-RS002000POISONALC",
      "region": "EP"
    }
  ]
}
```

The converter will automatically use these mappings when it detects the Steam App ID or song code.

---

### Method 3: Custom/Unofficial Songs

For custom songs NOT in the official database:

1. **Use a unique custom Content ID format:**
   ```
   EP0001-CUSA00745_00-CUSTOM0000000001
   EP0001-CUSA00745_00-CUSTOM0000000002
   etc.
   ```

2. **Keep a record of used IDs** to avoid conflicts

3. **Important:** Custom songs may work but won't appear in the official DLC list

---

## Region Codes

Choose the correct region for your PS4:

| Region | Code | Description |
|--------|------|-------------|
| Europe | EP0001 | SCEE (Sony Computer Entertainment Europe) |
| USA | UP0001 | SCEA (Sony Computer Entertainment America) |
| Japan | JP0001 | SCEJ (Sony Computer Entertainment Japan) |
| Asia | HP0001 | SCEH (Sony Computer Entertainment Hong Kong) |

**Note:** Most jailbroken PS4s can install any region, but match your game region when possible.

---

## Troubleshooting

### Error: CE-34707-1 (Content ID mismatch)
- **Cause:** Incorrect or generated Content ID
- **Fix:** Use the official Content ID from SerialStation

### Error: CE-34788-0 (Already installed)
- **Cause:** A package with that Content ID is already installed
- **Fix:** Uninstall the existing DLC first, or use a different Content ID

### Error: CE-30002-5 (PKG corrupted)
- **Cause:** PKG file is corrupted or incomplete
- **Fix:** Re-build the PKG, verify file integrity

### PKG installs but doesn't appear in game
- **Cause 1:** Content ID doesn't match any official DLC
- **Cause 2:** Song files are corrupted or incompatible
- **Fix:** Verify you're using the official Content ID and source files are correct

---

## Finding Content IDs

### Official DLC (Recommended Source)

**SerialStation Database:**
- URL: https://serialstation.com/titles/CUSA/00745
- Shows all official Rocksmith 2014 DLC with Content IDs
- Most reliable source

**PSN Store (Alternative):**
- Search for the DLC on the PS4 PSN Store
- Some homebrew tools can extract Content IDs from PKG files

### Extracting from Existing PKG Files

If you have official PKG files, you can extract the Content ID:

```python
# Quick Python script to read Content ID from PKG
with open('dlc.pkg', 'rb') as f:
    f.seek(0x40)  # Content ID is at offset 0x40
    content_id = f.read(36).decode('ascii').rstrip('\x00')
    print(f"Content ID: {content_id}")
```

Or using hexdump:
```bash
hexdump -C dlc.pkg | head -10
# Look at offset 0x40-0x63 for the Content ID string
```

---

## Updated Converter Behavior

### Priority Order (when auto-generating Content IDs)

1. **User-specified Content ID** (via `--content-id` parameter) ← HIGHEST PRIORITY
2. **Mapping database** (`ps4_content_id_mapping.json`)
3. **Steam App ID detection** (generates: `REGION-CUSA00745_00-APPID###########`)
4. **Hash-based fallback** (generates: `REGION-CUSA00745_00-MD5HASH#########`)

⚠️ **Warning:** Options 3 and 4 generate Content IDs that will likely cause CE-34707-1 errors!

### Best Practice

**Always specify the official Content ID** using one of these methods:
- Command line: `--content-id EP0001-CUSA00745_00-OFFICIAL0000ID00`
- GUI: Enter in "Custom Content ID" field
- Mapping file: Add to `ps4_content_id_mapping.json`

---

## Example Workflow

### Converting a Known Official DLC

```bash
# 1. Find the DLC on SerialStation
#    Example: Alice Cooper - Poison
#    Content ID: EP0001-CUSA00745_00-RS002000ALICECOOP

# 2. Convert with correct Content ID
python enhanced_converter.py "Alice_Cooper_Poison.psarc" ./output \
  --content-id EP0001-CUSA00745_00-RS002000ALICECOOP \
  --region EP0001

# 3. Install on PS4
#    File: EP0001-CUSA00745_00-RS002000ALICECOOP.pkg
#    Should install without CE-34707-1 error
```

### Converting a Custom Song

```bash
# For unofficial/custom songs, use CUSTOM prefix
python enhanced_converter.py "Custom_Song.psarc" ./output \
  --content-id EP0001-CUSA00745_00-CUSTOM0000000001 \
  --region EP0001

# Keep a list of your custom IDs to avoid duplicates
```

---

## Batch Converting Official DLCs

Create a mapping file with all your DLCs, then convert in batch:

**1. Create `my_dlc_batch.json`:**
```json
[
  {
    "file": "AliceCooper_Poison.psarc",
    "content_id": "EP0001-CUSA00745_00-RS002000ALICECOOP"
  },
  {
    "file": "BlackKeys_GoldOnCeiling.psarc",
    "content_id": "EP0001-CUSA00745_00-RS002000BLACKKEY"
  }
]
```

**2. Use the GUI batch conversion feature** or script it:
```bash
for dlc in *.psarc; do
  # Look up Content ID from your mapping
  content_id=$(jq -r ".[] | select(.file==\"$dlc\") | .content_id" my_dlc_batch.json)
  python enhanced_converter.py "$dlc" ./output --content-id "$content_id"
done
```

---

## Summary

✅ **DO:**
- Use official Content IDs from SerialStation
- Maintain a mapping database for your DLC collection
- Use unique CUSTOM prefixes for unofficial songs
- Match your PS4 region code

❌ **DON'T:**
- Use auto-generated Content IDs for official DLCs
- Reuse Content IDs across different songs
- Skip verifying Content IDs before installing

**Remember:** The Content ID is like a serial number - it must be correct for the PS4 to accept the package!

---

## Need Help?

If you're still getting CE-34707-1 errors:

1. **Verify your Content ID** matches SerialStation exactly
2. **Check your region code** (EP vs UP vs JP)
3. **Ensure no duplicate** Content IDs are installed
4. **Try a different song** to isolate the issue
5. **Check PKG file integrity** (not corrupted)

For official DLC Content IDs, SerialStation is the most reliable source:
https://serialstation.com/titles/CUSA/00745
