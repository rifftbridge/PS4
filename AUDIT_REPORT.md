# RiffBridge Codebase Audit Report

**Auditor:** Claude Opus 4.6
**Date:** 2026-02-12
**Scope:** Full codebase review of the RiffBridge Rocksmith 2014 PC-to-PS4 converter
**Commit:** 9056149 (HEAD of main)

---

## Executive Summary

RiffBridge is a ~2,900-line Python application with a Tkinter GUI that converts Rocksmith 2014 PC DLC (.psarc) to PS4 .pkg format. The project was authored by a graphic designer with AI assistance (Claude) and is explicitly stated as **"not actually working"** as of 7 January 2026.

This audit found **7 critical bugs**, **3 security issues**, **6 correctness/format problems**, and **12 code quality concerns**. The two most significant findings are:

1. The **param.sfo generator** has multiple structural bugs that produce malformed files (wrong data types, wrong offsets).
2. The **PKG builder** produces a simplified structure that omits required PS4 PKG components (PFS image, digests, mount image), making generated PKGs non-installable even on homebrew firmware.

---

## 1. Critical Bugs

### BUG-01: `self` used in standalone function (crash on startup)

**File:** `rocksmith_gui.py:886-892`
**Severity:** Critical (application crash)

The `main()` function references `self.root` but is a standalone function, not a class method. If the icon-loading code at lines 886-892 executes, it will raise `NameError: name 'self' is not defined`.

```python
def main():
    root = TkinterDnD.Tk()
    try:
        if sys.platform == 'win32':
            self.root.iconbitmap('RiffBridge.ico')  # BUG: 'self' undefined
        else:
            icon_img = tk.PhotoImage(file='RiffBridge_512.png')
            self.root.iconphoto(True, icon_img)     # BUG: 'self' undefined
    except Exception as e:
        pass  # Silently caught, so startup continues
```

**Impact:** Currently masked by the bare `except` clause. The icon silently fails to load. If the exception handler were removed, the application would crash on startup.

**Fix:** Replace `self.root` with `root`.

---

### BUG-02: Thread-safety violation in Tkinter GUI

**File:** `rocksmith_gui.py:674-679` (called from thread at lines 556-648)
**Severity:** Critical (intermittent crash / UI corruption)

The `log_message()` method directly modifies Tkinter widgets (`self.log_text`) but is called from the worker thread in `run_conversions()`. Tkinter is not thread-safe; all widget mutations must happen on the main thread.

The code correctly uses `self.root.after(0, ...)` for `file_tree.item()` updates but calls `self.log_message()` directly from the thread without marshaling.

```python
# In run_conversions() (worker thread):
self.log_message(f"\n[{i}/{total}] Processing: {job.input_file.name}", 'info')  # UNSAFE
# vs:
self.root.after(0, self.file_tree.item, item_id, ...)  # SAFE
```

**Impact:** Race conditions can cause intermittent crashes, frozen UI, or corrupted text output. This is the classic Tkinter threading bug.

**Fix:** All `self.log_message()` calls within `run_conversions()` should be wrapped in `self.root.after(0, self.log_message, ...)`.

---

### BUG-03: param.sfo data_table_start offset is wrong

**File:** `rocksmith_pc_to_ps4.py:76-80`
**Severity:** Critical (produces malformed SFO files)

The `data_table_start` is calculated **before** alignment padding is added to `key_data`:

```python
data_table_start = key_table_start + len(key_data)  # Line 76: calculated here

# Align to 4 bytes                                    # Lines 78-80: THEN padding added
while len(key_data) % 4 != 0:
    key_data += b'\x00'
```

The SFO header at line 88 is written with the **pre-padding** offset, but the actual data table starts after the padded key table. This means the PS4 will read garbage when it seeks to the data table.

**Fix:** Move the `data_table_start` calculation to after the alignment loop, or calculate it as `key_table_start + len(key_data)` after padding.

---

### BUG-04: param.sfo ATTRIBUTE entry stored as string instead of integer

**File:** `rocksmith_pc_to_ps4.py:53-54, 97`
**Severity:** Critical (produces malformed SFO files)

The ATTRIBUTE entry is defined with value `"ac"` (a string), but in the PS4 SFO format, ATTRIBUTE is a 32-bit integer (typically `0x00000000` for Additional Content):

```python
entries = [
    ("ATTRIBUTE", "ac", 4, 4),   # Should be integer 0, not string "ac"
    ("CATEGORY", "ac", 4, 3),    # This one IS a string, correctly
    ...
]
```

The data type assignment logic at line 97 compounds the error:
```python
f.write(struct.pack('<H', 0x0404 if max_len == 4 else 0x0402))
```

This assigns types based solely on `max_len`, not actual data type:
- `ATTRIBUTE` (max_len=4) -> gets 0x0404 (INT32) -- correct type, wrong value
- `CATEGORY` (max_len=4) -> gets 0x0404 (INT32) -- **wrong type**, should be 0x0402 (UTF8S)

**Impact:** The param.sfo is structurally invalid. PS4 firmware will reject it or misinterpret the metadata.

**Fix:** ATTRIBUTE should be stored as `struct.pack('<I', 0)` (integer). CATEGORY should keep type 0x0402. The type logic needs a proper type field rather than inference from max_len.

---

### BUG-05: Treeview multi-select removal corrupts job list

**File:** `rocksmith_gui.py:507-510`
**Severity:** High (data corruption)

When removing multiple selected items, indices shift as items are deleted:

```python
for item in selected:
    index = self.file_tree.index(item)
    self.file_tree.delete(item)
    del self.jobs[index]  # BUG: indices shift after each deletion
```

If items at indices [1, 3, 5] are selected, after deleting index 1, the former index 3 is now at index 2, and the wrong job gets deleted.

**Fix:** Delete in reverse order: `for item in reversed(selected):`, or collect indices first and delete from highest to lowest.

---

### BUG-06: PKG builder assigns duplicate entry IDs

**File:** `ps4_pkg_builder.py:78-88`
**Severity:** High (produces malformed PKG files)

All non-system files receive the same entry ID `0x1201`:

```python
def _get_entry_id_for_file(self, target_path: str) -> int:
    if 'param.sfo' in target_lower:
        return self.ENTRY_PARAM_SFO   # 0x1000
    elif 'icon0.png' in target_lower:
        return self.ENTRY_ICON0        # 0x1200
    else:
        return 0x1201  # BUG: same ID for ALL data files
```

In a PKG with multiple DLC files, every data entry would share ID 0x1201, making the entry table ambiguous.

**Fix:** Use a counter: `self._next_data_id` starting at 0x1201, incrementing per file.

---

### BUG-07: `data_values` list stores wrong type for ATTRIBUTE

**File:** `rocksmith_pc_to_ps4.py:69-74`
**Severity:** High (SFO corruption)

Related to BUG-04, the value handling code tests `isinstance(value, str)`:

```python
for key, value, max_len, used_len in entries:
    key_data += key.encode('utf-8') + b'\x00'
    if isinstance(value, str):
        data_values.append(value.encode('utf-8') + b'\x00')
    else:
        data_values.append(value)
```

Since ATTRIBUTE's value is `"ac"` (a string), it gets encoded as `b'ac\x00'` (3 bytes) and padded to max_len 4. But it should be `struct.pack('<I', 0)` (4 bytes representing integer 0).

---

## 2. Security Issues

### SEC-01: Command injection in open_output_folder

**File:** `rocksmith_gui.py:714-718`
**Severity:** Low (requires crafted directory name)

```python
def open_output_folder(self):
    if sys.platform == 'win32':
        os.startfile(self.output_base_dir)       # Safe
    elif sys.platform == 'darwin':
        os.system(f'open "{self.output_base_dir}"')     # Vulnerable
    else:
        os.system(f'xdg-open "{self.output_base_dir}"') # Vulnerable
```

A directory path containing `"$(malicious_command)"` or backticks could execute arbitrary commands. Risk is low since the path comes from a GUI directory picker, but it's a poor pattern.

**Fix:** Use `subprocess.run(['open', str(self.output_base_dir)])` or `subprocess.run(['xdg-open', str(self.output_base_dir)])` instead of `os.system()`.

---

### SEC-02: No input validation on Steam API responses

**File:** `steam_dlc_database.py:55-76`
**Severity:** Low

The Steam API response is parsed as JSON with no validation of structure, size, or content type. An unexpected response could cause unhandled exceptions.

---

### SEC-03: subprocess calls without input sanitization

**Files:** `rocksmith_pc_to_ps4.py:179-183`, `enhanced_converter.py:381-386`
**Severity:** Low

External tool invocations pass file paths directly to `subprocess.run()` as list arguments (which avoids shell injection), but the `cwd` parameter at `enhanced_converter.py:385` uses `str(output_dir)` which could be user-controlled. Since `subprocess.run` with a list avoids shell interpretation, the actual risk is minimal.

---

## 3. Format/Correctness Issues

### FMT-01: PKG builder produces non-installable packages

**File:** `ps4_pkg_builder.py` (entire file)
**Severity:** Fundamental (feature does not work)

The PKG builder writes a drastically simplified structure that omits multiple required PS4 PKG components:

| Required Component | Present? | Notes |
|---|---|---|
| PKG Header (0x000-0x0FF) | Partial | Missing many required fields |
| Digest table (SHA256 hashes) | No | Filled with zeros |
| Entry table | Partial | Wrong entry IDs (BUG-06) |
| PFS Image (PlayStation File System) | **No** | Required for all PKGs |
| Mount image | **No** | Required for content access |
| SC entries | **No** | Required for DLC validation |
| Proper content flags | No | Set to 0 |

A valid fake PKG (as created by tools like LibOrbisPkg or Fake PKG Generator) requires:
1. A PFS image containing the actual file system
2. Proper digest chains
3. Correct SC (System Content) entries
4. Mount image with encryption parameters (even if using dummy keys)

The current implementation writes raw files after the entry table, which is not how PS4 PKGs work. The PS4 expects files within a PFS image.

**Impact:** Generated PKGs will not install on any PS4 firmware (retail or homebrew).

---

### FMT-02: param.sfo is missing required entries

**File:** `rocksmith_pc_to_ps4.py:52-59`
**Severity:** High

A valid PS4 DLC param.sfo typically requires additional entries:

| Entry | Present? | Required? |
|---|---|---|
| ATTRIBUTE | Yes (wrong type) | Yes |
| CATEGORY | Yes (wrong data type) | Yes |
| CONTENT_ID | Yes | Yes |
| FORMAT | **No** | Yes (typically "obs") |
| TITLE | Yes | Yes |
| TITLE_ID | Yes | Yes |
| VERSION | Yes | Yes |
| PUBTOOLINFO | **No** | Recommended |
| SYSTEM_VER | **No** | Recommended |

---

### FMT-03: GP4 project file has incorrect DLC path structure

**File:** `rocksmith_pc_to_ps4.py:136`
**Severity:** Medium

```xml
<file targ_path="DLC/{psarc_filename}" orig_path="{psarc_filename}" />
```

The `orig_path` points to a filename without directory prefix, which means the GP4 parser expects the psarc file to be in the same directory as the GP4 file. This is fragile and may break depending on working directory.

---

### FMT-04: Content ID format may not match PS4 expectations

**File:** `enhanced_converter.py:96-109`
**Severity:** Medium

Generated Content IDs use format `APPID{steam_id}000...`:
```
EP0001-CUSA00745_00-APPID2221200000
```

PS4 Content IDs are typically 36 characters with format: `XX0000-CUSA00000_00-0000000000000000`. The "APPID" prefix in the suffix is non-standard and may cause issues with PS4 content management.

---

### FMT-05: PSARC conversion pipeline is incomplete

**Files:** `rocksmith_pc_to_ps4.py:248-298`, `enhanced_converter.py:111-264`
**Severity:** Fundamental

The core conversion pipeline has a critical gap: there is no PSARC repacking implementation. The code depends on external tools (`UnPSARC.exe`, `psarc.exe`) that are not bundled, and the `repack_psarc()` method uses a guessed command-line syntax:

```python
result = subprocess.run(
    [packer_found, "create", "--inputfile", str(source_dir),
     "--output", str(output_psarc), "--flags", str(flags)],
    ...
)
```

This command syntax is a placeholder that may not match any real tool. The PC-to-PS4 conversion workflow cannot complete without this step.

---

### FMT-06: Audio directory rename logic is platform-fragile

**File:** `rocksmith_pc_to_ps4.py:228-229`
**Severity:** Low

```python
if 'audio/windows' in str(rel_file) or 'audio\\windows' in str(rel_file):
    new_rel_file = str(rel_file).replace('windows', 'generic').replace('\\', '/')
```

String-based path manipulation instead of using `pathlib` properly. On Windows, `Path` objects use backslashes, and the string comparison could miss mixed separators.

---

## 4. Code Quality Issues

### CQ-01: ps4_pkg_builder.py not in PyInstaller spec

**File:** `RiffBridge.spec:4`, `BUILD_COMPLETE.bat:108-110`
**Severity:** Medium

The `ps4_pkg_builder.py` module is not listed in the PyInstaller data files or hidden imports. Because `enhanced_converter.py` imports it inside a try/except block, PyInstaller's static analysis may not detect the dependency. The built .exe may lack the PKG builder.

---

### CQ-02: Dead code in base converter

**File:** `rocksmith_pc_to_ps4.py:398-440` (`build_pkg` method), `rocksmith_pc_to_ps4.py:442-576` (`convert` method)
**Severity:** Low

The base class `build_pkg()` and `convert()` methods are never called through the GUI (which uses `EnhancedRocksmithConverter.convert_enhanced()` and `create_pkg_from_ps4()`). They represent an earlier iteration that has diverged from the active code path.

---

### CQ-03: Inconsistent import patterns

**Files:** Multiple
**Severity:** Low

Several modules are imported inside functions rather than at module level:
- `import traceback` (rocksmith_gui.py:633, enhanced_converter.py:263)
- `import json` (enhanced_converter.py:238)
- `import hashlib` (enhanced_converter.py:189, rocksmith_pc_to_ps4.py:494)
- `import shutil` (enhanced_converter.py:495)

This is not harmful but makes dependency tracking harder and violates PEP 8.

---

### CQ-04: No automated tests

**Severity:** Medium

`TEST_PS4_CONVERSION.py` and `TEST_IMAGE.py` are manual scripts that require user interaction (`input("Press Enter...")`). There are no unit tests, no pytest fixtures, no CI/CD pipeline.

---

### CQ-05: Excessive documentation files

**Severity:** Low

11 documentation/notes files totaling ~53KB for 2,893 lines of code. Most are AI session artifacts (`SYNTAX_ERROR_FIXED.txt`, `LAYOUT_FIXED.txt`, `SC_EXE_MISSING_FIX.txt`, etc.) that document iterative debugging rather than providing useful reference documentation. These add noise to the repository.

Files that could be removed:
- `SYNTAX_ERROR_FIXED.txt`
- `LAYOUT_FIXED.txt`
- `SC_EXE_MISSING_FIX.txt`
- `PKGTOOL_PATH_FIX.txt`
- `PKG_PATH_FIX.txt`
- `PKG_BUILDING_INTEGRATED.txt`
- `LIBORBISPKG_INTEGRATED.txt`
- `PYTHON_PKG_BUILDER_INTEGRATED.txt`
- `psarc_checker.py` (1-line placeholder)

---

### CQ-06: Naming inconsistencies

**Severity:** Low

The project name alternates between:
- "Rifft Bridge" (artwork filenames - likely intentional brand name)
- "Riff Bridge" (cover art filename)
- "RiffBridge" (code, .exe, icon)

---

### CQ-07: No `__init__.py` or package structure

**Severity:** Low

All Python files are flat in the root directory. For a project of this size, a simple package structure would improve organization.

---

### CQ-08: Error handling swallows details

**File:** `rocksmith_gui.py:53-54, 87-89, 207`
**Severity:** Low

Multiple bare `except Exception` blocks silently discard error information:
```python
except Exception as e:
    pass  # Silent fail, try next
```

---

### CQ-09: `hashlib` import used for non-security MD5

**Files:** `enhanced_converter.py:189-191`, `rocksmith_pc_to_ps4.py:494-496`
**Severity:** Informational

MD5 is used for generating Content ID suffixes. While not a security use case, this is noted for completeness. SHA256 truncated would be a more modern choice.

---

### CQ-10: No type checking or linting configured

**Severity:** Low

No `pyproject.toml`, `setup.cfg`, `mypy.ini`, or `.flake8` configuration. Type hints are present in some places but inconsistent.

---

### CQ-11: `requests` dependency has no version ceiling

**File:** `requirements_gui.txt`
**Severity:** Low

```
requests>=2.28.0
```

No upper bound could cause future breakage with major version changes.

---

### CQ-12: Unused `io` import

**File:** `ps4_pkg_builder.py:13`
**Severity:** Trivial

```python
import io  # Never used
```

---

## 5. Architecture Assessment

### What works well:
- **Modular design:** Clear separation between GUI, converter, Steam database, and PKG builder
- **Class hierarchy:** `RocksmithPS4Converter` -> `EnhancedRocksmithConverter` is reasonable
- **GUI design:** Drag-and-drop with batch processing is user-friendly
- **Fallback strategy:** Python PKG builder with external tool fallback is a sound approach
- **Steam integration:** Automatic metadata enrichment is a valuable feature

### What needs work:
- **Core pipeline is incomplete:** Cannot actually convert PC PSARC to PS4 PSARC without external tools
- **PKG format implementation is fundamentally insufficient:** Missing PFS image, digests, mount image
- **param.sfo has multiple structural bugs:** Will produce invalid metadata files
- **No end-to-end testing possible:** Without working PSARC tools and valid PKG generation, the pipeline cannot produce installable results

### Recommended architecture changes:
1. Either bundle the required external tools or implement PSARC pack/unpack in Python
2. The PKG builder needs a ground-up rewrite based on LibOrbisPkg's actual algorithm (not just header format)
3. Consider using the `orbis-pub-gen` project or porting LibOrbisPkg's PFS implementation
4. Add proper unit tests with known-good reference files for binary format validation

---

## 6. Summary Table

| Category | Count | Critical | High | Medium | Low |
|---|---|---|---|---|---|
| Bugs | 7 | 4 | 3 | 0 | 0 |
| Security | 3 | 0 | 0 | 0 | 3 |
| Format/Correctness | 6 | 2 | 1 | 2 | 1 |
| Code Quality | 12 | 0 | 0 | 3 | 9 |
| **Total** | **28** | **6** | **4** | **5** | **13** |

---

## 7. Verdict

The project demonstrates solid architectural thinking and good GUI design for a non-programmer's AI-assisted effort. However, it has **fundamental blockers** preventing it from achieving its stated goal:

1. **The param.sfo generator produces invalid files** (3 bugs in the binary format)
2. **The PKG builder produces non-installable packages** (missing PFS image and other required structures)
3. **The PSARC conversion pipeline is incomplete** (no pack/unpack implementation)

The README's statement that it is "not actually working" is accurate. To reach a working state, the project would need:
- param.sfo bugs fixed (straightforward)
- A working PSARC pack/unpack solution (moderate effort, could use Python psarc libraries)
- A complete PKG builder rewrite or integration with LibOrbisPkg (significant effort)

---

*End of audit report.*
