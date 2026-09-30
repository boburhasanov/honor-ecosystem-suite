"""
Fast Beam & Live Transfer Queue View for Honor Suite
Features high-precision real-time transfer speed gauge (MB/s),
true byte tracking, active connection watchdog, auto-resume,
cancel controls, Apple media conversion guard, and detailed event logging.
"""

import os
import time
import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from typing import Callable, Optional, Dict

class TransferView(Gtk.Box):
    def __init__(self, engine, show_msg: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.engine = engine
        self.show_msg = show_msg
        self.set_border_width(16)

        self.last_path: Optional[str] = None
        self.is_active = False

        self._build_ui()

    def _build_ui(self):
        # 1. Beamer Selection Card
        sel_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        sel_card.get_style_context().add_class("card")

        title = Gtk.Label(label="⚡ High-Speed Wireless File Beam", xalign=0)
        title.get_style_context().add_class("card-title")
        sel_card.pack_start(title, False, False, 0)

        desc = Gtk.Label(
            label="Beam full directories or multi-gigabyte files directly to your Honor 400 Pro over Wi-Fi 6 without cables. Features instant auto-resume, Apple format conversion guard, and live byte-level metrics.",
            xalign=0
        )
        desc.get_style_context().add_class("card-desc")
        desc.set_line_wrap(True)
        sel_card.pack_start(desc, False, False, 0)

        # Options Box: Target Destination & Apple Media Guard
        opt_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Destination selector
        dest_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        dest_lbl = Gtk.Label(label="Target Location:", xalign=0)
        dest_lbl.get_style_context().add_class("text-muted")
        dest_box.pack_start(dest_lbl, False, False, 0)

        self.target_dcim_radio = Gtk.RadioButton.new_with_label_from_widget(None, "📷 DCIM / Camera (Photos & Videos — Native Timeline)")
        self.target_dl_radio = Gtk.RadioButton.new_with_label_from_widget(self.target_dcim_radio, "📥 Download (General Files)")
        dest_box.pack_start(self.target_dcim_radio, False, False, 0)
        dest_box.pack_start(self.target_dl_radio, False, False, 0)
        opt_box.pack_start(dest_box, False, False, 0)

        # Apple Format Guard Toggle
        self.apple_guard_chk = Gtk.CheckButton.new_with_label("🍏 Universal Apple Media Guard (Auto-convert HEIC to JPG & MOV to MP4 for native Gallery)")
        self.apple_guard_chk.set_active(True)
        self.apple_guard_chk.set_tooltip_text("Prevents broken thumbnails and exclamation mark errors in Honor Gallery by converting Apple-specific formats on the fly.")
        opt_box.pack_start(self.apple_guard_chk, False, False, 0)

        sel_card.pack_start(opt_box, False, False, 2)

        # Action Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        folder_btn = Gtk.Button.new_with_label("📁 Beam Entire Folder...")
        folder_btn.get_style_context().add_class("btn-primary")
        folder_btn.connect("clicked", self.on_select_folder)
        btn_box.pack_start(folder_btn, True, True, 0)

        files_btn = Gtk.Button.new_with_label("📄 Beam Multiple Files...")
        files_btn.get_style_context().add_class("btn-success")
        files_btn.connect("clicked", self.on_select_files)
        btn_box.pack_start(files_btn, True, True, 0)

        sel_card.pack_start(btn_box, False, False, 4)
        self.pack_start(sel_card, False, False, 0)

        # 2. Live Speedometer & Progress Card
        self.prog_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.prog_card.get_style_context().add_class("card")

        # Top Bar: Title + Status Badge
        hdr_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        prog_title = Gtk.Label(label="LIVE TRANSFER INSTRUMENTATION", xalign=0)
        prog_title.get_style_context().add_class("metric-label")
        hdr_box.pack_start(prog_title, True, True, 0)

        self.badge_lbl = Gtk.Label(label="Idle", xalign=0.5)
        self.badge_lbl.get_style_context().add_class("badge-muted")
        hdr_box.pack_start(self.badge_lbl, False, False, 0)
        self.prog_card.pack_start(hdr_box, False, False, 0)

        # Current File / Operation
        self.filename_lbl = Gtk.Label(label="Idle — Ready to beam", xalign=0)
        self.filename_lbl.get_style_context().add_class("card-title")
        self.filename_lbl.set_ellipsize(3) # PANGO_ELLIPSIZE_END
        self.prog_card.pack_start(self.filename_lbl, False, False, 0)

        # Main Progress Bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_fraction(0.0)
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("0%")
        self.prog_card.pack_start(self.progress_bar, False, False, 2)

        # Metrics grid: Speed + Bytes + Files
        grid = Gtk.Grid()
        grid.set_column_spacing(16)
        grid.set_column_homogeneous(True)

        # Speed Gauge
        spd_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        spd_lbl = Gtk.Label(label="TRANSFER SPEED", xalign=0)
        spd_lbl.get_style_context().add_class("metric-label")
        spd_box.pack_start(spd_lbl, False, False, 0)

        self.speed_val_lbl = Gtk.Label(label="0.0 MB/s", xalign=0)
        self.speed_val_lbl.get_style_context().add_class("metric-value")
        spd_box.pack_start(self.speed_val_lbl, False, False, 0)
        grid.attach(spd_box, 0, 0, 1, 1)

        # Data transferred
        data_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        data_lbl = Gtk.Label(label="DATA TRANSFERRED", xalign=0)
        data_lbl.get_style_context().add_class("metric-label")
        data_box.pack_start(data_lbl, False, False, 0)

        self.bytes_val_lbl = Gtk.Label(label="0 MB / 0 MB (0%)", xalign=0)
        self.bytes_val_lbl.get_style_context().add_class("metric-value")
        data_box.pack_start(self.bytes_val_lbl, False, False, 0)
        grid.attach(data_box, 1, 0, 1, 1)

        # Files Count
        files_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        files_lbl = Gtk.Label(label="FILES PROCESSED", xalign=0)
        files_lbl.get_style_context().add_class("metric-label")
        files_box.pack_start(files_lbl, False, False, 0)

        self.files_val_lbl = Gtk.Label(label="0 / 0 files", xalign=0)
        self.files_val_lbl.get_style_context().add_class("metric-value")
        files_box.pack_start(self.files_val_lbl, False, False, 0)
        grid.attach(files_box, 2, 0, 1, 1)

        self.prog_card.pack_start(grid, False, False, 4)

        # Control Buttons: Cancel & Retry / Resume
        ctrl_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        self.cancel_btn = Gtk.Button.new_with_label("🛑 Cancel Transfer")
        self.cancel_btn.get_style_context().add_class("btn-danger")
        self.cancel_btn.set_sensitive(False)
        self.cancel_btn.connect("clicked", self.on_cancel_clicked)
        ctrl_box.pack_start(self.cancel_btn, True, True, 0)

        self.resume_btn = Gtk.Button.new_with_label("🔄 Retry / Resume")
        self.resume_btn.get_style_context().add_class("btn-secondary")
        self.resume_btn.set_sensitive(False)
        self.resume_btn.connect("clicked", self.on_resume_clicked)
        ctrl_box.pack_start(self.resume_btn, True, True, 0)

        self.prog_card.pack_start(ctrl_box, False, False, 4)

        # Activity Log Mini Terminal
        log_expander = Gtk.Expander(label="Activity Log & Diagnostic Details")
        log_expander.set_expanded(True)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(100)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.log_buffer = Gtk.TextBuffer()
        self.log_view = Gtk.TextView(buffer=self.log_buffer)
        self.log_view.set_editable(False)
        self.log_view.set_cursor_visible(False)
        self.log_view.get_style_context().add_class("view")
        scrolled.add(self.log_view)

        log_expander.add(scrolled)
        self.prog_card.pack_start(log_expander, True, True, 0)

        self.pack_start(self.prog_card, True, True, 0)
        self._append_log("Fast Beam initialized. Select folder or files to begin.")

    def _append_log(self, text: str):
        t_str = time.strftime("%H:%M:%S")
        end_iter = self.log_buffer.get_end_iter()
        self.log_buffer.insert(end_iter, f"[{t_str}] {text}\n")
        # Scroll to bottom
        mark = self.log_buffer.create_mark(None, self.log_buffer.get_end_iter(), False)
        self.log_view.scroll_to_mark(mark, 0.0, False, 0.0, 0.0)

    def _set_badge(self, text: str, css_class: str):
        self.badge_lbl.set_text(text)
        ctx = self.badge_lbl.get_style_context()
        for c in ["badge-muted", "badge-active", "badge-amber", "badge-danger", "badge-cyan"]:
            ctx.remove_class(c)
        ctx.add_class(css_class)

    def on_cancel_clicked(self, widget):
        self._append_log("User requested cancellation. Aborting transfer...")
        self.engine.cancel_transfer()
        self.cancel_btn.set_sensitive(False)
        self.filename_lbl.set_text("Cancelling transfer...")
        self._set_badge("Cancelling...", "badge-amber")

    def on_resume_clicked(self, widget):
        if self.last_path:
            self._append_log(f"Resuming transfer for: {os.path.basename(self.last_path)}...")
            self._start_beam(self.last_path)

    def on_select_folder(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Select Folder to Beam Wirelessly",
            parent=self.get_toplevel(),
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Beam Folder", Gtk.ResponseType.OK)
        res = dialog.run()
        folder_path = dialog.get_filename()
        dialog.destroy()

        if res == Gtk.ResponseType.OK and folder_path:
            self.last_path = folder_path
            self._start_beam(folder_path)

    def on_select_files(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Select Files to Beam Wirelessly",
            parent=self.get_toplevel(),
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Beam Files", Gtk.ResponseType.OK)
        dialog.set_select_multiple(True)
        res = dialog.run()
        files = dialog.get_filenames()
        dialog.destroy()

        if res == Gtk.ResponseType.OK and files:
            # Beam each file or start queue
            for f in files:
                self.last_path = f
                self._start_beam(f)

    def _get_target_dir(self) -> str:
        if self.target_dcim_radio.get_active():
            return "/storage/emulated/0/DCIM/Camera"
        return "/storage/emulated/0/Download"

    def _start_beam(self, local_path: str):
        target_dir = self._get_target_dir()
        auto_convert = self.apple_guard_chk.get_active()

        self.is_active = True
        self.cancel_btn.set_sensitive(True)
        self.resume_btn.set_sensitive(False)

        self.filename_lbl.set_text(f"Beaming: {os.path.basename(local_path)}...")
        self.progress_bar.set_fraction(0.0)
        self.progress_bar.set_text("Connecting...")
        self.speed_val_lbl.set_text("0.0 MB/s")
        self.bytes_val_lbl.set_text("Calculating...")
        self.files_val_lbl.set_text("0 files")
        self._set_badge("🟢 Active Beam", "badge-active")

        self._append_log(f"Starting beam: {local_path} -> {target_dir}")
        if auto_convert:
            self._append_log("Universal Apple Media Guard is enabled.")

        def on_progress(data: Dict):
            def update_ui():
                status = data.get("status", "BEAMING")
                fraction = data.get("fraction", 0.0)
                speed_mb = data.get("speed_mb", 0.0)
                sent_bytes = data.get("sent_bytes", 0)
                total_bytes = data.get("total_bytes", 1)
                file_idx = data.get("file_idx", 0)
                total_files = data.get("total_files", 0)
                curr_file = data.get("current_file", "")
                msg = data.get("message", "")

                pct = int(fraction * 100)
                self.progress_bar.set_fraction(min(fraction, 1.0))
                self.progress_bar.set_text(f"{pct}%")
                self.speed_val_lbl.set_text(f"⚡ {speed_mb:.1f} MB/s" if speed_mb > 0 else "0.0 MB/s")

                sent_mb = sent_bytes / (1024 * 1024)
                total_mb = total_bytes / (1024 * 1024)
                if total_mb > 1024:
                    self.bytes_val_lbl.set_text(f"{sent_mb/1024:.2f} GB / {total_mb/1024:.2f} GB ({pct}%)")
                else:
                    self.bytes_val_lbl.set_text(f"{sent_mb:.1f} MB / {total_mb:.1f} MB ({pct}%)")

                self.files_val_lbl.set_text(f"{file_idx} / {total_files} files")

                if status == "CONVERTING":
                    self._set_badge("🔄 Converting Media", "badge-cyan")
                    self.filename_lbl.set_text(f"Optimizing: {curr_file}")
                elif status == "INDEXING":
                    self._set_badge("🔍 Indexing Resume", "badge-cyan")
                    self.filename_lbl.set_text("Checking existing files on device...")
                elif status == "RECONNECTING":
                    self._set_badge("🟠 Reconnecting...", "badge-amber")
                    self.speed_val_lbl.set_text("0.0 MB/s")
                    self.filename_lbl.set_text(msg)
                    self._append_log(msg)
                elif status == "CANCELLED":
                    self._set_badge("⚪ Cancelled", "badge-muted")
                    self.speed_val_lbl.set_text("0.0 MB/s")
                    self.filename_lbl.set_text("Transfer cancelled by user")
                    self._append_log("Transfer was cancelled.")
                elif status == "COMPLETED":
                    self._set_badge("✅ Completed", "badge-active")
                    self.speed_val_lbl.set_text(f"⚡ {speed_mb:.1f} MB/s")
                    self.filename_lbl.set_text(f"✅ Completed: {os.path.basename(local_path)}")
                    self._append_log(f"Transfer finished successfully at {speed_mb:.1f} MB/s!")
                else:
                    self._set_badge("🟢 Active Beam", "badge-active")
                    if curr_file:
                        self.filename_lbl.set_text(f"Beaming ({file_idx}/{total_files}): {curr_file}")

            GLib.idle_add(update_ui)

        def worker():
            ok, msg = self.engine.push_path(
                local_path,
                target_dir,
                progress_cb=on_progress,
                auto_convert_apple=auto_convert
            )
            def done():
                self.is_active = False
                self.cancel_btn.set_sensitive(False)
                if ok:
                    self.resume_btn.set_sensitive(False)
                    self.show_msg(f"Finished beaming {os.path.basename(local_path)}!")
                else:
                    self.resume_btn.set_sensitive(True)
                    if "cancelled" in msg.lower():
                        self._set_badge("⚪ Cancelled", "badge-muted")
                        self.show_msg("Transfer cancelled.")
                    else:
                        self._set_badge("🔴 Transfer Failed", "badge-danger")
                        self.filename_lbl.set_text(f"Error: {msg}")
                        self._append_log(f"Error: {msg}")
                        self.show_msg(f"Transfer failed: {msg}")
            GLib.idle_add(done)

        threading.Thread(target=worker, daemon=True).start()
