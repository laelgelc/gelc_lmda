# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# Increase recursion limit
import sys
sys.setrecursionlimit(sys.getrecursionlimit() * 5)

datas = []
binaries = []
hiddenimports = []

# Collect spaCy and model
tmp_ret = collect_all('spacy')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('en_core_web_sm')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

# Collect PySide6 and matplotlib (hooks usually handle this, but we add to be safe)
try:
    tmp_ret = collect_all('PySide6')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except Exception:
    pass
try:
    tmp_ret = collect_all('matplotlib')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except Exception:
    pass

# Bundle licenses directory with Apache-2.0 and Qt/PySide6 licenses
import os
from PyInstaller.utils.hooks import collect_data_files
root = os.path.abspath('.')
lic_files = []
for fname in ['LICENSE', 'LICENCE', 'NOTICE']:
    p = os.path.join(root, fname)
    if os.path.exists(p):
        lic_files.append((p, 'licenses'))
# Try to collect PySide6 license texts (varies by install)
try:
    lic_files += collect_data_files('PySide6', includes=['LICENSE*', 'LICENSES/*', 'Qt*', '*/LICENSES/*'])
except Exception:
    pass

datas += lic_files


a = Analysis(
    ['run_lmda_poc.py'],
    pathex=['poc/src'],
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
    [],
    exclude_binaries=True,
    name='lmda_poc',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['LAEL.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='lmda_poc',
)
