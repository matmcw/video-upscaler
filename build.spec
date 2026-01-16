# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Video Upscaler.

This spec file configures PyInstaller to build a Windows executable
with all dependencies bundled (except model files).

Usage:
    pyinstaller build.spec

Output:
    dist/VideoUpscaler/
        VideoUpscaler.exe
        (plus all bundled dependencies)
"""

import os
from pathlib import Path

# Get the project root directory
project_root = Path(SPECPATH)

# Analysis configuration
a = Analysis(
    # Entry point script
    [str(project_root / 'src' / 'main.py')],

    # Additional paths to search for imports
    pathex=[str(project_root / 'src')],

    # Binary files to include (none - we bundle separately)
    binaries=[],

    # Data files to include
    datas=[],

    # Hidden imports that PyInstaller might miss
    hiddenimports=[
        'PyQt6.sip',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
    ],

    # Modules to exclude (reduce size)
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'unittest',
        'pytest',
        'setuptools',
        'pkg_resources',
    ],

    # Hook configuration
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],

    # Don't collect bytecode for excluded packages
    noarchive=False,
)

# Remove unnecessary PyQt6 plugins to reduce size
# Keep only essential plugins
excluded_plugins = [
    'PyQt6/Qt6/plugins/sqldrivers',
    'PyQt6/Qt6/plugins/multimedia',
    'PyQt6/Qt6/plugins/position',
    'PyQt6/Qt6/plugins/sensors',
    'PyQt6/Qt6/plugins/webview',
]

a.binaries = [b for b in a.binaries if not any(excl in b[0] for excl in excluded_plugins)]

# Create PYZ archive
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Use COLLECT for onedir mode
    name='VideoUpscaler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX if available
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Icon file (optional - create an icon.ico in project root)
    icon=str(project_root / 'icon.ico') if (project_root / 'icon.ico').exists() else None,
)

# Collect all files into the distribution folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoUpscaler',
)
