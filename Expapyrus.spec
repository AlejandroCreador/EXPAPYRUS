# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['expapyrus.py'],
    pathex=[],
    binaries=[],
    datas=[('expapyrus_icon.ico', '.')],
    hiddenimports=['PIL', 'pytesseract', 'pdf2image', 'tkinter'],
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
    name='Expapyrus',
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
    icon=['expapyrus_icon.ico'],
)
