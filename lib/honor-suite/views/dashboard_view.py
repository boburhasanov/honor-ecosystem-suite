"""
Dashboard View for Honor Suite
Displays real-time battery status, storage breakdown, Wi-Fi 6 health, and quick actions.
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from typing import Callable

class DashboardView(Gtk.Box):
    def __init__(self, engine, on_switch_tab: Callable[[str], None], show_msg: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.engine = engine
        self.on_switch_tab = on_switch_tab
        self.show_msg = show_msg
        self.set_border_width(16)

        self._build_ui()

    def _build_ui(self):
        # 1. Main Device Hero Card
        hero_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        hero_card.get_style_context().add_class("card")

        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        phone_icon = Gtk.Image.new_from_icon_name("phone", Gtk.IconSize.DIALOG)
        top_row.pack_start(phone_icon, False, False, 0)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.model_lbl = Gtk.Label(label="HONOR 400 Pro (Android 16)", xalign=0)
        self.model_lbl.get_style_context().add_class("card-title")
        info_box.pack_start(self.model_lbl, False, False, 0)

        self.net_lbl = Gtk.Label(label="Resolving wireless link...", xalign=0)
        self.net_lbl.get_style_context().add_class("card-desc")
        info_box.pack_start(self.net_lbl, False, False, 0)
        top_row.pack_start(info_box, True, True, 0)

        self.status_badge = Gtk.Label(label="Checking...")
        self.status_badge.get_style_context().add_class("badge-cyan")
        top_row.pack_end(self.status_badge, False, False, 0)
        hero_card.pack_start(top_row, False, False, 0)

        # Metrics row: Battery Status, RAM Usage, Internal Storage
        metrics_grid = Gtk.Grid()
        metrics_grid.set_column_spacing(14)
        metrics_grid.set_row_spacing(10)
        metrics_grid.set_column_homogeneous(True)

        # 1. Battery Box
        bat_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        bat_title = Gtk.Label(label="BATTERY STATUS", xalign=0)
        bat_title.get_style_context().add_class("metric-label")
        bat_box.pack_start(bat_title, False, False, 0)

        self.bat_val_lbl = Gtk.Label(label="-- %", xalign=0)
        self.bat_val_lbl.get_style_context().add_class("metric-value")
        bat_box.pack_start(self.bat_val_lbl, False, False, 0)

        self.bat_bar = Gtk.ProgressBar()
        self.bat_bar.set_fraction(0.0)
        bat_box.pack_start(self.bat_bar, False, False, 4)

        self.bat_sub_lbl = Gtk.Label(label="-- °C • Li-ion", xalign=0)
        self.bat_sub_lbl.get_style_context().add_class("card-desc")
        bat_box.pack_start(self.bat_sub_lbl, False, False, 0)
        metrics_grid.attach(bat_box, 0, 0, 1, 1)

        # 2. RAM Usage Box
        ram_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        ram_title = Gtk.Label(label="RAM USAGE", xalign=0)
        ram_title.get_style_context().add_class("metric-label")
        ram_box.pack_start(ram_title, False, False, 0)

        self.ram_val_lbl = Gtk.Label(label="-- GB / -- GB", xalign=0)
        self.ram_val_lbl.get_style_context().add_class("metric-value")
        ram_box.pack_start(self.ram_val_lbl, False, False, 0)

        self.ram_bar = Gtk.ProgressBar()
        self.ram_bar.set_fraction(0.0)
        ram_box.pack_start(self.ram_bar, False, False, 4)

        self.ram_sub_lbl = Gtk.Label(label="-- GB Available", xalign=0)
        self.ram_sub_lbl.get_style_context().add_class("card-desc")
        ram_box.pack_start(self.ram_sub_lbl, False, False, 0)
        metrics_grid.attach(ram_box, 1, 0, 1, 1)

        # 3. Storage Box
        stor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        stor_title = Gtk.Label(label="INTERNAL STORAGE", xalign=0)
        stor_title.get_style_context().add_class("metric-label")
        stor_box.pack_start(stor_title, False, False, 0)

        self.stor_val_lbl = Gtk.Label(label="-- GB / -- GB", xalign=0)
        self.stor_val_lbl.get_style_context().add_class("metric-value")
        stor_box.pack_start(self.stor_val_lbl, False, False, 0)

        self.stor_bar = Gtk.ProgressBar()
        self.stor_bar.set_fraction(0.0)
        stor_box.pack_start(self.stor_bar, False, False, 4)

        self.stor_sub_lbl = Gtk.Label(label="-- GB Free", xalign=0)
        self.stor_sub_lbl.get_style_context().add_class("card-desc")
        stor_box.pack_start(self.stor_sub_lbl, False, False, 0)
        metrics_grid.attach(stor_box, 2, 0, 1, 1)

        hero_card.pack_start(metrics_grid, False, False, 0)
        self.pack_start(hero_card, False, False, 0)

        # 2. Quick Actions Card
        qa_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        qa_card.get_style_context().add_class("card")

        qa_title = Gtk.Label(label="⚡ Ecosystem Quick Actions", xalign=0)
        qa_title.get_style_context().add_class("card-title")
        qa_card.pack_start(qa_title, False, False, 0)

        btn_grid = Gtk.Grid()
        btn_grid.set_column_spacing(10)
        btn_grid.set_row_spacing(10)
        btn_grid.set_column_homogeneous(True)

        mirror_btn = Gtk.Button.new_with_label("🖥️ Wireless Screen Mirror")
        mirror_btn.get_style_context().add_class("btn-primary")
        mirror_btn.connect("clicked", lambda b: self.on_switch_tab("mirror"))
        btn_grid.attach(mirror_btn, 0, 0, 1, 1)

        files_btn = Gtk.Button.new_with_label("📁 Browse Phone Storage")
        files_btn.get_style_context().add_class("btn-secondary")
        files_btn.connect("clicked", lambda b: self.on_switch_tab("files"))
        btn_grid.attach(files_btn, 1, 0, 1, 1)

        beam_btn = Gtk.Button.new_with_label("📤 Beam Files / Folders (70 MB/s)")
        beam_btn.get_style_context().add_class("btn-success")
        beam_btn.connect("clicked", lambda b: self.on_switch_tab("transfer"))
        btn_grid.attach(beam_btn, 0, 1, 1, 1)

        debloat_btn = Gtk.Button.new_with_label("🧹 Wireless Debloater")
        debloat_btn.get_style_context().add_class("btn-secondary")
        debloat_btn.connect("clicked", lambda b: self.on_switch_tab("debloat"))
        btn_grid.attach(debloat_btn, 1, 1, 1, 1)

        qa_card.pack_start(btn_grid, False, False, 0)
        self.pack_start(qa_card, False, False, 0)

    def refresh(self):
        def worker():
            overview = self.engine.get_device_overview()
            def update_ui():
                if overview["connected"]:
                    self.status_badge.set_text("Wireless Active")
                    self.status_badge.get_style_context().remove_class("badge-amber")
                    self.status_badge.get_style_context().add_class("badge-active")
                    self.net_lbl.set_text(f"Connected to {overview['target']} • Ping: {overview['ping_ms']} ms")

                    # 1. Battery Status
                    lvl = overview["battery_level"]
                    st = overview["battery_status"]
                    temp = overview.get("battery_temp_c", 0.0)
                    soh = overview.get("battery_soh", 100)

                    self.bat_val_lbl.set_text(f"{lvl}% ({st})")
                    self.bat_bar.set_fraction(lvl / 100.0)

                    if st == "Charging":
                        self.bat_sub_lbl.set_text(f"⚡ Charging • {temp:.1f} °C • Health: {soh}%")
                    else:
                        self.bat_sub_lbl.set_text(f"{temp:.1f} °C • Li-ion 6000 mAh • Health: {soh}%")

                    # 2. RAM Usage
                    ram_used = overview.get("ram_used_gb", 0.0)
                    ram_tot = overview.get("ram_total_gb", 0.0)
                    ram_free = overview.get("ram_free_gb", 0.0)
                    ram_pct = overview.get("ram_percent", 0)
                    self.ram_val_lbl.set_text(f"{ram_used} GB / {ram_tot} GB ({ram_pct}%)")
                    self.ram_bar.set_fraction(ram_pct / 100.0)
                    self.ram_sub_lbl.set_text(f"{ram_free} GB Available • Fast LPDDR5X")

                    # 3. Storage
                    used = overview["storage_used_gb"]
                    tot = overview["storage_total_gb"]
                    free = overview.get("storage_free_gb", 0.0)
                    pct = overview["storage_percent"]
                    self.stor_val_lbl.set_text(f"{used} GB / {tot} GB ({pct}%)")
                    self.stor_bar.set_fraction(pct / 100.0)
                    self.stor_sub_lbl.set_text(f"{free} GB Free (Cleaned)")
                else:
                    self.status_badge.set_text("Reconnecting...")
                    self.status_badge.get_style_context().remove_class("badge-active")
                    self.status_badge.get_style_context().add_class("badge-amber")
                    self.net_lbl.set_text(f"Attempting to bind to {overview['target']}...")
            GLib.idle_add(update_ui)

        import threading
        threading.Thread(target=worker, daemon=True).start()
