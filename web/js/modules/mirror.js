/**
 * Wireless Screen Mirror Controller (powered by Scrcpy)
 */

export function initMirror() {
  window.startMirrorSession = async function () {
    if (!window.pywebview) return;
    const preset = document.getElementById("mirrorPresetSelect").value;
    const screenOff = document.getElementById("chkTurnScreenOff").checked;
    const awake = document.getElementById("chkStayAwake").checked;
    const audio = document.getElementById("chkForwardAudio").checked;

    const statusEl = document.getElementById("mirrorStatusText");
    statusEl.textContent = "Starting 1440p session...";
    statusEl.style.color = "var(--cyan-glow)";

    const res = await window.pywebview.api.launch_mirror(preset, screenOff, awake, audio);
    statusEl.textContent = res.message;
    statusEl.style.color = res.success ? "var(--emerald-glow)" : "var(--red-glow)";
  };
}
