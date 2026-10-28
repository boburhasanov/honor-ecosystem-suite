"""
Live Telemetry & Dashboard View for Honor Ecosystem Suite.
Presents true /proc/meminfo RAM state, battery diagnostics, storage meters, and ping latency.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QGridLayout, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from lib.honor_suite.core.telemetry import TelemetryService
from lib.honor_suite.ui.widgets.stat_card import StatCard
from lib.honor_suite.ui.widgets.badge import StatusBadge

class TelemetryWorker(QThread):
    data_ready = Signal(dict)

    def __init__(self, service: TelemetryService):
        super().__init__()
        self.service = service

    def run(self):
        data = self.service.get_overview()
        self.data_ready.emit(data)

class DashboardView(QWidget):
    def __init__(self, telemetry_service: TelemetryService):
        super().__init__()
        self.service = telemetry_service
        self.worker: TelemetryWorker = None
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(18)

        # Header Section: Device Model & Status Pill
        header_card = QFrame()
        header_card.setProperty("class", "CardFrame")
        h_layout = QHBoxLayout(header_card)
        h_layout.setContentsMargins(16, 14, 16, 14)

        v_info = QVBoxLayout()
        self.model_lbl = QLabel("📱 Honor Device")
        self.model_lbl.setStyleSheet("color: #f8fafc; font-size: 20px; font-weight: 800;")
        self.os_lbl = QLabel("MagicOS 9.0 • Android 16")
        self.os_lbl.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: 500;")
        v_info.addWidget(self.model_lbl)
        v_info.addWidget(self.os_lbl)
        h_layout.addLayout(v_info)

        h_layout.addStretch()

        self.status_badge = StatusBadge("Checking...", "#f59e0b")
        h_layout.addWidget(self.status_badge)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setProperty("class", "SecondaryButton")
        self.refresh_btn.clicked.connect(self.refresh_data)
        h_layout.addWidget(self.refresh_btn)

        main_layout.addWidget(header_card)

        # 4 Stat Cards in 2x2 Grid
        grid = QGridLayout()
        grid.setSpacing(16)

        # 1. Battery Diagnostics Card
        self.battery_card = StatCard(
            title="Battery & Health",
            icon="🔋",
            initial_value="--%",
            subtitle="Health: 100% SOH • 0 Cycles"
        )
        grid.addWidget(self.battery_card, 0, 0)

        # 2. RAM State Card (/proc/meminfo)
        self.ram_card = StatCard(
            title="Live RAM (/proc/meminfo)",
            icon="⚡",
            initial_value="-- GB",
            subtitle="Real-time Active & Cache Memory"
        )
        grid.addWidget(self.ram_card, 0, 1)

        # 3. Storage Meter Card
        self.storage_card = StatCard(
            title="Internal Storage",
            icon="💾",
            initial_value="-- GB",
            subtitle="Internal /storage/emulated"
        )
        grid.addWidget(self.storage_card, 1, 0)

        # 4. Wireless Telemetry Card
        self.link_card = StatCard(
            title="Wireless Telemetry",
            icon="📶",
            initial_value="-- ms",
            subtitle="Zero-Loss Low Latency Link"
        )
        grid.addWidget(self.link_card, 1, 1)

        main_layout.addLayout(grid)
        main_layout.addStretch()

    def refresh_data(self):
        """Asynchronously triggers telemetry collection without UI lockup."""
        if self.worker and self.worker.isRunning():
            return
        self.refresh_btn.setEnabled(False)
        self.worker = TelemetryWorker(self.service)
        self.worker.data_ready.connect(self._on_data_ready)
        self.worker.start()

    def _on_data_ready(self, data: dict):
        self.refresh_btn.setEnabled(True)

        if not data.get("connected"):
            self.status_badge.setText("Offline")
            self.status_badge.update_style("#ef4444")
            self.model_lbl.setText("Device Offline")
            self.os_lbl.setText("Connect via USB or turn on Wireless Debugging")
            self.battery_card.set_data("--", -1, "Device disconnected")
            self.ram_card.set_data("--", -1, "Unavailable")
            self.storage_card.set_data("--", -1, "Unavailable")
            self.link_card.set_data("-- ms", -1, f"Target: {data.get('target', 'None')}")
            return

        self.status_badge.setText("Online • Connected")
        self.status_badge.update_style("#10b981")
        self.model_lbl.setText(f"📱 {data.get('model', 'Honor Smartphone')}")
        self.os_lbl.setText(f"MagicOS Suite • {data.get('android', 'Android')}")

        # Battery
        b_lvl = data.get("battery_level", 0)
        b_stat = data.get("battery_status", "Normal")
        b_volt = data.get("battery_voltage_v", 0.0)
        b_temp = data.get("battery_temp_c", 0.0)
        b_soh = data.get("battery_soh", 100)
        b_cycles = data.get("battery_cycles", 0)
        self.battery_card.set_data(
            value=f"{b_lvl}%",
            progress_pct=b_lvl,
            subtitle=f"{b_stat} • {b_volt}V • {b_temp}°C • SOH: {b_soh}% ({b_cycles} Cycles)"
        )

        # RAM
        r_tot = data.get("ram_total_gb", 0.0)
        r_used = data.get("ram_used_gb", 0.0)
        r_free = data.get("ram_free_gb", 0.0)
        r_pct = data.get("ram_percent", 0)
        self.ram_card.set_data(
            value=f"{r_used:.1f} / {r_tot:.1f} GB",
            progress_pct=r_pct,
            subtitle=f"Used: {r_pct}% • Available: {r_free:.1f} GB"
        )

        # Storage
        s_tot = data.get("storage_total_gb", 0.0)
        s_used = data.get("storage_used_gb", 0.0)
        s_free = data.get("storage_free_gb", 0.0)
        s_pct = data.get("storage_percent", 0)
        self.storage_card.set_data(
            value=f"{s_used:.1f} / {s_tot:.1f} GB",
            progress_pct=s_pct,
            subtitle=f"Used: {s_pct}% • Free: {s_free:.1f} GB"
        )

        # Link
        ping = data.get("ping_ms", 0.0)
        target = data.get("target", "127.0.0.1")
        self.link_card.set_data(
            value=f"{ping} ms" if ping > 0 else "Direct USB",
            progress_pct=min(int(ping), 100) if ping > 0 else 0,
            subtitle=f"Endpoint: {target} • High Speed ADB Link"
        )
