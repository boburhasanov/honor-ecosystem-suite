"""
Platform Helper Utility for Honor Ecosystem Suite
Ensures smooth cross-platform execution between Windows and Linux.
Handles non-flashing sub-processes, gateway resolution, pinging, and cache paths.
"""

import os
import sys
import shutil
import subprocess
import re
from pathlib import Path
from typing import Optional, List, Dict

IS_WINDOWS = sys.platform == "win32"
IS_LINUX = sys.platform.startswith("linux")

def get_creation_flags() -> int:
    """Returns CREATE_NO_WINDOW flag on Windows to prevent black console popup windows."""
    if IS_WINDOWS:
        return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    return 0

def find_executable(name: str) -> Optional[str]:
    """Finds binary in PATH or returns None."""
    return shutil.which(name)

def get_app_cache_dir() -> Path:
    """Returns platform-appropriate cache directory."""
    if IS_WINDOWS:
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        p = Path(base) / "HonorEcosystemSuite" / "cache"
    else:
        p = Path(os.path.expanduser("~/.cache/honor-suite"))
    p.mkdir(parents=True, exist_ok=True)
    return p

def get_default_gateway() -> Optional[str]:
    """
    Discovers the default gateway IP (typically smartphone Wi-Fi hotspot IP).
    Deterministic and handles both Windows and Linux without hanging.
    """
    if IS_WINDOWS:
        try:
            # Query default route via netsh / powershell or route print
            cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command",
                   "(Get-NetRoute -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue | Select-Object -First 1).NextHop"]
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3,
                creationflags=get_creation_flags()
            )
            gw = res.stdout.strip()
            if gw and gw != "0.0.0.0" and re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", gw):
                return gw
        except Exception:
            pass

        # Fallback to route print
        try:
            res = subprocess.run(
                ["route", "print", "0.0.0.0"],
                capture_output=True,
                text=True,
                timeout=2,
                creationflags=get_creation_flags()
            )
            for line in res.stdout.splitlines():
                parts = line.strip().split()
                if len(parts) >= 5 and parts[0] == "0.0.0.0" and parts[1] == "0.0.0.0":
                    candidate = parts[2]
                    if candidate != "0.0.0.0" and re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", candidate):
                        return candidate
        except Exception:
            pass

    elif IS_LINUX:
        try:
            res = subprocess.run(
                "ip route show default | awk '{print $3}'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=2
            )
            gw = res.stdout.strip()
            if gw and re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", gw):
                return gw
        except Exception:
            pass

    return None

def ping_host(host: str, timeout_ms: int = 1000) -> Optional[float]:
    """
    Pings host once and returns response time in milliseconds.
    """
    if not host:
        return None

    if IS_WINDOWS:
        cmd = ["ping", "-n", "1", "-w", str(timeout_ms), host]
    else:
        timeout_sec = max(1, timeout_ms // 1000)
        cmd = ["ping", "-c", "1", "-W", str(timeout_sec), host]

    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=max(2, (timeout_ms / 1000) + 1),
            creationflags=get_creation_flags()
        )
        if res.returncode == 0:
            # Parse time=<number>ms or time=<number> ms
            m = re.search(r"time[<=]([\d\.]+)\s*ms", res.stdout, re.IGNORECASE)
            if m:
                return float(m.group(1))
            # Russian/localized Windows: время=<number>мс
            m_ru = re.search(r"[=<]([\d\.]+)\s*(?:мс|ms)", res.stdout, re.IGNORECASE)
            if m_ru:
                return float(m_ru.group(1))
            return 1.0
    except Exception:
        pass
    return None
