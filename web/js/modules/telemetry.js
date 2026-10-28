/**
 * Live Telemetry & Hardware Gauges Controller
 * 100% Dynamic, Multi-Model Universal Profiler & 1-Click Wireless Handshake
 */

export function initTelemetry() {
  // Listen for real-time background telemetry events from Python daemon
  window.addEventListener("telemetry_update", (e) => {
    if (e.detail) updateTelemetryView(e.detail);
  });

  window.refreshTelemetry = async function () {
    if (!window.pywebview) return;
    try {
      const data = await window.pywebview.api.get_telemetry();
      updateTelemetryView(data);
    } catch (err) {
      console.error("Telemetry error:", err);
    }
  };

  window.enableWirelessHandshake = async function () {
    if (!window.pywebview) return;
    const btn = document.getElementById("btnEnableWireless");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Configuring Wireless...";
    }
    if (window.toast) window.toast.info("Enabling TCP port 5555 and establishing wireless link...");

    try {
      const res = await window.pywebview.api.enable_wireless_mode();
      if (res.success) {
        if (window.toast) window.toast.success(res.message, 6000);
        await window.refreshTelemetry();
      } else {
        if (window.toast) window.toast.error(res.message, 6000);
      }
    } catch (err) {
      if (window.toast) window.toast.error("Handshake error: " + err);
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = "⚡ Switch to Wireless Mode";
      }
    }
  };

  function updateTelemetryView(data) {
    const isConn = data.connected;
    const dot = document.getElementById("statusDot");
    const pill = document.getElementById("devicePillText");
    const badge = document.getElementById("connectionBadge");
    const btnWireless = document.getElementById("btnEnableWireless");

    if (isConn) {
      dot.classList.remove("offline");
      pill.textContent = data.model || "Android Device";

      const isWireless = data.connection_type === "wireless";
      if (badge) {
        badge.textContent = isWireless ? "Online • Wireless Hotspot/Wi-Fi" : "Online • USB Connected";
        badge.className = "status-pill-badge badge-emerald";
      }

      if (btnWireless) {
        if (isWireless) {
          btnWireless.style.display = "none";
        } else {
          btnWireless.style.display = "inline-flex";
          btnWireless.textContent = "⚡ Switch to Wireless Mode";
        }
      }

      const mName = document.getElementById("devModelName");
      if (mName) mName.textContent = "📱 " + (data.model || "Honor Device");

      const osVer = document.getElementById("devOsVersion");
      if (osVer) osVer.textContent = `MagicOS Suite • ${data.android || "Android"}`;

      const tIp = document.getElementById("targetIpText");
      if (tIp) tIp.textContent = "Endpoint: " + data.target;

      // Battery Gauge
      const bLvl = data.battery_level || 0;
      setVal("batLevelVal", `${bLvl}%`);
      setVal("batDetailsVal", `${data.battery_voltage_v}V • ${data.battery_temp_c}°C`);
      setVal("batStatusPill", data.battery_status || "Active");
      setVal("batSohVal", data.battery_soh > 0 ? `Health: ${data.battery_soh}% SOH • ${data.battery_cycles} Cycles` : `Battery Status: ${data.battery_status || 'Normal'}`);
      setGauge("batGaugeCircle", "batGaugeText", bLvl);

      // RAM Gauge (/proc/meminfo)
      const rPct = data.ram_percent || 0;
      setVal("ramUsedVal", `${data.ram_used_gb} / ${data.ram_total_gb} GB`);
      setVal("ramTotalVal", `Total: ${data.ram_total_gb} GB Physical RAM`);
      setVal("ramFreeVal", `Available: ${data.ram_free_gb} GB (Active / Cache)`);
      setGauge("ramGaugeCircle", "ramGaugeText", rPct);

      // Storage Gauge
      const sPct = data.storage_percent || 0;
      setVal("storageUsedVal", `${data.storage_used_gb} / ${data.storage_total_gb} GB`);
      setVal("storageTotalVal", `Total: ${data.storage_total_gb} GB Internal Storage`);
      setVal("storageFreeVal", `Free: ${data.storage_free_gb} GB for Media`);
      setGauge("storageGaugeCircle", "storageGaugeText", sPct);

      // Ping
      setVal("pingVal", data.ping_ms > 0 ? `${data.ping_ms} ms` : "Direct Link");
    } else {
      dot.classList.add("offline");
      pill.textContent = "Device Offline";
      if (badge) {
        badge.textContent = "Offline • Disconnected";
        badge.className = "status-pill-badge badge-red";
      }

      if (btnWireless) {
        btnWireless.style.display = "none";
      }

      setVal("devModelName", "📱 No Device Connected");
      setVal("devOsVersion", "Connect phone via USB (to enable Wireless) or turn on Hotspot");
      setVal("targetIpText", "Target: Searching...");

      // Explicitly reset all card placeholders to clean neutral state
      setVal("batLevelVal", "--%");
      setVal("batDetailsVal", "-- V • -- °C");
      setVal("batStatusPill", "Offline");
      setVal("batSohVal", "Health: -- SOH • -- Cycles");
      setGauge("batGaugeCircle", "batGaugeText", 0);

      setVal("ramUsedVal", "-- GB");
      setVal("ramTotalVal", "Total: -- GB Physical RAM");
      setVal("ramFreeVal", "Available: -- GB");
      setGauge("ramGaugeCircle", "ramGaugeText", 0);

      setVal("storageUsedVal", "-- GB");
      setVal("storageTotalVal", "Total: -- GB Internal Storage");
      setVal("storageFreeVal", "Free: -- GB");
      setGauge("storageGaugeCircle", "storageGaugeText", 0);

      setVal("pingVal", "-- ms");
    }
  }

  function setVal(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function setGauge(circleId, textId, pct) {
    const circle = document.getElementById(circleId);
    const text = document.getElementById(textId);
    if (circle) circle.setAttribute("stroke-dasharray", `${pct}, 100`);
    if (text) text.textContent = `${pct}%`;
  }
}
