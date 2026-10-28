"""
MagicOS Dark 9.0 QSS Design Theme for Honor Ecosystem Suite.
Enforces Obsidian palette (#0b0f19), card geometry, Honor Cyan accents, and anti-ghosting.
"""

import sys

def apply_windows_dark_titlebar(widget):
    """
    Applies Windows 11 / Windows 10 native dark titlebar via DwmSetWindowAttribute.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes
        hwnd = int(widget.winId())
        # DWMWA_USE_IMMERSIVE_DARK_MODE is 20 on Windows 11, 19 on early Windows 10
        value = ctypes.c_int(1)
        for attr in [20, 19]:
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                attr,
                ctypes.byref(value),
                ctypes.sizeof(value)
            )
    except Exception:
        pass

MAGIC_OS_QSS = """
/* Global Window Styling */
QMainWindow, QDialog, QWidget#CentralWidget {
    background-color: #0b0f19;
    color: #f8fafc;
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    font-size: 13px;
}

/* Sidebar Navigation */
QFrame#SidebarFrame {
    background-color: #0f172a;
    border-right: 1px solid #1e293b;
    min-width: 240px;
    max-width: 240px;
}

QLabel#BrandTitle {
    color: #38bdf8;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 0.5px;
    padding-top: 6px;
}

QLabel#BrandSubtitle {
    color: #64748b;
    font-size: 11px;
    font-weight: 500;
    margin-bottom: 8px;
}

/* Sidebar Nav Buttons */
QPushButton.NavButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    color: #94a3b8;
    font-weight: 600;
    font-size: 13px;
    text-align: left;
}

QPushButton.NavButton:hover {
    background-color: #1e293b;
    color: #f8fafc;
}

QPushButton.NavButton:checked, QPushButton.NavButton.active {
    background-color: #1e293b;
    color: #38bdf8;
    border-left: 3px solid #38bdf8;
    font-weight: 700;
}

/* Cards & Containers */
QFrame.CardFrame {
    background-color: #151c2c;
    border: 1px solid #232f46;
    border-radius: 12px;
    padding: 16px;
}

QLabel.CardTitle {
    color: #f8fafc;
    font-size: 15px;
    font-weight: 700;
}

QLabel.CardDesc {
    color: #94a3b8;
    font-size: 12px;
}

/* Action Buttons */
QPushButton.PrimaryButton {
    background-color: #0284c7;
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
}

QPushButton.PrimaryButton:hover {
    background-color: #38bdf8;
    color: #0b0f19;
}

QPushButton.PrimaryButton:pressed {
    background-color: #0369a1;
}

QPushButton.SecondaryButton {
    background-color: #1e293b;
    color: #f8fafc;
    font-weight: 600;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 14px;
}

QPushButton.SecondaryButton:hover {
    background-color: #334155;
    border-color: #475569;
}

QPushButton.DangerButton {
    background-color: #b91c1c;
    color: #ffffff;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
}

QPushButton.DangerButton:hover {
    background-color: #ef4444;
}

/* Progress Bars */
QProgressBar {
    background-color: #0b0f19;
    border: 1px solid #1e293b;
    border-radius: 6px;
    text-align: center;
    color: #f8fafc;
    font-weight: 700;
    font-size: 11px;
    height: 12px;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
    border-radius: 5px;
}

/* Inputs & Combos */
QLineEdit {
    background-color: #0b0f19;
    border: 1px solid #232f46;
    border-radius: 8px;
    padding: 8px 12px;
    color: #f8fafc;
    font-size: 13px;
}

QLineEdit:focus {
    border: 1px solid #38bdf8;
}

QComboBox {
    background-color: #0b0f19;
    border: 1px solid #232f46;
    border-radius: 8px;
    padding: 8px 12px;
    color: #f8fafc;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #151c2c;
    border: 1px solid #232f46;
    color: #f8fafc;
    selection-background-color: #1e293b;
    selection-color: #38bdf8;
}

/* Checkboxes */
QCheckBox {
    color: #f8fafc;
    font-size: 13px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    background-color: #0b0f19;
    border: 1px solid #334155;
    border-radius: 4px;
}

QCheckBox::indicator:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
}

/* Tables & Lists */
QTableWidget {
    background-color: #151c2c;
    border: 1px solid #232f46;
    border-radius: 8px;
    gridline-color: #1e293b;
    color: #f8fafc;
    selection-background-color: #1e293b;
    selection-color: #38bdf8;
}

QHeaderView::section {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #1e293b;
    font-weight: 700;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #232f46;
    border-radius: 8px;
    background-color: #151c2c;
}

QTabBar::tab {
    background-color: #0f172a;
    color: #94a3b8;
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #151c2c;
    color: #38bdf8;
    border-bottom: 2px solid #38bdf8;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #0b0f19;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #232f46;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #38bdf8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
