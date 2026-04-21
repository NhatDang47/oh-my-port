# oh-my-port.spec
# PyInstaller spec file — used on BOTH Windows and Linux.
# Run via: pyinstaller oh-my-port.spec

import sys
from PyInstaller.building.build_main import Analysis, PYZ, EXE

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=['.'],           # Project root — lets "from src.xxx import" work
    binaries=[],
    datas=[],
    hiddenimports=[
        'serial',
        'serial.tools',
        'serial.tools.list_ports',
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'src.gui.main_window',
        'src.core.serial_manager',
        'src.core.threads',
        'src.utils.logger',
    ],
    hookspath=[],
    hooksconfig={},
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
    name='oh-my-port',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # Compress the binary (requires UPX installed, optional)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,      # No terminal/cmd window — GUI only
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
