"""
Multi-Screen Collaboration & Screen Mirror View for Honor Suite
Provides resolution presets (1440p/1080p/720p), audio routing,
and battery-saver features (turn phone screen off while mirroring).
"""

import subprocess
import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from typing import Callable

class MirrorView(Gtk.Box):
    def __init__(self, engine, show_msg: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.engine = engine
        self.show_msg = show_msg
        self.set_border_width(16)

        self._build_ui()

    def _build_ui(self):
        # 1. Preset Card
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.get_style_context().add_class("card")

        title = Gtk.Label(label="🖥️ Multi-Screen Collaboration (Scrcpy v4.1)", xalign=0)
        title.get_style_context().add_class("card-title")
        card.pack_start(title, False, False, 0)

        desc = Gtk.Label(
            label="Control your Honor 400 Pro completely from your Linux Mint laptop. Type with your keyboard, use your mouse/trackpad gestures, drag & drop files onto the window, and hear phone audio through laptop speakers.",
            xalign=0
        )
        desc.get_style_context().add_class("card-desc")
        desc.set_line_wrap(True)
        card.pack_start(desc, False, False, 0)

        # Quality presets
        q_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        q_lbl = Gtk.Label(label="Quality Preset:", xalign=0)
        q_lbl.get_style_context().add_class("text-main")
        q_box.pack_start(q_lbl, False, False, 0)

        self.preset_combo = Gtk.ComboBoxText()
        self.preset_combo.append("1440p", "🌟 Ultra 1440p (60 FPS • 16 Mbps • Crystal Clear)")
        self.preset_combo.append("1080p", "⚡ Balanced 1080p (60 FPS • 10 Mbps • Low Latency)")
        self.preset_combo.append("720p",  "🍃 Eco 720p (30 FPS • 4 Mbps • Battery Saver)")
        self.preset_combo.set_active_id("1440p")
        q_box.pack_start(self.preset_combo, True, True, 0)
        card.pack_start(q_box, False, False, 0)

        # Toggles
        self.chk_screen_off = Gtk.CheckButton.new_with_label("Turn off phone display while mirroring (saves phone battery & heat)")
        self.chk_screen_off.set_active(False)
        card.pack_start(self.chk_screen_off, False, False, 0)

        self.chk_stay_awake = Gtk.CheckButton.new_with_label("Keep phone awake while mirroring")
        self.chk_stay_awake.set_active(True)
        card.pack_start(self.chk_stay_awake, False, False, 0)

        self.chk_audio = Gtk.CheckButton.new_with_label("Forward phone audio to laptop speakers")
        self.chk_audio.set_active(True)
        card.pack_start(self.chk_audio, False, False, 0)

        # Launch Button
        launch_btn = Gtk.Button.new_with_label("🚀 Launch Wireless Screen Mirror")
        launch_btn.get_style_context().add_class("btn-primary")
        launch_btn.connect("clicked", self.on_launch_mirror)
        card.pack_start(launch_btn, False, False, 6)

        self.pack_start(card, False, False, 0)

    def on_launch_mirror(self, widget):
        self.show_msg("Checking device connection...")
        def worker():
            if not self.engine.is_connected():
                self.engine.ensure_connected(max_retries=2)

            if not self.engine.is_connected():
                def err():
                    self.show_msg("⚠️ Device Offline! Please turn on 'Wireless Debugging' in Developer Options on your phone.")
                GLib.idle_add(err)
                return

            target = self.engine.get_target()
            preset = self.preset_combo.get_active_id() or "1440p"

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

            cmd = [
                "/usr/local/bin/scrcpy",
                "-s", target,
                f"--window-title=Honor 400 Pro ({preset} 60 FPS)",
                "--video-codec=h264",
                "-m", max_size,
                "-b", bit_rate,
                f"--max-fps={max_fps}"
            ]

            if self.chk_stay_awake.get_active():
                cmd.append("--stay-awake")
            if self.chk_screen_off.get_active():
                cmd.append("--turn-screen-off")
            if not self.chk_audio.get_active():
                cmd.append("--no-audio")

            def launch():
                self.show_msg(f"Launching Wireless Mirror at {preset}...")
                subprocess.Popen(cmd)
            GLib.idle_add(launch)

        threading.Thread(target=worker, daemon=True).start()
