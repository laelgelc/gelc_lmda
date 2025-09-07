# Python
# File: run_lmda_poc.py (repository root)
import sys

def _run_cli():
    from lmda_poc.cli import main
    return main()


def _run_gui():
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
