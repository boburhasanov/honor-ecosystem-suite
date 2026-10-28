#!/usr/bin/env python3
"""
Automated PyInstaller Build Script for Honor Ecosystem Suite (Windows Edition)
Generates a standalone commercial-grade Windows binary with custom 3D flagship icon,
bundled web motion UI assets, and zero external runtime dependencies.
"""

import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def build():
    print("=" * 60)
    print("  Building Honor Ecosystem Hub Standalone Windows Binary")
    print("=" * 60)

    icon_path = BASE_DIR / "desktop" / "honor-hub.ico"
    entry_point = BASE_DIR / "honor-hub-motion.py"
    web_dir = BASE_DIR / "web"
    desktop_dir = BASE_DIR / "desktop"
    assets_dir = BASE_DIR / "assets"

    # Verify essentials
    if not icon_path.exists():
        print(f"[!] Warning: Icon not found at {icon_path}")
    if not entry_point.exists():
        print(f"[ERROR] Entry point {entry_point} not found!")
        sys.exit(1)

    # PyInstaller arguments
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",  # No console window
        "--name", "HonorEcosystemHub",
        "--icon", str(icon_path),
        "--add-data", f"{web_dir};web",
        "--add-data", f"{desktop_dir};desktop",
        "--add-data", f"{assets_dir};assets",
        "--hidden-import", "webview",
        "--hidden-import", "webview.platforms.winforms",
        "--hidden-import", "clr",
        str(entry_point)
    ]

    print(f"[*] Executing PyInstaller command...")
    res = subprocess.run(cmd, cwd=str(BASE_DIR))
    if res.returncode == 0:
        print("\n" + "=" * 60)
        print(" [OK] Build completed successfully!")
        print(f" Output directory: {BASE_DIR / 'dist' / 'HonorEcosystemHub'}")
        print("=" * 60)
    else:
        print(f"[!] PyInstaller failed with exit code {res.returncode}")
        sys.exit(res.returncode)

if __name__ == "__main__":
    build()
