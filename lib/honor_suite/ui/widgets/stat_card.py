"""
Telemetry Metric Stat Card Widget.
Displays a rounded card with icon, title, large value, progress bar, and descriptive details.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt

class StatCard(QFrame):
    def __init__(self, title: str, icon: str = "📊", initial_value: str = "--", subtitle: str = ""):
        super().__init__()
        self.setProperty("class", "CardFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Header: Icon + Title
        header_layout = QHBoxLayout()
        self.title_lbl = QLabel(f"{icon}  {title}")
        self.title_lbl.setProperty("class", "CardTitle")
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Large Metric Value
        self.val_lbl = QLabel(initial_value)
        self.val_lbl.setStyleSheet("color: #38bdf8; font-size: 26px; font-weight: 800;")
        layout.addWidget(self.val_lbl)

        # Animated Progress Bar (Optional)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(8)
        layout.addWidget(self.progress)

        # Subtitle / Details
        self.sub_lbl = QLabel(subtitle)
        self.sub_lbl.setProperty("class", "CardDesc")
        self.sub_lbl.setWordWrap(True)
        layout.addWidget(self.sub_lbl)

    def set_data(self, value: str, progress_pct: int = -1, subtitle: str = ""):
        self.val_lbl.setText(value)
        if progress_pct >= 0:
            self.progress.setVisible(True)
            self.progress.setValue(min(max(progress_pct, 0), 100))
        else:
            self.progress.setVisible(False)

        if subtitle:
            self.sub_lbl.setText(subtitle)
