/**
 * Fast Beam (70+ MB/s) Wireless Synchronizer Controller
 */

export function initBeamer() {
  let selectedPath = "";

  window.selectBeamFile = async function () {
    if (!window.pywebview) return;
    const file = await window.pywebview.api.select_file();
    if (file) {
      selectedPath = file;
      document.getElementById("dropzoneText").textContent = "Selected: " + file.split("\\").pop();
      document.getElementById("dropzoneSub").textContent = file;
    }
  };

  window.selectBeamFolder = async function () {
    if (!window.pywebview) return;
    const folder = await window.pywebview.api.select_folder();
    if (folder) {
      selectedPath = folder;
      document.getElementById("dropzoneText").textContent = "Selected Folder: " + folder.split("\\").pop();
      document.getElementById("dropzoneSub").textContent = folder;
    }
  };

  window.startBeaming = async function () {
    if (!selectedPath) {
      alert("Please select a file or folder first!");
      return;
    }

    const remoteDir = document.getElementById("beamDestSelect").value;
    const autoApple = document.getElementById("chkAutoApple").checked;

    document.getElementById("btnStartBeam").disabled = true;
    document.getElementById("btnCancelBeam").disabled = false;
    document.getElementById("beamStatusMsg").textContent = "Preparing high-speed stream...";

    // Activate waveform animation
    setWaveformsActive(true);

    await window.pywebview.api.start_beam(selectedPath, remoteDir, autoApple);
  };

  window.cancelBeaming = async function () {
    await window.pywebview.api.cancel_beam();
    document.getElementById("btnCancelBeam").disabled = true;
    document.getElementById("btnStartBeam").disabled = false;
    setWaveformsActive(false);
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
  });

  function setWaveformsActive(active) {
    document.querySelectorAll(".wave-bar").forEach((bar) => {
      bar.classList.toggle("active", active);
    });
  }
}
