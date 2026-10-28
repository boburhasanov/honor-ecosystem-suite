/**
 * Wireless Screen Mirror Controller (powered by Scrcpy)
 * Supports 1440p / 1080p / 720p 60 FPS presets, audio routing, and display-off mode.
 */

export function initMirror() {
  window.startMirrorSession = async function () {
    if (!window.pywebview) return;
    const preset = document.getElementById("mirrorPresetSelect").value;
    const screenOff = document.getElementById("chkTurnScreenOff").checked;
    const awake = document.getElementById("chkStayAwake").checked;
    const audio = document.getElementById("chkForwardAudio").checked;

    const statusEl = document.getElementById("mirrorStatusText");
    statusEl.textContent = `Starting ${preset} session...`;
    statusEl.style.color = "var(--cyan-glow)";

    if (window.toast) window.toast.info(`Launching ${preset} screen mirror...`);

    const res = await window.pywebview.api.launch_mirror(preset, screenOff, awake, audio);
    statusEl.textContent = res.message;
    statusEl.style.color = res.success ? "var(--emerald-glow)" : "var(--red-glow)";

    if (window.toast) {
      if (res.success) {
        window.toast.success(`Screen Mirror connected (${preset})`);
      } else {
        window.toast.error(res.message);
      }
    }
  };
}
