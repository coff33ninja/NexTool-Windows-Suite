# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.win32 import versioninfo

block_cipher = None

# Add version info
version_info = versioninfo.VSVersionInfo(
    ffi=versioninfo.FixedFileInfo(
        filevers=(0, 1, 0, 0),
        prodvers=(0, 1, 0, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
    ),
    kids=[
        versioninfo.StringFileInfo([
            versioninfo.StringTable("040904B0", [
                versioninfo.StringStruct("CompanyName", "NexTool"),
                versioninfo.StringStruct("FileDescription", "NexTool Windows Suite"),
                versioninfo.StringStruct("FileVersion", "0.1.0"),
                versioninfo.StringStruct("InternalName", "NexTool"),
                versioninfo.StringStruct("OriginalFilename", "NexTool.exe"),
                versioninfo.StringStruct("ProductName", "NexTool Windows Suite"),
                versioninfo.StringStruct("ProductVersion", "0.1.0")
            ])
        ]),
        versioninfo.VarFileInfo([versioninfo.VarStruct("Translation", [1033, 1200])])
    ]
)

a = Analysis(
    ['NexTool.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('Modules', 'Modules'),
        ('docs', 'docs'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'win32api',
        'win32con',
        'win32security',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NexTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Changed to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='Extras/icon.ico',  # Add your icon file path
    version=version_info
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NexTool',
)