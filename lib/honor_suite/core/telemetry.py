"""
Live Hardware Telemetry Service for Honor Ecosystem Suite.
Gathers high-precision battery diagnostics, /proc/meminfo RAM state, and storage metrics.
"""

import re
from typing import Dict, Any
from lib.honor_suite.core.adb_service import AdbService
from lib.honor_suite.utils.platform_helper import ping_host, get_default_gateway

class TelemetryService:
    def __init__(self, adb: AdbService):
        self.adb = adb

    def get_overview(self) -> Dict[str, Any]:
        """
        Polls device overview, battery, RAM, storage, and network latency.
        Returns a structured dictionary ready for UI presentation.
        """
        overview: Dict[str, Any] = {
            "connected": False,
            "target": self.adb.get_target(),
            "model": "Honor Device",
            "android": "Android",
            "battery_level": 0,
            "battery_status": "Unknown",
            "battery_cycles": 0,
            "battery_soh": 100,
            "battery_voltage_v": 0.0,
            "battery_temp_c": 0.0,
            "storage_total_gb": 0.0,
            "storage_used_gb": 0.0,
            "storage_free_gb": 0.0,
            "storage_percent": 0,
            "ram_total_gb": 0.0,
            "ram_used_gb": 0.0,
            "ram_free_gb": 0.0,
            "ram_percent": 0,
            "ping_ms": 0.0
        }

        if not self.adb.is_connected():
            return overview

        overview["connected"] = True

        # 1. Device Model & OS
        _, m_out, _ = self.adb.run_cmd(["shell", "getprop", "ro.product.model"], timeout=2)
        if m_out.strip():
            overview["model"] = m_out.strip()

        _, a_out, _ = self.adb.run_cmd(["shell", "getprop", "ro.build.version.release"], timeout=2)
        if a_out.strip():
            overview["android"] = f"Android {a_out.strip()}"

        # 2. Battery Diagnostics
        _, b_out, _ = self.adb.run_cmd(["shell", "dumpsys", "battery"], timeout=3)
        for line in b_out.splitlines():
            line = line.strip()
            if line.startswith("level:"):
                try:
                    overview["battery_level"] = int(line.split(":")[1].strip())
                except ValueError:
                    pass
            elif line.startswith("status:"):
                st = line.split(":")[1].strip()
                overview["battery_status"] = "Charging" if st == "2" else "Discharging"
            elif line.startswith("voltage:"):
                try:
                    overview["battery_voltage_v"] = round(int(line.split(":")[1].strip()) / 1000.0, 2)
                except ValueError:
                    pass
            elif line.startswith("temperature:"):
                try:
                    overview["battery_temp_c"] = round(int(line.split(":")[1].strip()) / 10.0, 1)
                except ValueError:
                    pass

        # 3. Battery Cycles & State of Health (SOH)
        _, p8_out, _ = self.adb.run_cmd(["shell", "service", "call", "batteryproperties", "1", "i32", "8"], timeout=2)
        m8 = re.search(r"00000001\s+([0-9a-fA-F]{8})", p8_out)
        if m8:
            overview["battery_cycles"] = int(m8.group(1), 16)

        _, p10_out, _ = self.adb.run_cmd(["shell", "service", "call", "batteryproperties", "1", "i32", "10"], timeout=2)
        m10 = re.search(r"00000001\s+([0-9a-fA-F]{8})", p10_out)
        if m10:
            overview["battery_soh"] = int(m10.group(1), 16)

        # 4. Storage (/storage/emulated)
        _, df_out, _ = self.adb.run_cmd(["shell", "df", "-k", "/storage/emulated"], timeout=3)
        lines = df_out.strip().splitlines()
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 5:
                try:
                    total_k = int(parts[1])
                    used_k = int(parts[2])
                    free_k = int(parts[3])
                    overview["storage_total_gb"] = round(total_k / (1024 * 1024), 1)
                    overview["storage_used_gb"] = round(used_k / (1024 * 1024), 1)
                    overview["storage_free_gb"] = round(free_k / (1024 * 1024), 1)
                    overview["storage_percent"] = int(parts[4].replace("%", ""))
                except (ValueError, IndexError):
                    pass

        # 5. True Real-Time RAM from /proc/meminfo
        _, mem_out, _ = self.adb.run_cmd(["shell", "cat", "/proc/meminfo"], timeout=3)
        mem: Dict[str, int] = {}
        for line in mem_out.splitlines():
            parts = line.split(":")
            if len(parts) == 2:
                k = parts[0].strip()
                v = parts[1].strip().split()[0]
                if v.isdigit():
                    mem[k] = int(v)

        total_kb = mem.get("MemTotal", 0)
        avail_kb = mem.get("MemAvailable", 0)
        used_kb = max(total_kb - avail_kb, 0)
        if total_kb > 0:
            overview["ram_total_gb"] = round(total_kb / (1024 * 1024), 1)
            overview["ram_used_gb"] = round(used_kb / (1024 * 1024), 1)
            overview["ram_free_gb"] = round(avail_kb / (1024 * 1024), 1)
            overview["ram_percent"] = round((used_kb / total_kb) * 100)

        # 6. Network Latency
        gw = get_default_gateway()
        if gw:
            ping_val = ping_host(gw, timeout_ms=500)
            if ping_val is not None:
                overview["ping_ms"] = round(ping_val, 1)

        return overview
