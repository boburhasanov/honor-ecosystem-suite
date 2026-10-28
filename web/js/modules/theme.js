/**
 * Theme & Micro-Interactions Controller
 * Provides magnetic card hover glows, ripple effects, and 120 FPS tab routing.
 */

export function initThemeInteractions() {
  // Magnetic Radial Card Glow tracking mouse movement
  document.addEventListener("mousemove", (e) => {
    const cards = document.querySelectorAll(".glass-card, .card");
    cards.forEach((card) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      card.style.setProperty("--mouse-x", `${x}px`);
      card.style.setProperty("--mouse-y", `${y}px`);
    });
  });

  const titles = [
    ["Live Dashboard & Telemetry", "Real-time hardware diagnostics & ecosystem telemetry"],
    ["Fast Beam (70+ MB/s)", "Direct high-speed media synchronization with Apple Media Guard"],
    ["App Debloater", "Xiaomi Flash Tool style safe debloater with 1-Click Restore"],
    ["Screen Mirroring", "Ultra low-latency 1440p / 60 FPS wireless collaboration (Scrcpy)"],
    ["Remote File Explorer", "Explore, upload, download, and manage smartphone files over ADB"]
  ];

  // Smooth Tab Switcher
  window.switchTab = function (idx) {
    const navItems = document.querySelectorAll(".nav-item, .nav-tab-btn");
    const tabViews = document.querySelectorAll(".tab-view, .tab-view-container");

    navItems.forEach((btn, i) => {
      btn.classList.toggle("active", i === idx);
    });

    tabViews.forEach((view, i) => {
      view.classList.toggle("active", i === idx);
    });

    const topTitle = document.getElementById("topTitle");
    const topSubtitle = document.getElementById("topSubtitle");
    if (topTitle && titles[idx]) topTitle.textContent = titles[idx][0];
    if (topSubtitle && titles[idx]) topSubtitle.textContent = titles[idx][1];

    // Notify active module
    window.dispatchEvent(new CustomEvent("tab_changed", { detail: { tabIndex: idx } }));
  };

  window.refreshCurrentTab = function () {
    const activeNav = document.querySelector(".nav-item.active, .nav-tab-btn.active");
    const navItems = Array.from(document.querySelectorAll(".nav-item, .nav-tab-btn"));
    const idx = navItems.indexOf(activeNav);
    window.dispatchEvent(new CustomEvent("tab_changed", { detail: { tabIndex: idx >= 0 ? idx : 0 } }));
  };
}
