"""
Multi-Screen Collaboration & Screen Mirror View (powered by Scrcpy).
Features resolution presets (1440p/1080p/720p), audio bridge, and battery saver screen-off mode.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QCheckBox, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal
from lib.honor_suite.core.mirror_service import MirrorService

class MirrorLaunchWorker(QThread):
    finished_signal = Signal(bool, str)

    def __init__(self, service: MirrorService, preset: str, screen_off: bool, awake: bool, audio: bool):
        super().__init__()
        self.service = service
        self.preset = preset
        self.screen_off = screen_off
        self.awake = awake
        self.audio = audio

    def run(self):
        success, msg = self.service.launch(
            preset=self.preset,
            turn_screen_off=self.screen_off,
            stay_awake=self.awake,
            forward_audio=self.audio
        )
        self.finished_signal.emit(success, msg)

class MirrorView(QWidget):
    def __init__(self, mirror_service: MirrorService):
        super().__init__()
        self.mirror_service = mirror_service
        self.worker: MirrorLaunchWorker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        # Title Section
        title = QLabel("🖥️ Multi-Screen Collaboration (Scrcpy Screen Mirror)")
        title.setProperty("class", "CardTitle")
        title.setStyleSheet("font-size: 18px; font-weight: 800; color: #f8fafc;")
        layout.addWidget(title)

        desc = QLabel("Seamlessly mirror and control your Honor 400 Pro / Android smartphone from your Windows PC with mouse, keyboard gestures, shared clipboard, and audio streaming.")
        desc.setProperty("class", "CardDesc")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Main Settings Card
        card = QFrame()
        card.setProperty("class", "CardFrame")
        c_layout = QVBoxLayout(card)
        c_layout.setContentsMargins(20, 20, 20, 20)
        c_layout.setSpacing(14)

        # Preset Selector
        q_box = QHBoxLayout()
        q_lbl = QLabel("Display Preset:")
        q_lbl.setStyleSheet("color: #f8fafc; font-weight: 700; font-size: 13px;")
        q_box.addWidget(q_lbl)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("🌟 Ultra 1440p (60 FPS • 16 Mbps • Crystal Clear)", "1440p")
        self.preset_combo.addItem("⚡ Balanced 1080p (60 FPS • 10 Mbps • Low Latency)", "1080p")
        self.preset_combo.addItem("🍃 Eco 720p (30 FPS • 4 Mbps • Battery Saver)", "720p")
        q_box.addWidget(self.preset_combo, 1)
        c_layout.addLayout(q_box)

        # Checkbox Options
        self.chk_screen_off = QCheckBox("Turn off phone display while mirroring (saves phone battery & prevents heat)")
        self.chk_screen_off.setChecked(False)
        c_layout.addWidget(self.chk_screen_off)

        self.chk_stay_awake = QCheckBox("Keep phone awake while mirroring")
        self.chk_stay_awake.setChecked(True)
        c_layout.addWidget(self.chk_stay_awake)

        self.chk_audio = QCheckBox("Forward phone audio to PC speakers")
        self.chk_audio.setChecked(True)
        c_layout.addWidget(self.chk_audio)

        # Launch Button
        self.btn_launch = QPushButton("🚀 Launch Wireless Screen Mirror")
        self.btn_launch.setProperty("class", "PrimaryButton")
        self.btn_launch.setStyleSheet("font-size: 14px; padding: 12px 20px;")
        self.btn_launch.clicked.connect(self._launch_mirror)
        c_layout.addWidget(self.btn_launch)

        self.status_lbl = QLabel("Ready to launch")
        self.status_lbl.setProperty("class", "CardDesc")
        c_layout.addWidget(self.status_lbl)

        layout.addWidget(card)
        layout.addStretch()

    def _launch_mirror(self):
        preset = self.preset_combo.currentData()
        screen_off = self.chk_screen_off.isChecked()
        awake = self.chk_stay_awake.isChecked()
        audio = self.chk_audio.isChecked()

        self.btn_launch.setEnabled(False)
        self.status_lbl.setText("Starting Scrcpy session...")

        self.worker = MirrorLaunchWorker(self.mirror_service, preset, screen_off, awake, audio)
        self.worker.finished_signal.connect(self._on_launch_finished)
        self.worker.start()

    def _on_launch_finished(self, success: bool, msg: str):
        self.btn_launch.setEnabled(True)
        self.status_lbl.setText(msg)
        if not success:
            QMessageBox.warning(self, "Mirror Failed", msg)
