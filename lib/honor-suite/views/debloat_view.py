"""
Advanced Wireless App Manager & Debloater (Xiaomi Flash Tool / UAD Style)
Provides real-time inspection, search, multi-selection, debloating,
and instant restoration for all system, user, uninstalled, and disabled apps.
"""

import os
import threading
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GdkPixbuf, GLib
from typing import Callable, List, Dict, Set, Optional

KNOWN_BLOATWARE = {
    "com.yandex.browser",
    "com.yandex.searchapp",
    "com.yandex.preinstallsatellite",
    "com.aura.oobe.honor",
    "android.autoinstalls.config.honor.device",
    "com.hihonor.autoinstallapkfrommcc",
    "com.hihonor.gamecenter",
    "com.hihonor.gameassistant",
    "com.hihonor.game.kitserver",
    "com.hihonor.magazine",
    "com.hihonor.tips",
    "com.hihonor.browserhomepage",
    "com.hihonor.hnvideoplayer",
    "com.hihonor.hnmusicplayer",
    "com.facebook.system",
    "com.facebook.appmanager",
    "com.facebook.services",
    "com.google.android.apps.bard",
    "com.google.android.videos",
    "com.google.android.apps.tachyon",
}

class DebloatView(Gtk.Box):
    def __init__(self, engine, show_msg: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.engine = engine
        self.show_msg = show_msg
        self.set_border_width(16)

        self.current_filter = "ALL"  # ALL, SYSTEM, USER, RECYCLED, DISABLED
        self.search_query = ""
        self.all_packages_cache: List[Dict] = []
        self.selected_pkgs: Set[str] = set()
        self.icon_cache: Dict[str, Optional[GdkPixbuf.Pixbuf]] = {}

        self._build_ui()

    def get_icon_pixbuf(self, icon_name: str) -> Optional[GdkPixbuf.Pixbuf]:
        if icon_name in self.icon_cache:
            return self.icon_cache[icon_name]

        script_dir = os.path.dirname(os.path.realpath(__file__))
        candidates = [
            os.path.join(script_dir, "..", "assets", "icons", icon_name),
            os.path.join("/usr/local/lib/honor-suite", "assets", "icons", icon_name),
            os.path.join(script_dir, "..", "..", "assets", "icons", icon_name)
        ]
        for p in candidates:
            if os.path.exists(p):
                try:
                    pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(p, 22, 22, True)
                    self.icon_cache[icon_name] = pb
                    return pb
                except Exception:
                    pass

        theme = Gtk.IconTheme.get_default()
        for name in [icon_name, "package-x-generic", "application-x-executable", "preferences-system"]:
            try:
                pb = theme.load_icon(name, 22, Gtk.IconLookupFlags.GENERIC_FALLBACK)
                self.icon_cache[icon_name] = pb
                return pb
            except Exception:
                pass

        return None

    def _build_ui(self):
        # 1. Top Control Card (Xiaomi Flash Tool Style)
        ctrl_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        ctrl_card.get_style_context().add_class("card")

        title = Gtk.Label(label="🧹 Advanced Wireless App Manager (Xiaomi Flash Tool Style)", xalign=0)
        title.get_style_context().add_class("card-title")
        ctrl_card.pack_start(title, False, False, 0)

        desc = Gtk.Label(
            label="Real-time control over all system bloatware, user-installed apps, and uninstalled packages. Uninstall any bloatware or restore deleted apps in one click with zero risk.",
            xalign=0
        )
        desc.get_style_context().add_class("card-desc")
        desc.set_line_wrap(True)
        ctrl_card.pack_start(desc, False, False, 0)

        # Category Filter Tabs
        tab_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.tab_btns = {}

        tabs = [
            ("ALL", "📱 All Apps"),
            ("SYSTEM", "⚙️ System"),
            ("USER", "👤 User Installed"),
            ("RECYCLED", "🗑️ Recycled (Restore)"),
            ("DISABLED", "⏸️ Disabled"),
        ]

        for tab_id, tab_label in tabs:
            btn = Gtk.Button.new_with_label(tab_label)
            btn.get_style_context().add_class("tab-btn")
            if tab_id == "ALL":
                btn.get_style_context().add_class("btn-primary")
            else:
                btn.get_style_context().add_class("btn-secondary")
            btn.connect("clicked", lambda b, tid=tab_id: self.on_tab_changed(tid))
            tab_box.pack_start(btn, False, False, 0)
            self.tab_btns[tab_id] = btn

        ctrl_card.pack_start(tab_box, False, False, 2)

        # Search Bar + Batch Actions
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("🔍 Search app name or package ID (e.g. yandex, honor, google, chrome)...")
        self.search_entry.get_style_context().add_class("search-input")
        self.search_entry.connect("changed", self.on_search_changed)
        search_box.pack_start(self.search_entry, True, True, 0)

        safe_btn = Gtk.Button.new_with_label("⚡ Select Safe Bloatware")
        safe_btn.get_style_context().add_class("btn-secondary")
        safe_btn.connect("clicked", self.on_select_safe_bloatware)
        search_box.pack_start(safe_btn, False, False, 0)

        sel_all_btn = Gtk.Button.new_with_label("Toggle All")
        sel_all_btn.get_style_context().add_class("btn-secondary")
        sel_all_btn.connect("clicked", self.on_toggle_all)
        search_box.pack_start(sel_all_btn, False, False, 0)

        ctrl_card.pack_start(search_box, False, False, 2)

        # Stats status line
        self.stats_lbl = Gtk.Label(label="Scanning packages in real time...", xalign=0)
        self.stats_lbl.get_style_context().add_class("metric-label")
        ctrl_card.pack_start(self.stats_lbl, False, False, 0)

        self.pack_start(ctrl_card, False, False, 0)

        # 2. Main Package Table Card
        table_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        table_card.get_style_context().add_class("card")

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.set_min_content_height(340)

        # Model: [Selected(bool), Icon(Pixbuf), AppName(str), PackageID(str), Type(str), Status(str)]
        self.store = Gtk.ListStore(bool, GdkPixbuf.Pixbuf, str, str, str, str)
        self.tree = Gtk.TreeView(model=self.store)
        self.tree.get_style_context().add_class("view")

        # Column 0: Checkbox
        toggle_renderer = Gtk.CellRendererToggle()
        toggle_renderer.connect("toggled", self.on_cell_toggled)
        col_chk = Gtk.TreeViewColumn("", toggle_renderer, active=0)
        col_chk.set_min_width(40)
        self.tree.append_column(col_chk)

        # Column 1: App Name with Vector/Theme Icon
        col_name = Gtk.TreeViewColumn("App Name")
        col_name.set_min_width(220)
        col_name.set_sort_column_id(2)

        icon_renderer = Gtk.CellRendererPixbuf()
        text_renderer = Gtk.CellRendererText()

        col_name.pack_start(icon_renderer, False)
        col_name.pack_start(text_renderer, True)
        col_name.add_attribute(icon_renderer, "pixbuf", 1)
        col_name.add_attribute(text_renderer, "text", 2)
        self.tree.append_column(col_name)

        # Column 2: Package ID
        col_pkg = Gtk.TreeViewColumn("Package Identifier", Gtk.CellRendererText(), text=3)
        col_pkg.set_min_width(260)
        col_pkg.set_sort_column_id(3)
        self.tree.append_column(col_pkg)

        # Column 3: Type (System vs User)
        col_type = Gtk.TreeViewColumn("Category", Gtk.CellRendererText(), text=4)
        col_type.set_min_width(90)
        col_type.set_sort_column_id(4)
        self.tree.append_column(col_type)

        # Column 4: Status (Active, Disabled, Uninstalled)
        col_st = Gtk.TreeViewColumn("Current State", Gtk.CellRendererText(), text=5)
        col_st.set_min_width(120)
        col_st.set_sort_column_id(5)
        self.tree.append_column(col_st)

        scroller.add(self.tree)
        table_card.pack_start(scroller, True, True, 0)

        # Action Toolbar (Bottom)
        act_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.uninstall_btn = Gtk.Button.new_with_label("🗑️ Uninstall Selected")
        self.uninstall_btn.get_style_context().add_class("btn-danger")
        self.uninstall_btn.connect("clicked", self.on_uninstall_selected)
        act_box.pack_start(self.uninstall_btn, True, True, 0)

        self.restore_btn = Gtk.Button.new_with_label("🔄 Reinstall / Restore Selected")
        self.restore_btn.get_style_context().add_class("btn-primary")
        self.restore_btn.connect("clicked", self.on_restore_selected)
        act_box.pack_start(self.restore_btn, True, True, 0)

        self.disable_btn = Gtk.Button.new_with_label("⏸️ Disable Selected")
        self.disable_btn.get_style_context().add_class("btn-secondary")
        self.disable_btn.connect("clicked", self.on_disable_selected)
        act_box.pack_start(self.disable_btn, True, True, 0)

        self.enable_btn = Gtk.Button.new_with_label("▶️ Enable Selected")
        self.enable_btn.get_style_context().add_class("btn-success")
        self.enable_btn.connect("clicked", self.on_enable_selected)
        act_box.pack_start(self.enable_btn, True, True, 0)

        refresh_btn = Gtk.Button.new_with_label("🔄 Refresh")
        refresh_btn.get_style_context().add_class("btn-secondary")
        refresh_btn.connect("clicked", lambda b: self.refresh())
        act_box.pack_start(refresh_btn, False, False, 0)

        table_card.pack_start(act_box, False, False, 4)
        self.pack_start(table_card, True, True, 0)

        self.refresh()

    def on_tab_changed(self, tab_id: str):
        self.current_filter = tab_id
        for tid, btn in self.tab_btns.items():
            ctx = btn.get_style_context()
            ctx.remove_class("btn-primary")
            ctx.remove_class("btn-secondary")
            if tid == tab_id:
                ctx.add_class("btn-primary")
            else:
                ctx.add_class("btn-secondary")
        self._apply_filter()

    def on_search_changed(self, widget):
        self.search_query = self.search_entry.get_text().strip().lower()
        self._apply_filter()

    def on_cell_toggled(self, widget, path):
        it = self.store.get_iter(path)
        cur_val = self.store.get_value(it, 0)
        pkg = self.store.get_value(it, 3)
        new_val = not cur_val
        self.store.set_value(it, 0, new_val)
        if new_val:
            self.selected_pkgs.add(pkg)
        else:
            self.selected_pkgs.discard(pkg)
        self._update_stats_label()

    def on_toggle_all(self, widget):
        it = self.store.get_iter_first()
        any_unselected = False
        while it:
            if not self.store.get_value(it, 0):
                any_unselected = True
                break
            it = self.store.iter_next(it)

        target_state = any_unselected
        it = self.store.get_iter_first()
        while it:
            pkg = self.store.get_value(it, 3)
            self.store.set_value(it, 0, target_state)
            if target_state:
                self.selected_pkgs.add(pkg)
            else:
                self.selected_pkgs.discard(pkg)
            it = self.store.iter_next(it)
        self._update_stats_label()

    def on_select_safe_bloatware(self, widget):
        it = self.store.get_iter_first()
        selected_count = 0
        while it:
            pkg = self.store.get_value(it, 3)
            if pkg in KNOWN_BLOATWARE:
                self.store.set_value(it, 0, True)
                self.selected_pkgs.add(pkg)
                selected_count += 1
            it = self.store.iter_next(it)
        self.show_msg(f"Selected {selected_count} safe bloatware packages!")
        self._update_stats_label()

    def _update_stats_label(self):
        total = len(self.all_packages_cache)
        sys_cnt = sum(1 for p in self.all_packages_cache if p["type"] == "System")
        user_cnt = sum(1 for p in self.all_packages_cache if p["type"] == "User")
        rec_cnt = sum(1 for p in self.all_packages_cache if p["status"] == "Uninstalled")
        dis_cnt = sum(1 for p in self.all_packages_cache if p["status"] == "Disabled")
        sel_cnt = len(self.selected_pkgs)

        self.stats_lbl.set_text(
            f"Total: {total} apps ({sys_cnt} System, {user_cnt} User, {rec_cnt} Recycled, {dis_cnt} Disabled) • {sel_cnt} Selected"
        )

    def _apply_filter(self):
        self.store.clear()
        q = self.search_query

        for item in self.all_packages_cache:
            pkg = item["pkg"]
            name = item["name"]
            pkg_type = item["type"]
            status = item["status"]
            icon_name = item.get("icon", "package-x-generic")

            # Category filter
            if self.current_filter == "SYSTEM" and pkg_type != "System":
                continue
            if self.current_filter == "USER" and pkg_type != "User":
                continue
            if self.current_filter == "RECYCLED" and status != "Uninstalled":
                continue
            if self.current_filter == "DISABLED" and status != "Disabled":
                continue

            # Search query filter
            if q and (q not in pkg.lower() and q not in name.lower()):
                continue

            is_sel = pkg in self.selected_pkgs
            status_display = {
                "Active": "🟢 Active",
                "Disabled": "⏸️ Disabled",
                "Uninstalled": "🗑️ Uninstalled (Recycled)"
            }.get(status, status)

            pixbuf = self.get_icon_pixbuf(icon_name)
            self.store.append([is_sel, pixbuf, name, pkg, pkg_type, status_display])

        self._update_stats_label()

    def refresh(self):
        self.stats_lbl.set_text("Scanning packages in real time over ADB...")
        def worker():
            pkgs = self.engine.get_all_packages()
            def done():
                self.all_packages_cache = pkgs
                self._apply_filter()
            GLib.idle_add(done)
        threading.Thread(target=worker, daemon=True).start()

    def on_uninstall_selected(self, widget):
        if not self.selected_pkgs:
            self.show_msg("Please select at least one package to uninstall.")
            return

        pkgs_to_remove = list(self.selected_pkgs)
        self.show_msg(f"Uninstalling {len(pkgs_to_remove)} package(s)...")

        def worker():
            success = 0
            for pkg in pkgs_to_remove:
                ok, _ = self.engine.uninstall_package(pkg)
                if ok:
                    success += 1
            def done():
                self.show_msg(f"Successfully uninstalled {success}/{len(pkgs_to_remove)} package(s)!")
                self.selected_pkgs.clear()
                self.refresh()
            GLib.idle_add(done)
        threading.Thread(target=worker, daemon=True).start()

    def on_restore_selected(self, widget):
        if not self.selected_pkgs:
            self.show_msg("Please select at least one package to restore.")
            return

        pkgs_to_restore = list(self.selected_pkgs)
        self.show_msg(f"Restoring {len(pkgs_to_restore)} package(s)...")

        def worker():
            success = 0
            for pkg in pkgs_to_restore:
                ok, _ = self.engine.restore_package(pkg)
                if ok:
                    success += 1
            def done():
                self.show_msg(f"Successfully restored {success}/{len(pkgs_to_restore)} package(s)!")
                self.selected_pkgs.clear()
                self.refresh()
            GLib.idle_add(done)
        threading.Thread(target=worker, daemon=True).start()

    def on_disable_selected(self, widget):
        if not self.selected_pkgs:
            self.show_msg("Please select at least one package to disable.")
            return

        pkgs = list(self.selected_pkgs)
        def worker():
            success = 0
            for pkg in pkgs:
                ok, _ = self.engine.disable_package(pkg)
                if ok:
                    success += 1
            def done():
                self.show_msg(f"Disabled {success}/{len(pkgs)} package(s)!")
                self.selected_pkgs.clear()
                self.refresh()
            GLib.idle_add(done)
        threading.Thread(target=worker, daemon=True).start()

    def on_enable_selected(self, widget):
        if not self.selected_pkgs:
            self.show_msg("Please select at least one package to enable.")
            return

        pkgs = list(self.selected_pkgs)
        def worker():
            success = 0
            for pkg in pkgs:
                ok, _ = self.engine.enable_package(pkg)
                if ok:
                    success += 1
            def done():
                self.show_msg(f"Enabled {success}/{len(pkgs)} package(s)!")
                self.selected_pkgs.clear()
                self.refresh()
            GLib.idle_add(done)
        threading.Thread(target=worker, daemon=True).start()
