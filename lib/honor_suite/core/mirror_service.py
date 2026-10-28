"""
Multi-Screen Collaboration & Wireless Mirroring Service (powered by Scrcpy).
Configures ultra low-latency 1440p/1080p/720p presets, bi-directional audio bridge, and battery saver.
"""

import subprocess
from typing import Optional, Tuple, List
from lib.honor_suite.core.adb_service import AdbService
from lib.honor_suite.utils.platform_helper import find_executable, get_creation_flags

class MirrorService:
    def __init__(self, adb: AdbService):
        self.adb = adb
        self.scrcpy_bin = find_executable("scrcpy") or "scrcpy"
        self.active_proc: Optional[subprocess.Popen] = None

    def launch(
        self,
        preset: str = "1440p",
        turn_screen_off: bool = False,
        stay_awake: bool = True,
        forward_audio: bool = True
    ) -> Tuple[bool, str]:
        """
        Launches Scrcpy screen mirror in a standalone GUI process.
        """
        if not self.adb.is_connected():
            self.adb.ensure_connected(max_retries=2)

        if not self.adb.is_connected():
            return False, "Device is offline. Turn on Wireless Debugging or connect USB."

        target = self.adb.get_target()

        if preset == "1440p":
            max_size = "1440"
            bit_rate = "16M"
            max_fps = "60"
        elif preset == "1080p":
            max_size = "1080"
            bit_rate = "10M"
            max_fps = "60"
        else:
            max_size = "720"
            bit_rate = "4M"
            max_fps = "30"

        cmd: List[str] = [
            self.scrcpy_bin,
            "-s", target,
            f"--window-title=Honor Suite Screen Mirror ({preset} 60 FPS)",
            "--video-codec=h264",
            "-m", max_size,
            "-b", bit_rate,
            f"--max-fps={max_fps}"
        ]

        if stay_awake:
            cmd.append("--stay-awake")
        if turn_screen_off:
            cmd.append("--turn-screen-off")
        if not forward_audio:
            cmd.append("--no-audio")

        try:
            # We don't hide Scrcpy window because it is an interactive GUI window!
            self.active_proc = subprocess.Popen(cmd)
            return True, f"Launched Screen Mirror ({preset})"
        except Exception as e:
            return False, f"Failed to start scrcpy: {e}"

    def is_running(self) -> bool:
        return self.active_proc is not None and self.active_proc.poll() is None

    def stop(self):
        if self.is_running() and self.active_proc:
            try:
                self.active_proc.terminate()
            except Exception:
                pass
            self.active_proc = None
