"""
Fast Beam (70+ MB/s) Wireless File Beamer View for Honor Ecosystem Suite.
Features Drag & Drop, Apple Media Guard, Speedometer instrument, and MediaStore indexing.
"""

from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QComboBox, QCheckBox, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from lib.honor_suite.core.file_beamer import FileBeamer
from lib.honor_suite.ui.widgets.speedo import SpeedometerWidget

class BeamWorker(QThread):
    progress_signal = Signal(dict)
    finished_signal = Signal(bool, str)

    def __init__(self, beamer: FileBeamer, local_path: str, remote_dir: str, auto_apple: bool):
        super().__init__()
        self.beamer = beamer
        self.local_path = local_path
        self.remote_dir = remote_dir
        self.auto_apple = auto_apple

    def run(self):
        success, msg = self.beamer.beam(
            local_path=self.local_path,
            remote_dir=self.remote_dir,
            progress_cb=self.progress_signal.emit,
            auto_convert_apple=self.auto_apple
        )
        self.finished_signal.emit(success, msg)

class DropZone(QFrame):
    file_dropped = Signal(str)

    def __init__(self):
        super().__init__()
        self.setProperty("class", "CardFrame")
        self.setAcceptDrops(True)
        self.setMinimumHeight(140)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_lbl = QLabel("📁")
        self.icon_lbl.setStyleSheet("font-size: 36px;")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_lbl)

        self.text_lbl = QLabel("Drag & Drop Files or Folders Here")
        self.text_lbl.setStyleSheet("color: #f8fafc; font-size: 15px; font-weight: 700;")
        self.text_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.text_lbl)

        self.sub_lbl = QLabel("or use the browse buttons below (70+ MB/s Fast Beam)")
        self.sub_lbl.setProperty("class", "CardDesc")
        self.sub_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.sub_lbl)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("border: 2px dashed #38bdf8; background-color: #1e293b;")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event):
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.file_dropped.emit(path)

class BeamView(QWidget):
    def __init__(self, beamer: FileBeamer):
        super().__init__()
        self.beamer = beamer
        self.selected_path: str = ""
        self.worker: BeamWorker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header Title
        title = QLabel("🚀 Fast Beam (70+ MB/s Media Synchronization)")
        title.setProperty("class", "CardTitle")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #f8fafc;")
        layout.addWidget(title)

        desc = QLabel("Direct high-speed stream to your Honor device. Automatically transcodes Apple HEIC/MOV and scans photos into MagicOS Gallery.")
        desc.setProperty("class", "CardDesc")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Drag and Drop Zone
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self._set_selected_path)
        layout.addWidget(self.drop_zone)

        # File Selection Actions
        btn_box = QHBoxLayout()
        self.btn_browse_file = QPushButton("📄 Select Files...")
        self.btn_browse_file.setProperty("class", "SecondaryButton")
        self.btn_browse_file.clicked.connect(self._browse_file)
        btn_box.addWidget(self.btn_browse_file)

        self.btn_browse_folder = QPushButton("📂 Select Folder...")
        self.btn_browse_folder.setProperty("class", "SecondaryButton")
        self.btn_browse_folder.clicked.connect(self._browse_folder)
        btn_box.addWidget(self.btn_browse_folder)

        btn_box.addStretch()

        self.dest_combo = QComboBox()
        self.dest_combo.addItem("📸 Camera Gallery (/DCIM/Camera)", "/storage/emulated/0/DCIM/Camera")
        self.dest_combo.addItem("📥 Downloads (/Download)", "/storage/emulated/0/Download")
        self.dest_combo.addItem("🎵 Music Folder (/Music)", "/storage/emulated/0/Music")
        self.dest_combo.addItem("🎬 Movies Folder (/Movies)", "/storage/emulated/0/Movies")
        btn_box.addWidget(self.dest_combo)

        layout.addLayout(btn_box)

        # Toggles
        self.chk_apple = QCheckBox("🛡️ Apple Media Guard: Auto-convert .HEIC to .JPG & .MOV to .MP4 via FFmpeg")
        self.chk_apple.setChecked(True)
        layout.addWidget(self.chk_apple)

        # Speedometer Instrument
        self.speedo = SpeedometerWidget()
        layout.addWidget(self.speedo)

        # Action Buttons: Beam & Cancel
        action_box = QHBoxLayout()
        self.btn_beam = QPushButton("⚡ Start Fast Beam (70 MB/s)")
        self.btn_beam.setProperty("class", "PrimaryButton")
        self.btn_beam.clicked.connect(self._start_beam)
        action_box.addWidget(self.btn_beam)

        self.btn_cancel = QPushButton("❌ Cancel Beam")
        self.btn_cancel.setProperty("class", "DangerButton")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._cancel_beam)
        action_box.addWidget(self.btn_cancel)

        action_box.addStretch()
        layout.addLayout(action_box)

        layout.addStretch()

    def _browse_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select File to Beam")
        if f:
            self._set_selected_path(f)

    def _browse_folder(self):
        d = QFileDialog.getExistingDirectory(self, "Select Folder to Beam")
        if d:
            self._set_selected_path(d)

    def _set_selected_path(self, path: str):
        self.selected_path = path
        p = Path(path)
        self.drop_zone.text_lbl.setText(f"Selected: {p.name}")
        self.drop_zone.sub_lbl.setText(f"Path: {str(p)}")

    def _start_beam(self):
        if not self.selected_path:
            self.speedo.update_instrument(0.0, 0.0, "Please select a file or folder first!", 0, 1)
            return

        remote_dir = self.dest_combo.currentData()
        auto_apple = self.chk_apple.isChecked()

        self.btn_beam.setEnabled(False)
        self.btn_cancel.setEnabled(True)

        self.worker = BeamWorker(self.beamer, self.selected_path, remote_dir, auto_apple)
        self.worker.progress_signal.connect(self._on_progress)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.start()

    def _cancel_beam(self):
        self.beamer.cancel()
        self.btn_cancel.setEnabled(False)

    def _on_progress(self, data: dict):
        speed_mb = data.get("speed_mb", 0.0)
        fraction = data.get("fraction", 0.0)
        msg = data.get("message", "Processing...")
        sent = data.get("sent_bytes", 0)
        total = data.get("total_bytes", 1)
        self.speedo.update_instrument(speed_mb, fraction, msg, sent, total)

    def _on_finished(self, success: bool, msg: str):
        self.btn_beam.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.speedo.status_msg.setText(msg)
