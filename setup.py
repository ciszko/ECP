import sys
from cx_Freeze import setup, Executable
import os.path
import pkgutil

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ["TCL_LIBRARY"] = os.path.join(PYTHON_INSTALL_DIR, "tcl", "tcl8.6")
os.environ["TK_LIBRARY"] = os.path.join(PYTHON_INSTALL_DIR, "tcl", "tk8.6")
imported_modules = [
    "tkcalendar",
    "ttkwidgets",
    "babel",
    "os",
    "json",
    "shutil",
    "tkinter",
    "collections",
    "encodings",
    "importlib",
    "fpdf",
    "urllib",
    "email",
    "http",
    "html",
    "PIL",
    "logging",
    "zoneinfo",
    "cffi",
    "concurrent",
    "ctypes",
    "curses",
    "distutils",
    "lib2to3",
    "multiprocessing",
    "PIL",
    "pkg_resources",
    "pycparser",
    "pydoc_data",
    "pytz",
    "setuptools",
    "unittest",
    "xml",
    "xmlrpc",
]
all_packages = [i.name for i in list(pkgutil.iter_modules()) if i.ispkg]

base = None
if sys.platform == "win32":
    base = "Win32GUI"


options = {
    "build_exe": {
        "include_files": [
            (
                os.path.join(PYTHON_INSTALL_DIR, "DLLs", "tk86t.dll"),
                os.path.join("lib", "tk86t.dll"),
            ),
            (
                os.path.join(PYTHON_INSTALL_DIR, "DLLs", "tcl86t.dll"),
                os.path.join("lib", "tcl86t.dll"),
            ),
            ("./data/ikonka.ico", "data/ikonka.ico"),
            ("./data/DejaVuSans.ttf", "data/DejaVuSans.ttf"),
        ],
        "packages": imported_modules,
        "excludes": [p for p in all_packages if p not in imported_modules],
        "optimize": 2,
    },
}

executables = [
    Executable("main.py", base=base, icon="./data/ikonka.ico", shortcut_name="ECP")
]

setup(
    name="ECP",
    version="3.0",
    description="Ewidencja Czasu Pracy",
    executables=executables,
    options=options,
)

# C:/Users/ciszk/AppData/Local/Programs/Python/Python37/python.exe setup.py build
