"""
Robust Cross-Platform ADB Service for Honor Ecosystem Suite.
Manages ADB daemon execution, dynamic target discovery, and non-blocking command routing.
"""

import subprocess
import time
from typing import List, Tuple, Optional
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

    def get_target(self) -> str:
        """
        Dynamically finds the currently connected ADB device.
        Prioritizes connected USB/wireless device serial, then tries Wi-Fi hotspot gateway IP.
        """
        try:
            res = subprocess.run(
                [self.adb_bin, "devices"],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=get_creation_flags()
            )
            lines = res.stdout.strip().splitlines()
            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    self._target = parts[0]
                    return self._target
        except Exception:
            pass

        # Try automatic Wi-Fi gateway connection (hotspot mode)
        gw = get_default_gateway()
        if gw:
            target = f"{gw}:5555"
            try:
                subprocess.run(
                    [self.adb_bin, "connect", target],
                    capture_output=True,
                    timeout=2,
                    creationflags=get_creation_flags()
                )
                self._target = target
                return target
            except Exception:
                pass

        return self._target or "127.0.0.1:5555"

    def run_cmd(self, args: List[str], timeout: int = 10) -> Tuple[int, str, str]:
        """
        Executes ADB command targeted to current active device.
        Guarantees non-flickering execution on Windows with creationflags.
        """
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

    def is_connected(self) -> bool:
        """Checks if active device responds to get-state."""
        code, out, _ = self.run_cmd(["get-state"], timeout=2)
        return code == 0 and "device" in out

    def ensure_connected(self, max_retries: int = 5) -> bool:
        """Tries to re-establish connection if device dropped offline."""
        for _ in range(max_retries):
            if self.is_connected():
                return True
            target = self.get_target()
            subprocess.run(
                [self.adb_bin, "connect", target],
                capture_output=True,
                timeout=2,
                creationflags=get_creation_flags()
            )
            time.sleep(1)
        return False
