/**
 * Live Telemetry & Hardware Gauges Controller
 */

export function initTelemetry() {
  window.refreshTelemetry = async function () {
    if (!window.pywebview) return;
    try {
      const data = await window.pywebview.api.get_telemetry();
      updateTelemetryView(data);
    } catch (err) {
      console.error("Telemetry error:", err);
    }
  };

  function updateTelemetryView(data) {
    const isConn = data.connected;
    const dot = document.getElementById("statusDot");
    const pill = document.getElementById("devicePillText");
    const badge = document.getElementById("connectionBadge");

    if (isConn) {
      dot.classList.remove("offline");
      pill.textContent = data.model || "Honor Device (Connected)";
      if (badge) {
        badge.textContent = "Online • Connected";
        badge.className = "status-pill-badge badge-emerald";
      }

      const mName = document.getElementById("devModelName");
      if (mName) mName.textContent = "📱 " + (data.model || "Honor 400 Pro");

      const osVer = document.getElementById("devOsVersion");
      if (osVer) osVer.textContent = "MagicOS Suite • " + (data.android || "Android 16");

      const tIp = document.getElementById("targetIpText");
      if (tIp) tIp.textContent = "Endpoint: " + data.target;

      // Battery Gauge
      const bLvl = data.battery_level || 0;
      setVal("batLevelVal", `${bLvl}%`);
      setVal("batDetailsVal", `${data.battery_voltage_v}V • ${data.battery_temp_c}°C`);
      setVal("batStatusPill", data.battery_status || "Discharging");
      setVal("batSohVal", `Health: ${data.battery_soh}% SOH • ${data.battery_cycles} Charge Cycles`);
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
      setVal("storageTotalVal", `Total: ${data.storage_total_gb} GB Internal UFS 4.0`);
      setVal("storageFreeVal", `Free: ${data.storage_free_gb} GB for Media`);
      setGauge("storageGaugeCircle", "storageGaugeText", sPct);

      // Ping
      setVal("pingVal", data.ping_ms > 0 ? `${data.ping_ms} ms` : "Direct USB");
    } else {
      dot.classList.add("offline");
      pill.textContent = "Device Offline";
      if (badge) {
        badge.textContent = "Offline • Disconnected";
        badge.className = "status-pill-badge badge-red";
      }
      setVal("devModelName", "📱 Device Offline");
      setVal("devOsVersion", "Connect phone via USB or turn on Wireless Debugging");
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
