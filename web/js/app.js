/**
 * Master Application Bootstrap for Honor Ecosystem Suite
 * MagicOS 9.0 Obsidian Design System (120 FPS Motion UI)
 */

import { initThemeInteractions } from "./modules/theme.js";
import { initTelemetry } from "./modules/telemetry.js";
import { initBeamer } from "./modules/beamer.js";
import { initDebloater } from "./modules/debloater.js";
import { initMirror } from "./modules/mirror.js";
import { initFiles } from "./modules/files.js";

// Initialize window bindings immediately upon script evaluation
initThemeInteractions();
initTelemetry();
initBeamer();
initDebloater();
initMirror();
initFiles();

document.addEventListener("DOMContentLoaded", () => {
  // 1. Tab change listener for on-demand lazy loading
  window.addEventListener("tab_changed", (e) => {
    const idx = e.detail.tabIndex;
    if (idx === 0 && window.refreshTelemetry) window.refreshTelemetry();
    if (idx === 2 && window.loadPackageList) window.loadPackageList();
    if (idx === 4 && window.loadDirectory) window.loadDirectory("/storage/emulated/0");
  });

  // 2. PyWebView Ready Event Trigger
  window.addEventListener("pywebviewready", () => {
    if (window.refreshTelemetry) window.refreshTelemetry();
    // 5-second non-blocking telemetry loop
    setInterval(() => {
      if (window.refreshTelemetry) window.refreshTelemetry();
    }, 5000);
  });
});
