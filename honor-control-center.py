#!/usr/bin/env python3
"""
Honor Ecosystem Suite — MagicOS PC Suite (Windows & Linux Entry Point)
High-Speed 70 MB/s Fast Beam • Live RAM & Battery Telemetry • Wireless Mirroring • App Debloater
Zero-Resource Guarantee (0% CPU, 0 MB RAM when closed or idle).
"""

import sys
import os
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root and lib to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from lib.honor_suite.ui.main_window import MainWindow

def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Honor Ecosystem Suite")
    app.setOrganizationName("Honor Ecosystem")

    # Set Application Icon if available
    icon_path = BASE_DIR / "desktop" / "honor-hub.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
