import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASEDIR = Path(sys.executable).parent
else:
    BASEDIR = Path(__file__).parent
YEARLY_SUMMARY_DIR = BASEDIR / "Roczne podsumowanie"
EMPLOYEES_DIR = BASEDIR / "Pracownicy"
SCHEDULES_DIR = BASEDIR / "Harmonogramy"
HOLIDAYS_FILE = SCHEDULES_DIR / "swieta.json"
ICON_FILE = BASEDIR / "data" / "ikonka.ico"
FONT_FILE = BASEDIR / "data" / "DejaVuSans.ttf"

# COlORS
DAY_OFF_COLOR = "red3"
