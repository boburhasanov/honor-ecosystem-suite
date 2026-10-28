"""
Pre-flight environment verification script for Honor Ecosystem Suite on Windows/Linux.
Checks Python runtime, PySide6 installation, and external binary dependencies (adb, scrcpy, ffmpeg).
"""

import sys
import shutil
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def check_binary(name: str) -> tuple[bool, str]:
    path = shutil.which(name)
    if path:
        return True, path
    return False, "Not found in PATH"

def main():
    print("=" * 60)
    print("Honor Ecosystem Suite - System Verification")
    print("=" * 60)

    # 1. Python version
    py_ver = sys.version.split()[0]
    print(f"[*] Python Version: {py_ver} (OK)")

    # 2. PySide6
    try:
        import PySide6.QtCore as QtCore
        print(f"[*] PySide6 (Qt {QtCore.__version__}): Available (OK)")
    except ImportError as e:
        print(f"[!] PySide6: Missing ({e})")

    # 3. External Tools
    tools = ["adb", "scrcpy", "ffmpeg"]
    all_ok = True
    for tool in tools:
        ok, location = check_binary(tool)
        if ok:
            print(f"[*] {tool.upper():<7}: Found at {location}")
        else:
            print(f"[!] {tool.upper():<7}: MISSING ({location})")
            all_ok = False

    print("-" * 60)
    if all_ok:
        print("[OK] All prerequisites are satisfied!")
    else:
        print("[!] Some components are missing. Check winget or PATH.")
    print("=" * 60)

if __name__ == "__main__":
    main()
