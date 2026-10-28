/**
 * Glassmorphic Toast Notification Controller
 * Displays non-blocking, elegant notifications with status indicators and auto-dismissal.
 */

class ToastManager {
  constructor() {
    this.container = null;
    this.init();
  }

  init() {
    if (!document.body) return;
    let el = document.getElementById("toastContainer");
    if (!el) {
      el = document.createElement("div");
      el.id = "toastContainer";
      el.className = "toast-container";
      document.body.appendChild(el);
    }
    this.container = el;
  }

  show(message, type = "info", durationMs = 3500) {
    if (!this.container) this.init();

    const toast = document.createElement("div");
    toast.className = `toast-pill toast-${type}`;

    let icon = "ℹ️";
    if (type === "success") icon = "✅";
    if (type === "error") icon = "⚠️";
    if (type === "warning") icon = "🔔";

    toast.innerHTML = `
      <span class="toast-icon">${icon}</span>
      <span class="toast-message">${message}</span>
      <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    this.container.appendChild(toast);

    // Trigger enter animation
    requestAnimationFrame(() => {
      toast.classList.add("show");
    });

    // Auto dismiss
    setTimeout(() => {
      toast.classList.remove("show");
      setTimeout(() => toast.remove(), 300);
    }, durationMs);
  }

  success(msg, dur) { this.show(msg, "success", dur); }
  error(msg, dur) { this.show(msg, "error", dur); }
  warning(msg, dur) { this.show(msg, "warning", dur); }
  info(msg, dur) { this.show(msg, "info", dur); }
}

export const toast = new ToastManager();
window.toast = toast;
