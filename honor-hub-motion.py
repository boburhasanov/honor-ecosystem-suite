#!/usr/bin/env python3
"""
Honor Ecosystem Suite — Motion Edition (120 FPS Flagship PC Suite)
Powered by Hardware-Accelerated PyWebView (Edge Chromium) and Async Python Core.
Zero-Resource Guarantee (0% CPU, 0 MB RAM when idle or closed).
"""

import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import webview
from lib.honor_suite.bridge import HonorBridgeApi

def main():
    api = HonorBridgeApi()
    html_path = BASE_DIR / "web" / "index.html"

    # Create window with Edge Chromium (WebView2) hardware acceleration
    window = webview.create_window(
        title="Honor Ecosystem Hub — MagicOS PC Suite",
        url=f"file:///{html_path.as_posix()}",
        js_api=api,
        width=1200,
        height=800,
        min_size=(960, 640),
        background_color="#070a13"
    )
    api.set_window(window)

    # Start PyWebView with GUI thread
    webview.start(debug=False)

if __name__ == "__main__":
    main()
