"""
Xiaomi Flash Tool Style Debloater View for Honor Ecosystem Suite.
Categorized tabs, instant search, safe batch uninstallation, and 1-click restore from Recycle Bin.
"""

from typing import List, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QTabBar, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from lib.honor_suite.core.package_manager import PackageManagerService
from lib.honor_suite.ui.widgets.badge import StatusBadge

class PackageQueryWorker(QThread):
    packages_ready = Signal(list)

    def __init__(self, service: PackageManagerService):
        super().__init__()
        self.service = service

    def run(self):
        pkgs = self.service.get_all_packages()
        self.packages_ready.emit(pkgs)

class BatchActionWorker(QThread):
    action_finished = Signal(str)

    def __init__(self, service: PackageManagerService, packages: List[str], action: str):
        super().__init__()
        self.service = service
        self.packages = packages
        self.action = action

    def run(self):
        success_count = 0
        total = len(self.packages)
        for pkg in self.packages:
            if self.action == "uninstall":
                ok, _ = self.service.uninstall_package(pkg)
            elif self.action == "restore":
                ok, _ = self.service.restore_package(pkg)
            elif self.action == "disable":
                ok, _ = self.service.disable_package(pkg)
            elif self.action == "enable":
                ok, _ = self.service.enable_package(pkg)
            if ok:
                success_count += 1
        self.action_finished.emit(f"Processed {success_count}/{total} packages successfully!")

class DebloaterView(QWidget):
    def __init__(self, pm_service: PackageManagerService):
        super().__init__()
        self.pm_service = pm_service
        self.all_packages: List[Dict] = []
        self.filtered_packages: List[Dict] = []
        self.worker: PackageQueryWorker = None
        self.action_worker: BatchActionWorker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Title Section
        title = QLabel("🧹 Xiaomi Flash Tool Style Debloater & App Manager")
        title.setProperty("class", "CardTitle")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #f8fafc;")
        layout.addWidget(title)

        desc = QLabel("Safely uninstall bloatware without root access. Uninstalled apps are kept in the Recycle Bin and can be restored in 1 click at any time.")
        desc.setProperty("class", "CardDesc")
        layout.addWidget(desc)

        # Controls Bar: Search & Action Buttons
        ctrl_bar = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search by application name or package ID...")
        self.search_box.textChanged.connect(self._apply_filter)
        ctrl_bar.addWidget(self.search_box)

        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setProperty("class", "SecondaryButton")
        self.btn_refresh.clicked.connect(self.load_packages)
        ctrl_bar.addWidget(self.btn_refresh)

        self.btn_select_all = QPushButton("☑️ Toggle All")
        self.btn_select_all.setProperty("class", "SecondaryButton")
        self.btn_select_all.clicked.connect(self._toggle_select_all)
        ctrl_bar.addWidget(self.btn_select_all)

        layout.addLayout(ctrl_bar)

        # Filter Tabs
        self.tab_bar = QTabBar()
        self.tab_bar.addTab("All Packages")
        self.tab_bar.addTab("Recommended (Bloatware)")
        self.tab_bar.addTab("System Apps")
        self.tab_bar.addTab("User Installed")
        self.tab_bar.addTab("Recycle Bin (Uninstalled)")
        self.tab_bar.currentChanged.connect(self._apply_filter)
        layout.addWidget(self.tab_bar)

        # Table Widget
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Select", "Application Name", "Package Identifier", "Safety Status", "State"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # Bottom Batch Actions
        bottom_bar = QHBoxLayout()
        self.count_lbl = QLabel("0 packages loaded")
        self.count_lbl.setProperty("class", "CardDesc")
        bottom_bar.addWidget(self.count_lbl)

        bottom_bar.addStretch()

        self.btn_uninstall = QPushButton("🗑️ Uninstall Selected (--user 0)")
        self.btn_uninstall.setProperty("class", "DangerButton")
        self.btn_uninstall.clicked.connect(self._uninstall_selected)
        bottom_bar.addWidget(self.btn_uninstall)

        self.btn_restore = QPushButton("♻️ 1-Click Restore Selected")
        self.btn_restore.setProperty("class", "PrimaryButton")
        self.btn_restore.clicked.connect(self._restore_selected)
        bottom_bar.addWidget(self.btn_restore)

        layout.addLayout(bottom_bar)

    def load_packages(self):
        if self.worker and self.worker.isRunning():
            return
        self.btn_refresh.setEnabled(False)
        self.count_lbl.setText("Scanning packages from device...")
        self.worker = PackageQueryWorker(self.pm_service)
        self.worker.packages_ready.connect(self._on_packages_ready)
        self.worker.start()

    def _on_packages_ready(self, packages: list):
        self.btn_refresh.setEnabled(True)
        self.all_packages = packages
        self._apply_filter()

    def _apply_filter(self):
        query = self.search_box.text().strip().lower()
        tab_idx = self.tab_bar.currentIndex()

        self.filtered_packages = []
        for p in self.all_packages:
            name_match = query in p["name"].lower() or query in p["pkg"].lower()
            if not name_match:
                continue

            # Tab filtering
            if tab_idx == 1:  # Recommended
                if p["safety_label"] != "Safe to Remove":
                    continue
            elif tab_idx == 2:  # System Apps
                if p["type"] != "System":
                    continue
            elif tab_idx == 3:  # User Installed
                if p["type"] != "User":
                    continue
            elif tab_idx == 4:  # Recycle Bin (Uninstalled)
                if p["status"] != "Uninstalled":
                    continue

            self.filtered_packages.append(p)

        self._render_table()

    def _render_table(self):
        self.table.setRowCount(len(self.filtered_packages))
        self.count_lbl.setText(f"Showing {len(self.filtered_packages)} / {len(self.all_packages)} packages")

        for row, p in enumerate(self.filtered_packages):
            # Checkbox
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            chk_item.setCheckState(Qt.Checked if p["selected"] else Qt.Unchecked)
            self.table.setItem(row, 0, chk_item)

            # Name
            name_item = QTableWidgetItem(p["name"])
            name_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            name_item.setForeground(Qt.white)
            self.table.setItem(row, 1, name_item)

            # Package
            pkg_item = QTableWidgetItem(p["pkg"])
            pkg_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 2, pkg_item)

            # Safety Badge
            badge_widget = StatusBadge(p["safety_label"], p["safety_color"])
            self.table.setCellWidget(row, 3, badge_widget)

            # Status State
            status_color = "#10b981" if p["status"] == "Active" else "#ef4444"
            status_badge = StatusBadge(p["status"], status_color)
            self.table.setCellWidget(row, 4, status_badge)

    def _toggle_select_all(self):
        any_unchecked = False
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 0)
            if item and item.checkState() == Qt.Unchecked:
                any_unchecked = True
                break

        target_state = Qt.Checked if any_unchecked else Qt.Unchecked
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 0)
            if item:
                item.setCheckState(target_state)

    def _get_selected_pkgs(self) -> List[str]:
        selected = []
        for i in range(self.table.rowCount()):
            item = self.table.item(i, 0)
            if item and item.checkState() == Qt.Checked:
                pkg_item = self.table.item(i, 2)
                if pkg_item:
                    selected.append(pkg_item.text())
        return selected

    def _uninstall_selected(self):
        pkgs = self._get_selected_pkgs()
        if not pkgs:
            QMessageBox.information(self, "No Selection", "Please check at least one package to uninstall.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Batch Uninstall",
            f"Are you sure you want to uninstall {len(pkgs)} selected packages?\n\n(Note: Packages are safely uninstalled for User 0 and can be restored from the Recycle Bin).",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._execute_batch(pkgs, "uninstall")

    def _restore_selected(self):
        pkgs = self._get_selected_pkgs()
        if not pkgs:
            QMessageBox.information(self, "No Selection", "Please check at least one package to restore.")
            return

        self._execute_batch(pkgs, "restore")

    def _execute_batch(self, pkgs: List[str], action: str):
        self.btn_uninstall.setEnabled(False)
        self.btn_restore.setEnabled(False)
        self.count_lbl.setText(f"Executing {action} on {len(pkgs)} packages...")

        self.action_worker = BatchActionWorker(self.pm_service, pkgs, action)
        self.action_worker.action_finished.connect(self._on_action_finished)
        self.action_worker.start()

    def _on_action_finished(self, msg: str):
        self.btn_uninstall.setEnabled(True)
        self.btn_restore.setEnabled(True)
        self.count_lbl.setText(msg)
        self.load_packages()
