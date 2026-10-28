/**
 * Remote Device File Explorer Controller
 */

export function initFiles() {
  let currentRemoteDir = "/storage/emulated/0";

  window.loadDirectory = async function (path) {
    if (!window.pywebview) return;
    currentRemoteDir = path;
    document.getElementById("filePathInput").value = path;
    const tbody = document.getElementById("fileTableBody");
    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 30px;"><div class="skeleton-shimmer" style="height: 24px; width: 50%; margin: auto;"></div></td></tr>';

    const items = await window.pywebview.api.list_directory(path);
    tbody.innerHTML = "";

    if (items.length === 0) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-dim); padding: 30px;">Directory is empty.</td></tr>';
      document.getElementById("fileStatusFooter").textContent = "0 items";
      return;
    }

    document.getElementById("fileStatusFooter").textContent = `${items.length} items in ${path}`;
    const fragment = document.createDocumentFragment();

    items.forEach((it) => {
      const tr = document.createElement("tr");
      tr.style.cursor = "pointer";
      tr.ondblclick = () => {
        if (it.is_dir) {
          window.loadDirectory(it.path);
        } else {
          window.downloadFile(it.path);
        }
      };

      const icon = it.is_dir ? "📁" : "📄";
      tr.innerHTML = `
        <td style="font-weight: 600; color: var(--text-primary);">${icon} ${it.name}</td>
        <td style="color: var(--text-dim);">${it.is_dir ? "Folder" : "File"}</td>
        <td style="font-family: monospace;">${it.size_str}</td>
        <td style="color: var(--text-muted);">${it.date}</td>
      `;
      fragment.appendChild(tr);
    });

    tbody.appendChild(fragment);
  };

  window.navigateUpFolder = function () {
    if (currentRemoteDir === "/storage/emulated/0" || currentRemoteDir === "/") return;
    const parts = currentRemoteDir.split("/").filter((p) => p.length > 0);
    parts.pop();
    const parentDir = "/" + parts.join("/");
    window.loadDirectory(parentDir || "/storage/emulated/0");
  };

  window.downloadFile = async function (remotePath) {
    const localDir = await window.pywebview.api.select_folder();
    if (localDir) {
      await window.pywebview.api.pull_file(remotePath, localDir);
      alert("Downloaded successfully to: " + localDir);
    }
  };

  window.uploadFileDialog = async function () {
    const localFile = await window.pywebview.api.select_file();
    if (localFile) {
      await window.pywebview.api.push_file(localFile, currentRemoteDir);
      window.loadDirectory(currentRemoteDir);
    }
  };
}
