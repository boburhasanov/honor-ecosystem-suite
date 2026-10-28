"""
Remote File Browser Service for Honor Ecosystem Suite.
Enables rapid directory navigation, upload, download, and deletion directly over ADB.
"""

import os
from typing import List, Dict, Tuple
from lib.honor_suite.core.adb_service import AdbService

class FileBrowserService:
    def __init__(self, adb: AdbService):
        self.adb = adb

    def list_directory(self, remote_path: str = "/storage/emulated/0") -> List[Dict]:
        """
        High-performance POSIX directory lister executing single-pass stat on device.
        """
        clean_path = remote_path.rstrip("/") or "/storage/emulated/0"

        script = f"""
for f in "{clean_path}"/* "{clean_path}"/.*; do
    [ "$f" = "{clean_path}/*" ] && continue
    [ "$f" = "{clean_path}/." ] && continue
    [ "$f" = "{clean_path}/.." ] && continue
    [ -e "$f" ] || continue
    name=$(basename "$f")
    if [ -d "$f" ]; then
        echo "DIR|$name|0|0"
    else
        size=$(stat -c%s "$f" 2>/dev/null || echo 0)
        mtime=$(stat -c%y "$f" 2>/dev/null | cut -d' ' -f1 || echo "")
        echo "FILE|$name|$size|$mtime"
    fi
done
"""
        code, out, _ = self.adb.run_cmd(["shell", script], timeout=8)
        items: List[Dict] = []

        for line in out.splitlines():
            line = line.strip()
            if not line or "|" not in line:
                continue
            parts = line.split("|")
            if len(parts) >= 4:
                is_dir = parts[0] == "DIR"
                name = parts[1]
                size_bytes = int(parts[2]) if parts[2].isdigit() else 0
                date_str = parts[3]

                if is_dir:
                    size_str = "Folder"
                else:
                    if size_bytes > 1024 * 1024 * 1024:
                        size_str = f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
                    elif size_bytes > 1024 * 1024:
                        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
                    elif size_bytes > 1024:
                        size_str = f"{size_bytes / 1024:.1f} KB"
                    else:
                        size_str = f"{size_bytes} B"

                items.append({
                    "name": name,
                    "is_dir": is_dir,
                    "size_str": size_str,
                    "size_bytes": size_bytes,
                    "date": date_str,
                    "path": f"{clean_path}/{name}"
                })

        dirs = sorted([x for x in items if x["is_dir"]], key=lambda x: x["name"].lower())
        files = sorted([x for x in items if not x["is_dir"]], key=lambda x: x["name"].lower())
        return dirs + files

    def pull_file(self, remote_path: str, local_dest_dir: str) -> Tuple[bool, str]:
        """Pulls a remote file or folder into the specified local folder."""
        os.makedirs(local_dest_dir, exist_ok=True)
        code, out, err = self.adb.run_cmd(["pull", "-a", remote_path, local_dest_dir], timeout=180)
        if code == 0:
            return True, f"Downloaded to {local_dest_dir}"
        return False, err or out

    def push_file(self, local_path: str, remote_dest_dir: str) -> Tuple[bool, str]:
        """Pushes a local file or folder to the remote phone directory."""
        code, out, err = self.adb.run_cmd(["push", local_path, remote_dest_dir], timeout=180)
        if code == 0:
            return True, f"Uploaded to {remote_dest_dir}"
        return False, err or out

    def delete_item(self, remote_path: str) -> Tuple[bool, str]:
        """Deletes a file or directory on the phone."""
        code, out, err = self.adb.run_cmd(["shell", "rm", "-rf", f"'{remote_path}'"], timeout=10)
        if code == 0:
            return True, "Item deleted"
        return False, err or out
