# Python
# File: lmda_poc.spec (place at the repository root)
# Build with: pyinstaller lmda_poc.spec

from PyInstaller.utils.hooks import collect_all
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
import os
import sys

# Increase recursion limit
sys.setrecursionlimit(sys.getrecursionlimit() * 5)

# Collect spaCy and the English model resources
spacy_datas, spacy_binaries, spacy_hidden = collect_all('spacy')
model_datas, model_binaries, model_hidden = collect_all('en_core_web_sm')

pathex = [os.path.join(os.getcwd(), 'poc', 'src')]

a = Analysis(
    ['run_poc.py'],
    pathex=pathex,
    binaries=spacy_binaries + model_binaries,
    datas=spacy_datas + model_datas,
    hiddenimports=spacy_hidden + model_hidden,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='lmda_poc',
    console=True,      # console app
    icon=None,
)
# For --onefile build, use EXE only; for onedir, wrap with COLLECT.
