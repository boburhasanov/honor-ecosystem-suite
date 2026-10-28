"""
Bi-directional Bridge API for Honor Ecosystem Suite.
Connects the high-performance async Python backend to the 120 FPS GPU-accelerated Web UI.
Features dedicated background daemon monitoring to prevent any GUI freezing or '(Не отвечает)'.
"""

import os
import sys
import json
import time
import threading
from typing import Dict, Any, List, Optional
import webview

from lib.honor_suite.core.adb_service import AdbService
from lib.honor_suite.core.telemetry import TelemetryService
from lib.honor_suite.core.file_beamer import FileBeamer
from lib.honor_suite.core.package_manager import PackageManagerService
from lib.honor_suite.core.mirror_service import MirrorService
from lib.honor_suite.core.file_browser import FileBrowserService

class HonorBridgeApi:
    def __init__(self, window_ref=None):
        self.window = window_ref
        self.adb = AdbService()
        self.telemetry = TelemetryService(self.adb)
        self.beamer = FileBeamer(self.adb)
        self.pm = PackageManagerService(self.adb)
        self.mirror = MirrorService(self.adb)
        self.browser = FileBrowserService(self.adb)
        self._beam_thread: Optional[threading.Thread] = None

        # Thread-safe telemetry cache (guarantees 0ms response to JS)
        self._latest_telemetry = self.telemetry.get_overview()
        self._stop_monitor = False
        self._monitor_thread = threading.Thread(target=self._background_monitor_loop, daemon=True)
        self._monitor_thread.start()

    def set_window(self, window):
        self.window = window

    def emit_event(self, event_name: str, payload: Any):
        """Dispatches an asynchronous event into the JavaScript runtime."""
        if not self.window:
            return
        try:
            json_str = json.dumps(payload)
            script = f"if (window.dispatchEvent) {{ window.dispatchEvent(new CustomEvent('{event_name}', {{ detail: {json_str} }})); }}"
            self.window.evaluate_js(script)
        except Exception:
            pass

    def _background_monitor_loop(self):
        """Continuously polls hardware status in background without blocking GUI."""
        counter = 0
        while not self._stop_monitor:
            try:
                # Every ~15 seconds, try auto-connecting to hotspot gateway if offline
                if counter % 5 == 0 and not self.adb.is_connected():
                    self.adb.try_auto_connect_gateway()

                data = self.telemetry.get_overview()
                self._latest_telemetry = data
                self.emit_event("telemetry_update", data)
            except Exception:
                pass
            counter += 1
            time.sleep(3.0)

    # 1. Telemetry & Connection API
    def get_telemetry(self) -> Dict[str, Any]:
        """Returns the latest hardware telemetry instantly in 0ms."""
        return self._latest_telemetry or self.telemetry.get_overview()

    def enable_wireless_mode(self) -> Dict[str, Any]:
        """Triggers 1-Click USB-to-Wireless Magic Handshake (tcpip 5555 + auto-connect)."""
        ok, msg, target = self.adb.enable_wireless_mode()
        # Immediately refresh cached telemetry
        self._latest_telemetry = self.telemetry.get_overview()
        return {"success": ok, "message": msg, "target": target}

    # 2. Fast Beam API
    def start_beam(self, local_path: str, remote_dir: str = "/storage/emulated/0/DCIM/Camera", auto_apple: bool = True) -> Dict[str, Any]:
        if not local_path:
            return {"success": False, "message": "No file or folder selected."}

        def worker():
            def on_progress(data: Dict):
                self.emit_event("beam_progress", data)

            success, msg = self.beamer.beam(
                local_path=local_path,
                remote_dir=remote_dir,
                progress_cb=on_progress,
                auto_convert_apple=auto_apple
            )
            self.emit_event("beam_finished", {"success": success, "message": msg})

        self._beam_thread = threading.Thread(target=worker, daemon=True)
        self._beam_thread.start()
        return {"success": True, "message": "Beam started"}

    def cancel_beam(self) -> Dict[str, Any]:
        self.beamer.cancel()
        return {"success": True, "message": "Beam cancelled"}

    # 3. Debloater API
    def get_all_packages(self, force_refresh: bool = False) -> List[Dict]:
        return self.pm.get_all_packages(force_refresh=force_refresh)

    def uninstall_packages(self, pkg_list: List[str]) -> Dict[str, Any]:
        success_count = 0
        total = len(pkg_list)
        for pkg in pkg_list:
            ok, _ = self.pm.uninstall_package(pkg)
            if ok:
                success_count += 1
        return {"success": True, "processed": success_count, "total": total}

    def restore_packages(self, pkg_list: List[str]) -> Dict[str, Any]:
        success_count = 0
        total = len(pkg_list)
        for pkg in pkg_list:
            ok, _ = self.pm.restore_package(pkg)
            if ok:
                success_count += 1
        return {"success": True, "processed": success_count, "total": total}

    # 4. Mirroring API
    def launch_mirror(self, preset: str = "1440p", screen_off: bool = False, awake: bool = True, audio: bool = True) -> Dict[str, Any]:
        ok, msg = self.mirror.launch(
            preset=preset,
            turn_screen_off=screen_off,
            stay_awake=awake,
            forward_audio=audio
        )
        return {"success": ok, "message": msg}

    def stop_mirror(self) -> Dict[str, Any]:
        self.mirror.stop()
        return {"success": True, "message": "Mirror stopped"}

    # 5. Remote File Explorer API
    def list_directory(self, remote_path: str = "/storage/emulated/0") -> List[Dict]:
        return self.browser.list_directory(remote_path)

    def pull_file(self, remote_path: str, local_dir: str) -> Dict[str, Any]:
        ok, msg = self.browser.pull_file(remote_path, local_dir)
        return {"success": ok, "message": msg}

    def push_file(self, local_path: str, remote_dir: str) -> Dict[str, Any]:
        ok, msg = self.browser.push_file(local_path, remote_dir)
        return {"success": ok, "message": msg}

    def delete_item(self, remote_path: str) -> Dict[str, Any]:
        ok, msg = self.browser.delete_item(remote_path)
        return {"success": ok, "message": msg}

    # 6. Native Dialog Helpers
    def select_file(self) -> str:
        if not self.window:
            return ""
        result = self.window.create_file_dialog(webview.OPEN_DIALOG)
        if result and len(result) > 0:
            return result[0]
        return ""

    def select_folder(self) -> str:
        if not self.window:
            return ""
        result = self.window.create_file_dialog(webview.FOLDER_DIALOG)
        if result and len(result) > 0:
            return result[0]
        return ""
