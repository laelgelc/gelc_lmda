# Python
# File: run_lmda_poc.py (repository root)
import sys
from pathlib import Path

def _ensure_local_package_on_path():
    """
    Ensure the local 'poc/src' directory (which contains the 'lmda_poc' package)
    is available on sys.path when running from the repository root.
    This is a no-op if the path doesn't exist or is already on sys.path.
    """
    try:
        script_dir = Path(__file__).resolve().parent
    except NameError:
        # Fallback if __file__ is not defined (some interactive contexts)
        script_dir = Path.cwd()

    candidates = [
        script_dir / "poc" / "src",        # repo layout during development
        script_dir / "src",                # alternative common layout
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            c_str = str(c)
            if c_str not in sys.path:
                sys.path.insert(0, c_str)
            # Once we've added a valid candidate, we can stop
            break

def _run_cli():
    _ensure_local_package_on_path()
    from lmda_poc.cli import main
    return main()


def _run_gui():
    _ensure_local_package_on_path()
    try:
        from lmda_poc.gui_qt import launch_gui
    except Exception as e:
        print("ERROR: GUI dependencies missing. Ensure PySide6 and matplotlib are installed.")
        print(str(e))
        return 1
    return launch_gui()


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--gui" in argv:
        # Remove flag before passing to any CLI parsing
        argv = [a for a in argv if a != "--gui"]
        sys.exit(_run_gui())
    else:
        sys.exit(_run_cli())
