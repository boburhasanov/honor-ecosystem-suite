"""
Real-Time Speedometer and Transfer Instrument Widget for Fast Beam.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt

class SpeedometerWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setProperty("class", "CardFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header
        h_layout = QHBoxLayout()
        title = QLabel("⚡ High-Speed Beam Instrument")
        title.setProperty("class", "CardTitle")
        h_layout.addWidget(title)
        h_layout.addStretch()

        self.speed_lbl = QLabel("0.0 MB/s")
        self.speed_lbl.setStyleSheet("color: #10b981; font-size: 28px; font-weight: 800;")
        h_layout.addWidget(self.speed_lbl)
        layout.addLayout(h_layout)

        # Main Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(14)
        layout.addWidget(self.progress_bar)

        # Footer Metrics (Files count & Bytes transferred)
        footer_layout = QHBoxLayout()
        self.status_msg = QLabel("Ready to beam")
        self.status_msg.setProperty("class", "CardDesc")
        footer_layout.addWidget(self.status_msg)

        footer_layout.addStretch()

        self.bytes_lbl = QLabel("0 MB / 0 MB")
        self.bytes_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600;")
        footer_layout.addWidget(self.bytes_lbl)
        layout.addLayout(footer_layout)

    def update_instrument(self, speed_mb: float, fraction: float, message: str, sent_bytes: int, total_bytes: int):
        self.speed_lbl.setText(f"{speed_mb:.1f} MB/s")
        self.progress_bar.setValue(int(fraction * 100))
        self.status_msg.setText(message)

        sent_mb = sent_bytes / (1024 * 1024)
        total_mb = total_bytes / (1024 * 1024)
        if total_mb >= 1024:
            self.bytes_lbl.setText(f"{sent_mb/1024:.2f} GB / {total_mb/1024:.2f} GB")
        else:
            self.bytes_lbl.setText(f"{sent_mb:.1f} MB / {total_mb:.1f} MB")
