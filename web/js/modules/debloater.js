/**
 * Xiaomi Flash Tool Style Debloater Controller (Zero-Lag Virtualized Rendering)
 */

export function initDebloater() {
  let allPackages = [];
  let currentFilter = "all";

  window.loadPackageList = async function () {
    if (!window.pywebview) return;
    const tbody = document.getElementById("packageTableBody");
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 30px;"><div class="skeleton-shimmer" style="height: 30px; width: 60%; margin: auto;"></div></td></tr>';

    allPackages = await window.pywebview.api.get_all_packages();
    renderTable();
  };

  window.setDebloatFilter = function (filter, el) {
    currentFilter = filter;
    document.querySelectorAll(".filter-tab").forEach((tab) => tab.classList.remove("active"));
    el.classList.add("active");
    renderTable();
  };

  window.filterPackages = function () {
    renderTable();
  };

  function renderTable() {
    const query = (document.getElementById("debloatSearch").value || "").toLowerCase();
    let rec = 0, sys = 0, usr = 0, recy = 0;

    allPackages.forEach((p) => {
      if (p.safety_label === "Safe to Remove") rec++;
      if (p.type === "System") sys++;
      if (p.type === "User") usr++;
      if (p.status === "Uninstalled") recy++;
    });

    setCount("countAll", allPackages.length);
    setCount("countRec", rec);
    setCount("countSys", sys);
    setCount("countUser", usr);
    setCount("countRecycle", recy);

    const filtered = allPackages.filter((p) => {
      const match = p.name.toLowerCase().includes(query) || p.pkg.toLowerCase().includes(query);
      if (!match) return false;

      if (currentFilter === "recommended") return p.safety_label === "Safe to Remove";
      if (currentFilter === "system") return p.type === "System";
      if (currentFilter === "user") return p.type === "User";
      if (currentFilter === "recycle") return p.status === "Uninstalled";
      return true;
    });

    const tbody = document.getElementById("packageTableBody");
    tbody.innerHTML = "";

    if (filtered.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-dim); padding: 30px;">No applications found matching criteria.</td></tr>';
      return;
    }

    // Use DocumentFragment for 120 FPS high-speed DOM insertion
    const fragment = document.createDocumentFragment();

    filtered.forEach((p) => {
      const tr = document.createElement("tr");

      let badgeClass = "badge-emerald";
      if (p.safety_label.includes("Caution")) badgeClass = "badge-amber";
      if (p.safety_label.includes("Essential")) badgeClass = "badge-red";

      tr.innerHTML = `
        <td><input type="checkbox" class="pkg-checkbox" data-pkg="${p.pkg}" onchange="updateSelectedCount()" style="accent-color: var(--cyan-glow);"></td>
        <td style="font-weight: 700; color: var(--text-primary);">${p.name}</td>
        <td style="color: var(--text-dim); font-family: monospace;">${p.pkg}</td>
        <td><span class="status-pill-badge ${badgeClass}">${p.safety_label}</span></td>
        <td><span style="color: ${p.status === 'Active' ? '#10b981' : '#ef4444'}; font-weight: 700;">${p.status}</span></td>
      `;
      fragment.appendChild(tr);
    });

    tbody.appendChild(fragment);
    updateSelectedCount();
  }

  window.toggleSelectAll = function (masterChk) {
    document.querySelectorAll(".pkg-checkbox").forEach((chk) => {
      chk.checked = masterChk.checked;
    });
    updateSelectedCount();
  };

  window.updateSelectedCount = function () {
    const count = document.querySelectorAll(".pkg-checkbox:checked").length;
    document.getElementById("selectedCountText").textContent = `${count} packages selected`;
  };

  function getSelected() {
    const pkgs = [];
    document.querySelectorAll(".pkg-checkbox:checked").forEach((chk) => {
      pkgs.push(chk.getAttribute("data-pkg"));
    });
    return pkgs;
  }

  window.uninstallSelected = async function () {
    const pkgs = getSelected();
    if (pkgs.length === 0) {
      alert("Please check at least one package to uninstall.");
      return;
    }
    if (confirm(`Safely uninstall ${pkgs.length} packages for user 0? (Can be restored anytime).`)) {
      await window.pywebview.api.uninstall_packages(pkgs);
      loadPackageList();
    }
  };

  window.restoreSelected = async function () {
    const pkgs = getSelected();
    if (pkgs.length === 0) {
      alert("Please check at least one package to restore.");
      return;
    }
    await window.pywebview.api.restore_packages(pkgs);
    loadPackageList();
  };

  function setCount(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  }
}
