# Add GUI to the PoC

This document explains how to develop and run the PoC with both CLI and GUI (PySide6), and how to package a distributable build. It assumes you're working inside the Junie project environment.

## Overview

- Code style: Python 3.12
- Package manager: conda (do not mix with others)
- GUI toolkit: PySide6 (LGPLv3)
- License: Apache-2.0 (project), LGPLv3 notices required for Qt/PySide6 when distributing binaries
- Entry points:
  - CLI: run_lmda_poc.py (repository root), or `python -m lmda_poc` when working from `poc/src`
  - GUI: started via a CLI flag in run_lmda_poc.py (e.g., `--gui`) or a dedicated launch script (if added)

## Prerequisites

- Python 3.12 in the active environment
- Installed packages (selected): pandas, numpy, matplotlib, PySide6, PyInstaller (if packaging)
- Activate `my_env` conda virtual environment before running commands

Install GUI dependency (already installed for many devs; included here for completeness):

```
conda install pyside6
```

Optional for packaging:

```
conda install pyinstaller
```

## Running the PoC

### CLI mode (recommended for quick iterations)

```
python run_lmda_poc.py --help
python run_lmda_poc.py # with your typical arguments
```

### GUI mode (PySide6)
If a unified entry point supports a GUI flag:
```
python run_lmda_poc.py --gui
```

If a dedicated GUI launcher module/script is added later (e.g., app_main.py):
```
python app_main.py --gui
```

Notes:
- GUI runs on the main thread; any long computation should execute in a worker (QThread/QThreadPool) to keep the UI responsive.
- For plotting inside Qt, use matplotlib with the QtAgg backend. If interactive web plots are needed later, consider Qt WebEngine.

## Debugging

- Run with verbose logging in CLI to inspect parameters and data flow.
- For GUI issues:
  - Check Qt platform plugin errors (e.g., “xcb” on Linux). Ensure Qt shared libraries are found (usually automatic).
  - macOS: if you see “app cannot be opened because the developer cannot be verified,” run from Terminal or notarize/sign in distributed builds.

## Packaging (PyInstaller)

Two sample spec files are provided:
- lmda_poc.spec (folder-based bundle)
- lmda_poc_onefile.spec (single-file bundle; larger, slower start)

Build:

```
pyinstaller lmda_poc.spec
# or
pyinstaller lmda_poc_onefile.spec
```

Artifacts appear under dist/. Test the executable on a clean machine or VM.

### LGPLv3 compliance for PySide6/Qt in binaries

- Qt must be dynamically linked (default for Python builds).
- Include license texts in your bundle:
  - Project LICENSE (Apache-2.0)
  - Project NOTICE (Apache-2.0)
  - Qt/PySide6 licenses (copy the Qt licenses directory, or include LGPLv3 text and relevant Qt license notices).
- Do not add technical measures that prevent users from replacing Qt libraries.

A practical approach:
- Create a licenses/ folder in the bundle via PyInstaller's datas in the spec file and place:
  - LICENSE (Apache-2.0)
  - NOTICE
  - Third-party: PySide6/Qt license texts

## Coding conventions

- Keep GUI and core logic decoupled:
  - Core pipeline functions live in importable modules (pure Python, no Qt imports).
  - GUI imports the core and orchestrates parameters, threading, and presentation.
- CLI and GUI share the same core modules to avoid duplication.
- Add type hints and small, composable functions for testability.

## Reproducibility

- Document environment setup in README and/or an environment.yml export (if used with `my_env` conda virtual environment).
- Seed any stochastic steps and prefer deterministic algorithms where possible.
- Provide small sample inputs (not datasets) for quick testing, if appropriate.

## Release checklist (short)

- [ ] LICENSE at repo root (Apache-2.0)
- [ ] NOTICE at repo root (Apache-2.0 attribution and citation)
- [ ] CITATION.cff at repo root
- [ ] GUI and CLI both run on a clean environment
- [ ] PyInstaller bundle built and smoke-tested
- [ ] Bundle includes licenses/ folder with Apache-2.0 + Qt/PySide6 notices
- [ ] README updated with how to run CLI and GUI
- [ ] Tag release and include citation in the release notes

## Troubleshooting

- ImportError: No module named PySide6
  - Ensure the active environment is `my_env` conda virtual environment with PySide6 installed.
- Qt platform plugin error
  - On Linux, install system dependencies for Qt (e.g., libxcb). On macOS/Windows, usually bundled automatically.
- GUI freezes during long runs
  - Move work to a QThread or QRunnable; emit signals to update the UI.
