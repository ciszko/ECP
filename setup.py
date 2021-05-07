import sys
from cx_Freeze import setup, Executable
import os.path

PYTHON_INSTALL_DIR = os.path.dirname(os.path.dirname(os.__file__))
os.environ['TCL_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tcl8.6')
os.environ['TK_LIBRARY'] = os.path.join(PYTHON_INSTALL_DIR, 'tcl', 'tk8.6')

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        'include_files': [
            (os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tk86t.dll'),
             os.path.join('lib', 'tk86t.dll')),
            (os.path.join(PYTHON_INSTALL_DIR, 'DLLs', 'tcl86t.dll'), os.path.join('lib', 'tcl86t.dll'))],
        "packages": ["tkcalendar", "babel.numbers"]
    },
}

executables = [
    Executable('main.py', base=base,
               icon="./data/ikonka.ico", shortcutName='ECP')
]

setup(name='ECP',
      version='3.0',
      description='Ewidencja Czasu Pracy',
      executables=executables,
      options=options
      )
