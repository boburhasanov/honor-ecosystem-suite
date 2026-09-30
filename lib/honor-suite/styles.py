"""
MagicOS Design-First Stylesheet for Honor Suite
Complies with modern MagicOS/HarmonyOS/Apple Design tokens:
Obsidian palette (#0b0f19), slate cards (#151c2c), Honor Cyan (#38bdf8),
Emerald (#10b981), Amber (#f59e0b), high-contrast labels, anti-ghosting.
"""

MAGIC_OS_CSS = """
window {
    background-color: #0b0f19;
    color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Ubuntu", sans-serif;
}

/* Sidebar Styling */
.sidebar {
    background-color: #0f172a;
    border-right: 1px solid #1e293b;
    padding: 12px 8px;
}

.sidebar-title {
    color: #38bdf8;
    font-size: 1.1em;
    font-weight: 800;
    padding: 12px 10px 4px 10px;
    letter-spacing: 0.5px;
}

.sidebar-subtitle {
    color: #64748b;
    font-size: 0.8em;
    font-weight: 500;
    padding: 0 10px 14px 10px;
}

.sidebar-btn {
    background: transparent;
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    color: #94a3b8;
    font-weight: 600;
    font-size: 0.95em;
    transition: all 150ms ease;
    margin-bottom: 4px;
}

.sidebar-btn:hover {
    background-color: #1e293b;
    color: #f8fafc;
}

.sidebar-btn:checked, .sidebar-btn.active {
    background-color: #1e293b;
    color: #38bdf8;
    border-left: 3px solid #38bdf8;
    font-weight: 700;
}

/* Card Geometry */
.card {
    background-color: #151c2c;
    border: 1px solid #232f46;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 12px;
}

.card-title {
    color: #f8fafc;
    font-size: 1.1em;
    font-weight: 700;
}

.card-desc {
    color: #94a3b8;
    font-size: 0.88em;
}

.text-white {
    color: #f8fafc;
}

.text-muted {
    color: #94a3b8;
}

.text-cyan {
    color: #38bdf8;
}

/* Metrics and Gauges */
.metric-value {
    color: #f8fafc;
    font-size: 2em;
    font-weight: 800;
}

.metric-label {
    color: #64748b;
    font-size: 0.82em;
    font-weight: 600;
    letter-spacing: 0.8px;
}

.badge-active {
    background-color: #10b981;
    color: #ffffff;
    font-weight: 700;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 0.8em;
}

.badge-cyan {
    background-color: #0284c7;
    color: #ffffff;
    font-weight: 700;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 0.8em;
}

.badge-amber {
    background-color: #d97706;
    color: #ffffff;
    font-weight: 700;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 0.8em;
}

.badge-danger {
    background-color: #dc2626;
    color: #ffffff;
    font-weight: 700;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 0.8em;
}

.badge-muted {
    background-color: #334155;
    color: #94a3b8;
    font-weight: 700;
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 0.8em;
}

/* Buttons */
.btn-primary {
    background-image: linear-gradient(135deg, #0284c7, #2563eb);
    color: #ffffff;
    font-weight: 700;
    border-radius: 10px;
    padding: 9px 18px;
    border: none;
}
.btn-primary:hover {
    background-image: linear-gradient(135deg, #38bdf8, #0284c7);
}

.btn-success {
    background-image: linear-gradient(135deg, #059669, #10b981);
    color: #ffffff;
    font-weight: 700;
    border-radius: 10px;
    padding: 9px 18px;
    border: none;
}
.btn-success:hover {
    background-image: linear-gradient(135deg, #10b981, #34d399);
}

.btn-secondary {
    background-color: #1e293b;
    color: #f8fafc;
    font-weight: 600;
    border-radius: 10px;
    padding: 8px 14px;
    border: 1px solid #334155;
}
.btn-secondary:hover {
    background-color: #334155;
    color: #ffffff;
}

.btn-danger {
    background-image: linear-gradient(135deg, #b91c1c, #dc2626);
    color: #ffffff;
    font-weight: 700;
    border-radius: 10px;
    padding: 8px 14px;
    border: none;
}

/* Progress bar */
progressbar progress {
    background-image: linear-gradient(90deg, #38bdf8, #2563eb);
    border-radius: 6px;
}
progressbar trough {
    background-color: #1e293b;
    border-radius: 6px;
    min-height: 10px;
}

/* File Tree / List */
treeview.view {
    background-color: #111827;
    color: #f8fafc;
    border: 1px solid #232f46;
    border-radius: 8px;
}

treeview.view:selected {
    background-color: #0284c7;
    color: #ffffff;
}

treeview.view header button {
    background-color: #1e293b;
    color: #94a3b8;
    font-weight: 700;
    border: none;
    border-bottom: 1px solid #334155;
    padding: 6px;
}

entry.search-input {
    background-color: #111827;
    color: #f8fafc;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px 12px;
}
entry.search-input:focus {
    border-color: #38bdf8;
}

.tab-btn {
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: 600;
    font-size: 0.88em;
}

infobar {
    background-color: #1e293b;
    border-bottom: 1px solid #334155;
    color: #f8fafc;
    padding: 6px 14px;
}
infobar label {
    font-size: 13px;
    font-weight: 600;
    color: #38bdf8;
}
"""
