# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\POS\\Desktop\\posprinter_supabase\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src'), ('printer_config.json', '.'), ('C:\\Users\\POS\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\escpos\\capabilities.json', 'escpos/.'), ('C:\\Users\\POS\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\escpos\\capabilities_win.json', 'escpos/.')],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui', 'websockets', 'requests', 'python_escpos', 'psutil', 'pyusb', 'serial', 'escpos', 'escpos.capabilities'],
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
    name='POSPrinter',
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
)
