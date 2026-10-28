"""
Remote File Manager View for Honor Ecosystem Suite.
Allows exploring Android filesystem, downloading files, uploading to phone, and deletion.
"""

from typing import List, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox, QLineEdit
)
from PySide6.QtCore import Qt, QThread, Signal
from lib.honor_suite.core.file_browser import FileBrowserService

class FileListWorker(QThread):
    items_ready = Signal(list)

    def __init__(self, service: FileBrowserService, path: str):
        super().__init__()
        self.service = service
        self.path = path

    def run(self):
        items = self.service.list_directory(self.path)
        self.items_ready.emit(items)

class TransferActionWorker(QThread):
    action_finished = Signal(bool, str)

    def __init__(self, service: FileBrowserService, action: str, remote_path: str, local_path: str = ""):
        super().__init__()
        self.service = service
        self.action = action
        self.remote_path = remote_path
        self.local_path = local_path

    def run(self):
        if self.action == "pull":
            ok, msg = self.service.pull_file(self.remote_path, self.local_path)
        elif self.action == "push":
            ok, msg = self.service.push_file(self.local_path, self.remote_path)
        elif self.action == "delete":
            ok, msg = self.service.delete_item(self.remote_path)
        else:
            ok, msg = False, "Unknown action"
        self.action_finished.emit(ok, msg)

class FileView(QWidget):
    def __init__(self, browser_service: FileBrowserService):
        super().__init__()
        self.browser_service = browser_service
        self.current_path = "/storage/emulated/0"
        self.items: List[Dict] = []
        self.worker: FileListWorker = None
        self.transfer_worker: TransferActionWorker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # Title
        title = QLabel("📁 Remote Device File Explorer")
        title.setProperty("class", "CardTitle")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #f8fafc;")
        layout.addWidget(title)

        # Path & Navigation Toolbar
        nav_bar = QHBoxLayout()
        self.btn_up = QPushButton("⬆️ Up")
        self.btn_up.setProperty("class", "SecondaryButton")
        self.btn_up.clicked.connect(self._go_up)
        nav_bar.addWidget(self.btn_up)

        self.path_edit = QLineEdit(self.current_path)
        self.path_edit.returnPressed.connect(self._on_path_entered)
        nav_bar.addWidget(self.path_edit, 1)

        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setProperty("class", "SecondaryButton")
        self.btn_refresh.clicked.connect(self.load_directory)
        nav_bar.addWidget(self.btn_refresh)

        self.btn_upload = QPushButton("📤 Upload...")
        self.btn_upload.setProperty("class", "SecondaryButton")
        self.btn_upload.clicked.connect(self._upload_file)
        nav_bar.addWidget(self.btn_upload)

        self.btn_download = QPushButton("📥 Download Selected")
        self.btn_download.setProperty("class", "PrimaryButton")
        self.btn_download.clicked.connect(self._download_selected)
        nav_bar.addWidget(self.btn_download)

        self.btn_delete = QPushButton("🗑️ Delete")
        self.btn_delete.setProperty("class", "DangerButton")
        self.btn_delete.clicked.connect(self._delete_selected)
        nav_bar.addWidget(self.btn_delete)

        layout.addLayout(nav_bar)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Size", "Date Modified"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        layout.addWidget(self.table)

        self.status_lbl = QLabel("Ready")
        self.status_lbl.setProperty("class", "CardDesc")
        layout.addWidget(self.status_lbl)

    def load_directory(self):
        if self.worker and self.worker.isRunning():
            return
        self.path_edit.setText(self.current_path)
        self.status_lbl.setText(f"Loading {self.current_path}...")
        self.worker = FileListWorker(self.browser_service, self.current_path)
        self.worker.items_ready.connect(self._on_items_ready)
        self.worker.start()

    def _on_items_ready(self, items: list):
        self.items = items
        self.status_lbl.setText(f"{len(items)} items in {self.current_path}")
        self.table.setRowCount(len(items))

        for row, it in enumerate(items):
            icon = "📁 " if it["is_dir"] else "📄 "
            name_item = QTableWidgetItem(icon + it["name"])
            name_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            name_item.setForeground(Qt.white)
            self.table.setItem(row, 0, name_item)

            type_item = QTableWidgetItem("Folder" if it["is_dir"] else "File")
            type_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 1, type_item)

            size_item = QTableWidgetItem(it["size_str"])
            size_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 2, size_item)

            date_item = QTableWidgetItem(it["date"])
            date_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 3, date_item)

    def _go_up(self):
        if self.current_path in ["/", "/storage", "/storage/emulated"]:
            return
        parts = self.current_path.rstrip("/").split("/")
        if len(parts) > 1:
            self.current_path = "/".join(parts[:-1]) or "/"
            self.load_directory()

    def _on_path_entered(self):
        self.current_path = self.path_edit.text().strip()
        self.load_directory()

    def _on_cell_double_clicked(self, row, col):
        if row < len(self.items):
            it = self.items[row]
            if it["is_dir"]:
                self.current_path = it["path"]
                self.load_directory()
            else:
                self._download_selected()

    def _get_selected_item(self) -> Dict:
        row = self.table.currentRow()
        if row >= 0 and row < len(self.items):
            return self.items[row]
        return None

    def _download_selected(self):
        it = self._get_selected_item()
        if not it:
            QMessageBox.information(self, "No Selection", "Please select a file or folder to download.")
            return

        dest_dir = QFileDialog.getExistingDirectory(self, "Select Download Destination Folder")
        if dest_dir:
            self.status_lbl.setText(f"Downloading {it['name']}...")
            self.transfer_worker = TransferActionWorker(self.browser_service, "pull", it["path"], dest_dir)
            self.transfer_worker.action_finished.connect(self._on_action_finished)
            self.transfer_worker.start()

    def _upload_file(self):
        local_file, _ = QFileDialog.getOpenFileName(self, "Select File to Upload")
        if local_file:
            self.status_lbl.setText(f"Uploading {local_file}...")
            self.transfer_worker = TransferActionWorker(self.browser_service, "push", self.current_path, local_file)
            self.transfer_worker.action_finished.connect(self._on_action_finished)
            self.transfer_worker.start()

    def _delete_selected(self):
        it = self._get_selected_item()
        if not it:
            return
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{it['name']}' from your phone?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.status_lbl.setText(f"Deleting {it['name']}...")
            self.transfer_worker = TransferActionWorker(self.browser_service, "delete", it["path"])
            self.transfer_worker.action_finished.connect(self._on_action_finished)
            self.transfer_worker.start()

    def _on_action_finished(self, success: bool, msg: str):
        self.status_lbl.setText(msg)
        self.load_directory()
