import os
import sys
from pathlib import Path

# Ensure utf-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from lib.honor_suite.ui.main_window import MainWindow

app = QApplication(sys.argv)
w = MainWindow()
w.show()
print("MainWindow initialized and shown successfully.")
def shutdown():
    w.close()
    app.quit()

QTimer.singleShot(1000, shutdown)
res = app.exec()
print(f"Application event loop finished with code: {res}")
