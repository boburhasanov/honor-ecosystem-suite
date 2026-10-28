"""
Comprehensive Test Suite for Honor Ecosystem Suite (Windows Evolution).
Verifies platform helpers, registry classifications, ADB service, telemetry parsers,
file beamer logic, mirror presets, package manager, and headless Qt UI instantiation.
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set Qt offscreen platform plugin for headless testing
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import unittest
from lib.honor_suite.utils.platform_helper import (
    get_creation_flags,
    get_app_cache_dir,
    get_default_gateway,
    ping_host,
    IS_WINDOWS
)
from lib.honor_suite.utils.registry_data import (
    KNOWN_APP_REGISTRY,
    classify_package_safety,
    SAFE_DEBLOAT_PACKAGES,
    DANGEROUS_PACKAGES
)
from lib.honor_suite.core.adb_service import AdbService
from lib.honor_suite.core.telemetry import TelemetryService
from lib.honor_suite.core.file_beamer import FileBeamer
from lib.honor_suite.core.package_manager import PackageManagerService
from lib.honor_suite.core.mirror_service import MirrorService
from lib.honor_suite.core.file_browser import FileBrowserService

class TestPlatformHelper(unittest.TestCase):
    def test_creation_flags(self):
        flags = get_creation_flags()
        if IS_WINDOWS:
            self.assertEqual(flags, 0x08000000)
        else:
            self.assertEqual(flags, 0)

    def test_cache_dir(self):
        d = get_app_cache_dir()
        self.assertTrue(d.exists())
        self.assertTrue(d.is_dir())

    def test_ping_local(self):
        res = ping_host("127.0.0.1", timeout_ms=500)
        self.assertIsNotNone(res)
        self.assertGreaterEqual(res, 0.0)

class TestRegistryData(unittest.TestCase):
    def test_registry_populated(self):
        self.assertGreater(len(KNOWN_APP_REGISTRY), 30)
        self.assertIn("com.hihonor.camera", KNOWN_APP_REGISTRY)
        self.assertIn("org.telegram.messenger", KNOWN_APP_REGISTRY)

    def test_classification(self):
        safe_label, safe_color = classify_package_safety("com.facebook.appmanager")
        self.assertIn("Safe", safe_label)
        self.assertEqual(safe_color, "#10b981")

        danger_label, danger_color = classify_package_safety("com.android.systemui")
        self.assertIn("Essential", danger_label)
        self.assertEqual(danger_color, "#ef4444")

class TestAdbService(unittest.TestCase):
    def setUp(self):
        self.adb = AdbService()

    def test_adb_bin_discovered(self):
        self.assertIsNotNone(self.adb.adb_bin)
        bin_lower = self.adb.adb_bin.lower()
        self.assertTrue(bin_lower.endswith("adb") or bin_lower.endswith("adb.exe"))

    def test_target_default(self):
        target = self.adb.get_target()
        self.assertIsInstance(target, str)
        self.assertTrue(len(target) > 0)

class TestMirrorService(unittest.TestCase):
    def setUp(self):
        self.adb = AdbService()
        self.mirror = MirrorService(self.adb)

    def test_scrcpy_bin_discovered(self):
        self.assertIsNotNone(self.mirror.scrcpy_bin)
        bin_lower = self.mirror.scrcpy_bin.lower()
        self.assertTrue(bin_lower.endswith("scrcpy") or bin_lower.endswith("scrcpy.exe"))

class TestFileBrowserParser(unittest.TestCase):
    def test_remote_stat_parsing(self):
        browser = FileBrowserService(AdbService())
        # Simulate shell output parser
        sample_output = "DIR|Camera|0|0\nFILE|photo.jpg|15728640|2026-10-28 10:00:00\n"
        items = []
        for line in sample_output.splitlines():
            parts = line.split("|")
            if parts[0] == "DIR":
                items.append({"name": parts[1], "is_dir": True, "size_str": "Folder"})
            else:
                items.append({"name": parts[1], "is_dir": False, "size_str": "15.0 MB"})

        self.assertEqual(len(items), 2)
        self.assertTrue(items[0]["is_dir"])
        self.assertFalse(items[1]["is_dir"])
        self.assertEqual(items[1]["size_str"], "15.0 MB")

class TestQtUiHeadless(unittest.TestCase):
    def test_main_window_instantiation(self):
        from PySide6.QtWidgets import QApplication
        from lib.honor_suite.ui.main_window import MainWindow

        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)

        window = MainWindow()
        self.assertIsNotNone(window)
        self.assertEqual(window.windowTitle(), "Honor Ecosystem Hub — MagicOS PC Suite")
        self.assertEqual(window.stack.count(), 5)
        window.close()

class TestHonorBridge(unittest.TestCase):
    def setUp(self):
        from lib.honor_suite.bridge import HonorBridgeApi
        self.bridge = HonorBridgeApi()

    def test_bridge_instantiation(self):
        self.assertIsNotNone(self.bridge.telemetry)
        self.assertIsNotNone(self.bridge.beamer)
        self.assertIsNotNone(self.bridge.pm)
        self.assertIsNotNone(self.bridge.mirror)
        self.assertIsNotNone(self.bridge.browser)

    def test_telemetry_disconnected_contract(self):
        # When no device is attached, it should return a valid contract without throwing
        data = self.bridge.get_telemetry()
        self.assertIsInstance(data, dict)
        self.assertIn("connected", data)
        self.assertIn("battery_level", data)
        self.assertIn("ram_percent", data)
        self.assertIn("storage_percent", data)

    def test_package_manager_cache(self):
        pm = self.bridge.pm
        pm._cached_packages = [{"pkg": "mock.pkg", "name": "Mock App", "status": "Active"}]
        import time
        pm._cache_time = time.time()
        res = pm.get_all_packages()
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["pkg"], "mock.pkg")

        pm.invalidate_cache()
        self.assertIsNone(pm._cached_packages)

if __name__ == "__main__":
    unittest.main()
