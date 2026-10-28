/**
 * Fast Beam (70+ MB/s) Wireless Synchronizer Controller
 * Features drag-and-drop feedback, real-time audio-wave equalizer, and glassmorphic toasts.
 */

export function initBeamer() {
  let selectedPath = "";

  window.selectBeamFile = async function () {
    if (!window.pywebview) return;
    const file = await window.pywebview.api.select_file();
    if (file) {
      selectedPath = file;
      const fileName = file.split("\\").pop();
      document.getElementById("dropzoneText").textContent = "Selected: " + fileName;
      document.getElementById("dropzoneSub").textContent = file;
      if (window.toast) window.toast.info(`Selected file: ${fileName}`);
    }
  };

  window.selectBeamFolder = async function () {
    if (!window.pywebview) return;
    const folder = await window.pywebview.api.select_folder();
    if (folder) {
      selectedPath = folder;
      const folderName = folder.split("\\").pop();
      document.getElementById("dropzoneText").textContent = "Selected Folder: " + folderName;
      document.getElementById("dropzoneSub").textContent = folder;
      if (window.toast) window.toast.info(`Selected folder: ${folderName}`);
    }
  };

  window.startBeaming = async function () {
    if (!selectedPath) {
      if (window.toast) {
        window.toast.warning("Please select a file or folder first!");
      } else {
        alert("Please select a file or folder first!");
      }
      return;
    }

    const remoteDir = document.getElementById("beamDestSelect").value;
    const autoApple = document.getElementById("chkAutoApple").checked;

    document.getElementById("btnStartBeam").disabled = true;
    document.getElementById("btnCancelBeam").disabled = false;
    document.getElementById("beamStatusMsg").textContent = "Preparing high-speed stream...";

    // Activate waveform animation
    setWaveformsActive(true);

    if (window.toast) window.toast.info("Fast Beam initiated (70+ MB/s direct ADB)...");

    await window.pywebview.api.start_beam(selectedPath, remoteDir, autoApple);
  };

  window.cancelBeaming = async function () {
    await window.pywebview.api.cancel_beam();
    document.getElementById("btnCancelBeam").disabled = true;
    document.getElementById("btnStartBeam").disabled = false;
    setWaveformsActive(false);
    if (window.toast) window.toast.warning("Transfer cancelled by user.");
  };

  window.addEventListener("beam_progress", (e) => {
    const d = e.detail;
    document.getElementById("beamStatusMsg").textContent = d.message || "Beaming...";
    document.getElementById("beamSpeedText").textContent = `${(d.speed_mb || 0).toFixed(1)} MB/s`;
    document.getElementById("beamProgressBar").style.width = `${((d.fraction || 0) * 100)}%`;
    document.getElementById("beamItemCounter").textContent = `${d.file_idx || 0} / ${d.total_files || 0} items`;

    const sentMb = ((d.sent_bytes || 0) / (1024 * 1024)).toFixed(1);
    const totalMb = ((d.total_bytes || 1) / (1024 * 1024)).toFixed(1);
    document.getElementById("beamBytesCounter").textContent = `${sentMb} MB / ${totalMb} MB`;
  });

  window.addEventListener("beam_finished", (e) => {
    const d = e.detail;
    document.getElementById("btnStartBeam").disabled = false;
    document.getElementById("btnCancelBeam").disabled = true;
    document.getElementById("beamStatusMsg").textContent = d.message;
    setWaveformsActive(false);

    if (window.toast) {
      if (d.success) {
        window.toast.success(d.message);
      } else {
        window.toast.error(d.message);
      }
    }
  });

  function setWaveformsActive(active) {
    document.querySelectorAll(".wave-bar").forEach((bar) => {
      bar.classList.toggle("active", active);
    });
  }
}
