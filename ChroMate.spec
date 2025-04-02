# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(
    ['main_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('chromium_updater_icon.ico', '.')],
    hiddenimports=['plyer.platforms.win.notification'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ChroMate_v1.0.0',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='chromium_updater_icon.ico',
    version='version_info.txt'
)

