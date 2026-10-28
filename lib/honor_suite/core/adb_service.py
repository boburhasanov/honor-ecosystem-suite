"""
Robust Cross-Platform ADB Service for Honor Ecosystem Suite.
Manages ADB daemon execution, dynamic target discovery, and non-blocking command routing.
Supports 1-Click USB-to-Wireless Magic Handshake and auto-hotspot reconnection.
"""

import subprocess
import time
import re
from typing import List, Tuple, Optional, Dict
from lib.honor_suite.utils.platform_helper import (
    find_executable,
    get_creation_flags,
    get_default_gateway
)

class AdbService:
    def __init__(self):
        self._target: Optional[str] = None
        self._last_gw: Optional[str] = None
        self.cancel_requested: bool = False
        self.active_proc: Optional[subprocess.Popen] = None
        self.adb_bin = find_executable("adb") or "adb"

    def cancel_active_process(self):
        """Cancels running transfer or subprocess immediately."""
        self.cancel_requested = True
        if self.active_proc and self.active_proc.poll() is None:
            try:
                self.active_proc.terminate()
            except Exception:
                pass

    def is_cancelled(self) -> bool:
        return self.cancel_requested

    def is_connected(self) -> bool:
        """
        Instant non-blocking check if any device is currently connected.
        Executes 'adb devices' with a 1-second timeout.
        If no device in list, returns False immediately in ~20ms!
        """
        if not self.adb_bin:
            return False
        try:
            res = subprocess.run(
                [self.adb_bin, "devices"],
                capture_output=True,
                text=True,
                timeout=1,
                creationflags=get_creation_flags()
            )
            for line in res.stdout.strip().splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    self._target = parts[0]
                    return True
        except Exception:
            pass
        return False

    def get_target(self) -> str:
        """
        Dynamically returns the currently connected device serial or IP.
        Fast and non-blocking (never executes blocking connect calls).
        """
        if self.is_connected():
            return self._target or "device"
        return self._target or "127.0.0.1:5555"

    def try_auto_connect_gateway(self) -> bool:
        """
        Attempts to connect to hotspot gateway once if not currently connected.
        Runs safely in background worker thread.
        """
        if self.is_connected():
            return True
        gw = get_default_gateway()
        if gw:
            target = f"{gw}:5555"
            try:
                conn_res = subprocess.run(
                    [self.adb_bin, "connect", target],
                    capture_output=True,
                    text=True,
                    timeout=1.5,
                    creationflags=get_creation_flags()
                )
                if "connected" in conn_res.stdout.lower():
                    self._target = target
                    return True
            except Exception:
                pass
        return False

    def get_connection_type(self) -> str:
        """Returns 'wireless', 'usb', or 'offline'."""
        if not self.is_connected():
            return "offline"
        target = self.get_target()
        return "wireless" if ":" in target else "usb"

    def get_device_ip(self) -> Optional[str]:
        """Discovers the IP address of the active phone across wlan0, ap0, or hotspot."""
        if not self.is_connected():
            return None

        # 1. Try ip addr show wlan0 or ap0
        for iface in ["wlan0", "ap0", "rndis0", "wlan1"]:
            code, out, _ = self.run_cmd(["shell", "ip", "-f", "inet", "addr", "show", iface], timeout=2)
            if code == 0 and "inet " in out:
                m = re.search(r"inet\s+(\d+\.\d+\.\d+\.\d+)", out)
                if m:
                    ip = m.group(1)
                    if not ip.startswith("127."):
                        return ip

        # 2. Try getprop dhcp.wlan0.ipaddress
        code, out, _ = self.run_cmd(["shell", "getprop", "dhcp.wlan0.ipaddress"], timeout=2)
        if code == 0 and out.strip():
            return out.strip()

        # 3. Check host default gateway (Hotspot gateway)
        gw = get_default_gateway()
        if gw and gw != "127.0.0.1":
            return gw

        return None

    def enable_wireless_mode(self) -> Tuple[bool, str, str]:
        """
        1-Click USB-to-Wireless Magic Handshake:
        1. Ensures phone is connected via USB.
        2. Discovers phone IP (or hotspot gateway).
        3. Configures adb tcpip 5555.
        4. Connects over TCP and updates target.
        Returns (success, message, target_ip).
        """
        if not self.is_connected():
            return False, "Qurilma topilmadi. Avval telefonni USB kabel orqali ulang.", ""

        # Find phone's wireless IP
        phone_ip = self.get_device_ip()
        if not phone_ip:
            phone_ip = get_default_gateway() or "192.168.43.1"

        # Switch ADB daemon on device to listen on port 5555
        self.run_cmd(["tcpip", "5555"], timeout=4)
        time.sleep(1.0)  # Give adbd time to restart on port 5555

        # Connect over wireless
        target_endpoint = f"{phone_ip}:5555"
        conn_res = subprocess.run(
            [self.adb_bin, "connect", target_endpoint],
            capture_output=True,
            text=True,
            timeout=4,
            creationflags=get_creation_flags()
        )

        if "connected" in conn_res.stdout.lower():
            self._target = target_endpoint
            return True, f"Simsiz rejim faollashtirildi ({target_endpoint})! Endi USB kabelni bemalol uzishingiz mumkin.", target_endpoint
        else:
            return False, f"Port 5555 ochildi, lekin ulanib bo'lmadi ({phone_ip}). Telefon va noutbuk bir xil Wi-Fi/Hotspot tarmog'idaligini tekshiring.", target_endpoint

    def run_cmd(self, args: List[str], timeout: int = 10) -> Tuple[int, str, str]:
        """
        Executes ADB command targeted to current active device.
        Guarantees non-flickering execution on Windows with creationflags.
        """
        if not self.adb_bin:
            return -1, "", "ADB executable not found"

        target = self.get_target()
        cmd = [self.adb_bin, "-s", target] + args
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=get_creation_flags()
            )
            return res.returncode, res.stdout, res.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    def ensure_connected(self, max_retries: int = 3) -> bool:
        """Tries to re-establish connection if device dropped offline."""
        for _ in range(max_retries):
            if self.is_connected():
                return True
            target = self.get_target()
            subprocess.run(
                [self.adb_bin, "connect", target],
                capture_output=True,
                timeout=1.5,
                creationflags=get_creation_flags()
            )
            time.sleep(0.5)
        return False
