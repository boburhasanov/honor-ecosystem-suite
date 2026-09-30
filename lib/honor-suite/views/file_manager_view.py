"""
Interactive Phone File Manager View for Honor Suite
Enables full wireless browsing of internal phone storage (/sdcard),
folder navigation, folder & file uploading, downloading, and deletion.
"""

import os
import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
from typing import Callable, Optional

class FileManagerView(Gtk.Box):
    def __init__(self, engine, show_msg: Callable[[str], None]):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.engine = engine
        self.show_msg = show_msg
        self.current_path = "/storage/emulated/0"
        self.set_border_width(14)

        self._build_ui()

    def _build_ui(self):
        # 1. Header Toolbar Card
        top_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        top_card.get_style_context().add_class("card")

        # Breadcrumbs row
        path_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        home_btn = Gtk.Button.new_with_label("🏠 Home")
        home_btn.get_style_context().add_class("btn-secondary")
        home_btn.connect("clicked", lambda b: self.navigate_to("/storage/emulated/0"))
        path_box.pack_start(home_btn, False, False, 0)

        up_btn = Gtk.Button.new_with_label("⬆ Up")
        up_btn.get_style_context().add_class("btn-secondary")
        up_btn.connect("clicked", self.on_up_clicked)
        path_box.pack_start(up_btn, False, False, 0)

        self.path_entry = Gtk.Entry()
        self.path_entry.set_text(self.current_path)
        self.path_entry.connect("activate", lambda e: self.navigate_to(e.get_text().strip()))
        path_box.pack_start(self.path_entry, True, True, 0)

        refresh_btn = Gtk.Button.new_with_label("🔄")
        refresh_btn.get_style_context().add_class("btn-secondary")
        refresh_btn.connect("clicked", lambda b: self.navigate_to(self.current_path))
        path_box.pack_end(refresh_btn, False, False, 0)
        top_card.pack_start(path_box, False, False, 0)

        # Action Buttons Row
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        upload_folder_btn = Gtk.Button.new_with_label("📁 Upload Folder...")
        upload_folder_btn.get_style_context().add_class("btn-primary")
        upload_folder_btn.connect("clicked", self.on_upload_folder)
        action_box.pack_start(upload_folder_btn, False, False, 0)

        upload_files_btn = Gtk.Button.new_with_label("📄 Upload Files...")
        upload_files_btn.get_style_context().add_class("btn-success")
        upload_files_btn.connect("clicked", self.on_upload_files)
        action_box.pack_start(upload_files_btn, False, False, 0)

        download_btn = Gtk.Button.new_with_label("📥 Download to PC")
        download_btn.get_style_context().add_class("btn-secondary")
        download_btn.connect("clicked", self.on_download_selected)
        action_box.pack_start(download_btn, False, False, 0)

        delete_btn = Gtk.Button.new_with_label("🗑️ Delete")
        delete_btn.get_style_context().add_class("btn-danger")
        delete_btn.connect("clicked", self.on_delete_selected)
        action_box.pack_end(delete_btn, False, False, 0)

        top_card.pack_start(action_box, False, False, 0)
        self.pack_start(top_card, False, False, 0)

        # 2. File Explorer Table
        list_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        list_card.get_style_context().add_class("card")

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.set_min_content_height(420)

        # ListStore: [Icon(str), Name(str), Size(str), Date(str), FullPath(str), IsDir(bool)]
        self.store = Gtk.ListStore(str, str, str, str, str, bool)

        self.tree = Gtk.TreeView(model=self.store)
        self.tree.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.tree.connect("row-activated", self.on_row_activated)

        # Column 1: Icon + Name
        col1 = Gtk.TreeViewColumn("Name")
        col1.set_expand(True)
        col1.set_sort_column_id(1)

        rend_icon = Gtk.CellRendererText()
        col1.pack_start(rend_icon, False)
        col1.add_attribute(rend_icon, "text", 0)

        rend_name = Gtk.CellRendererText()
        col1.pack_start(rend_name, True)
        col1.add_attribute(rend_name, "text", 1)
        self.tree.append_column(col1)

        # Column 2: Size
        rend_size = Gtk.CellRendererText()
        col2 = Gtk.TreeViewColumn("Size", rend_size, text=2)
        col2.set_min_width(110)
        col2.set_sort_column_id(2)
        self.tree.append_column(col2)

        # Column 3: Date
        rend_date = Gtk.CellRendererText()
        col3 = Gtk.TreeViewColumn("Modified", rend_date, text=3)
        col3.set_min_width(120)
        col3.set_sort_column_id(3)
        self.tree.append_column(col3)

        scroller.add(self.tree)
        list_card.pack_start(scroller, True, True, 0)

        # Status footer
        self.status_lbl = Gtk.Label(label="Ready", xalign=0)
        self.status_lbl.get_style_context().add_class("card-desc")
        list_card.pack_start(self.status_lbl, False, False, 4)

        self.pack_start(list_card, True, True, 0)

    def navigate_to(self, path: str):
        self.current_path = path.rstrip("/")
        if not self.current_path:
            self.current_path = "/storage/emulated/0"
        self.path_entry.set_text(self.current_path)
        self.status_lbl.set_text(f"Loading {self.current_path}...")

        def worker():
            items = self.engine.list_directory(self.current_path)
            def update_ui():
                self.store.clear()
                dir_count = 0
                file_count = 0
                for item in items:
                    icon = "📁 " if item["is_dir"] else "📄 "
                    if item["is_dir"]:
                        dir_count += 1
                    else:
                        file_count += 1
                    self.store.append([
                        icon,
                        item["name"],
                        item["size_str"],
                        item["date"],
                        item["path"],
                        item["is_dir"]
                    ])
                self.status_lbl.set_text(f"{dir_count} folders, {file_count} files in {self.current_path}")
            GLib.idle_add(update_ui)

        threading.Thread(target=worker, daemon=True).start()

    def on_up_clicked(self, widget):
        parent = os.path.dirname(self.current_path)
        if parent and parent != "/" and parent.startswith("/storage"):
            self.navigate_to(parent)

    def on_row_activated(self, tree, path, column):
        model = tree.get_model()
        iter_ = model.get_iter(path)
        if iter_:
            name = model.get_value(iter_, 1)
            full_path = model.get_value(iter_, 4)
            is_dir = model.get_value(iter_, 5)
            if is_dir:
                self.navigate_to(full_path)
            else:
                self.show_msg(f"Selected file: {name}. Use 'Download to PC' to save it.")

    def on_upload_folder(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Select Folder to Beam to Phone",
            parent=self.get_toplevel(),
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Upload Folder", Gtk.ResponseType.OK)
        res = dialog.run()
        folder_path = dialog.get_filename()
        dialog.destroy()

        if res == Gtk.ResponseType.OK and folder_path:
            self.show_msg(f"Beaming folder {os.path.basename(folder_path)} wirelessly to {self.current_path}...")
            def worker():
                ok, msg = self.engine.push_path(folder_path, self.current_path)
                def done():
                    self.show_msg(msg)
                    self.navigate_to(self.current_path)
                GLib.idle_add(done)
            threading.Thread(target=worker, daemon=True).start()

    def on_upload_files(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Select Files to Beam to Phone",
            parent=self.get_toplevel(),
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Upload Files", Gtk.ResponseType.OK)
        dialog.set_select_multiple(True)
        res = dialog.run()
        files = dialog.get_filenames()
        dialog.destroy()

        if res == Gtk.ResponseType.OK and files:
            self.show_msg(f"Beaming {len(files)} file(s) wirelessly to {self.current_path}...")
            def worker():
                for f in files:
                    self.engine.push_path(f, self.current_path)
                def done():
                    self.show_msg(f"Beamed {len(files)} file(s) successfully!")
                    self.navigate_to(self.current_path)
                GLib.idle_add(done)
            threading.Thread(target=worker, daemon=True).start()

    def on_download_selected(self, widget):
        sel = self.tree.get_selection()
        model, iter_ = sel.get_selected()
        if not iter_:
            self.show_msg("Please select a file or folder from the list first.")
            return

        name = model.get_value(iter_, 1)
        full_path = model.get_value(iter_, 4)
        dest_dir = os.path.expanduser("~/Downloads/Honor")
        self.show_msg(f"Downloading {name} to {dest_dir}...")

        def worker():
            ok, msg = self.engine.pull_path(full_path, dest_dir)
            def done():
                self.show_msg(f"Downloaded {name} to {dest_dir}!")
                import subprocess
                subprocess.Popen(["nemo", dest_dir])
            GLib.idle_add(done)
        threading.Thread(target=worker, daemon=True).start()

    def on_delete_selected(self, widget):
        sel = self.tree.get_selection()
        model, iter_ = sel.get_selected()
        if not iter_:
            self.show_msg("Please select a file or folder to delete.")
            return

        name = model.get_value(iter_, 1)
        full_path = model.get_value(iter_, 4)

        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=0,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=f"Delete '{name}' from phone?"
        )
        dialog.format_secondary_text("This action cannot be undone.")
        res = dialog.run()
        dialog.destroy()

        if res == Gtk.ResponseType.OK:
            self.show_msg(f"Deleting {name}...")
            def worker():
                ok, msg = self.engine.delete_path(full_path)
                def done():
                    self.show_msg(f"Deleted {name}")
                    self.navigate_to(self.current_path)
                GLib.idle_add(done)
            threading.Thread(target=worker, daemon=True).start()
