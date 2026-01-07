# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('enhanced_converter.py', '.'), ('rocksmith_pc_to_ps4.py', '.'), ('steam_dlc_database.py', '.'), ('RiffBridge_icon.ico', '.'), ('Riff_Bridge_cover_art.jpg', '.')]
binaries = []
hiddenimports = ['tkinterdnd2', 'PIL._tkinter_finder', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont', 'PIL.ImageTk']
tmp_ret = collect_all('tkinterdnd2')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['rocksmith_gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='RiffBridge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['RiffBridge_icon.ico'],
)
