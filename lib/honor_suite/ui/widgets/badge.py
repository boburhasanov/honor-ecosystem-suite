"""
Semantic Status Badge for Honor Ecosystem Suite.
"""

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt

class StatusBadge(QLabel):
    def __init__(self, text: str = "Active", bg_color: str = "#10b981", text_color: str = "#ffffff"):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.update_style(bg_color, text_color)

    def update_style(self, bg_color: str, text_color: str = "#ffffff"):
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                font-size: 11px;
                font-weight: 700;
                padding: 3px 8px;
                border-radius: 6px;
            }}
        """)
