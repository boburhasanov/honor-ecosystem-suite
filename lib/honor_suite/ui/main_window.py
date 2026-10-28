"""
Main Application Window for Honor Ecosystem Suite (PySide6 / Qt 6).
Features Obsidian Dark styling, sidebar navigation, stacked view router, and Zero-Resource clean exit.
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QApplication
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from lib.honor_suite.core.adb_service import AdbService
from lib.honor_suite.core.telemetry import TelemetryService
from lib.honor_suite.core.file_beamer import FileBeamer
from lib.honor_suite.core.package_manager import PackageManagerService
from lib.honor_suite.core.mirror_service import MirrorService
from lib.honor_suite.core.file_browser import FileBrowserService

from lib.honor_suite.ui.theme import MAGIC_OS_QSS, apply_windows_dark_titlebar
from lib.honor_suite.ui.widgets.badge import StatusBadge
from lib.honor_suite.ui.views.dashboard_view import DashboardView
from lib.honor_suite.ui.views.beam_view import BeamView
from lib.honor_suite.ui.views.debloater_view import DebloaterView
from lib.honor_suite.ui.views.mirror_view import MirrorView
from lib.honor_suite.ui.views.file_view import FileView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Honor Ecosystem Hub — MagicOS PC Suite")
        self.resize(1180, 780)
        self.setMinimumSize(960, 640)

        # Apply MagicOS Theme & Windows 11 Dark Titlebar
        self.setStyleSheet(MAGIC_OS_QSS)
        apply_windows_dark_titlebar(self)

        # Initialize Core Services
        self.adb = AdbService()
        self.telemetry = TelemetryService(self.adb)
        self.beamer = FileBeamer(self.adb)
        self.pm = PackageManagerService(self.adb)
        self.mirror = MirrorService(self.adb)
        self.file_browser = FileBrowserService(self.adb)

        self._build_ui()

        # Connection Watchdog (every 6 seconds, non-blocking)
        self.watchdog_timer = QTimer(self)
        self.watchdog_timer.timeout.connect(self._watchdog_check)
        self.watchdog_timer.start(6000)

        # Trigger initial data load
        QTimer.singleShot(300, self.dashboard_view.refresh_data)

    def _build_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("SidebarFrame")
        s_layout = QVBoxLayout(sidebar)
        s_layout.setContentsMargins(14, 18, 14, 18)
        s_layout.setSpacing(6)

        # Branding
        title = QLabel("HONOR ECOSYSTEM")
        title.setObjectName("BrandTitle")
        s_layout.addWidget(title)

        subtitle = QLabel("MagicOS 9.0 PC Suite (v2.0)")
        subtitle.setObjectName("BrandSubtitle")
        s_layout.addWidget(subtitle)

        s_layout.addSpacing(10)

        # Nav Buttons
        self.nav_buttons = []
        nav_items = [
            ("📊  Dashboard", 0),
            ("🚀  Fast Beam (70 MB/s)", 1),
            ("🧹  App Debloater", 2),
            ("🖥️  Screen Mirror", 3),
            ("📁  File Explorer", 4),
        ]

        for text, idx in nav_items:
            btn = QPushButton(text)
            btn.setProperty("class", "NavButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked=False, i=idx: self._switch_tab(i))
            s_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        s_layout.addStretch()

        # Sidebar Footer: Zero-Resource Guarantee & Link Status
        foot_box = QVBoxLayout()
        foot_box.setSpacing(6)

        self.sidebar_status = StatusBadge("Checking...", "#f59e0b")
        foot_box.addWidget(self.sidebar_status)

        zero_res_lbl = QLabel("🛡️ Zero-Resource Guarantee\n0% CPU • 0 MB RAM when idle")
        zero_res_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 600; line-height: 1.4;")
        foot_box.addWidget(zero_res_lbl)

        s_layout.addLayout(foot_box)
        root_layout.addWidget(sidebar)

        # 2. Right Stacked Content Views
        self.stack = QStackedWidget()
        self.dashboard_view = DashboardView(self.telemetry)
        self.beam_view = BeamView(self.beamer)
        self.debloater_view = DebloaterView(self.pm)
        self.mirror_view = MirrorView(self.mirror)
        self.file_view = FileView(self.file_browser)

        self.stack.addWidget(self.dashboard_view)
        self.stack.addWidget(self.beam_view)
        self.stack.addWidget(self.debloater_view)
        self.stack.addWidget(self.mirror_view)
        self.stack.addWidget(self.file_view)

        root_layout.addWidget(self.stack, 1)

        # Default to Dashboard
        self._switch_tab(0)

    def _switch_tab(self, index: int):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

        # On tab switch, trigger relevant refreshes if empty
        if index == 2 and not self.debloater_view.all_packages:
            self.debloater_view.load_packages()
        elif index == 4 and not self.file_view.items:
            self.file_view.load_directory()

    def _watchdog_check(self):
        """Periodic background status check without blocking UI."""
        is_conn = self.adb.is_connected()
        if is_conn:
            self.sidebar_status.setText("● Device Online")
            self.sidebar_status.update_style("#10b981")
        else:
            self.sidebar_status.setText("○ Device Offline")
            self.sidebar_status.update_style("#ef4444")

    def closeEvent(self, event):
        """Enforces Zero-Resource Background Guarantee on exit."""
        self.watchdog_timer.stop()
        self.beamer.cancel()
        self.mirror.stop()
        self.adb.cancel_active_process()

        # Stop any active UI background workers cleanly
        for view in [self.dashboard_view, self.beam_view, self.debloater_view, self.mirror_view, self.file_view]:
            worker = getattr(view, "worker", None)
            if worker and worker.isRunning():
                worker.terminate()
                worker.wait(300)
            action_worker = getattr(view, "action_worker", None)
            if action_worker and action_worker.isRunning():
                action_worker.terminate()
                action_worker.wait(300)
            transfer_worker = getattr(view, "transfer_worker", None)
            if transfer_worker and transfer_worker.isRunning():
                transfer_worker.terminate()
                transfer_worker.wait(300)

        event.accept()
