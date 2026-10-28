# Honor Ecosystem Suite — Agent Directive & System Invariants

## 🌟 Brand & Product North Star
**Honor Ecosystem Suite (MagicOS PC Suite)** is a modern desktop integration system bridging Windows/Linux PCs with Honor and Android smartphones.

### System Invariants
1. **Zero-Resource Architecture**:
   - When idle or closed, the suite must consume 0% CPU and 0 MB RAM.
   - No persistent background daemons, orphan sub-processes, or memory leaks.
2. **Modular Decoupling (3-Layer DOE)**:
   - **Directive Layer**: Declarative Markdown specifications (`.agent/`, `directives/`).
   - **Domain / Logic Layer**: Pure Python services (`core/`), completely isolated from UI code.
   - **Presentation Layer**: PySide6 (Qt 6) widgets (`ui/`), driven strictly by signals and events.
3. **Safe Operation**:
   - Debloating operations only invoke `pm uninstall -k --user 0`, preserving APKs in `/system` so they can always be restored via `cmd package install-existing` without factory resets.
4. **Resilient Data Transfer**:
   - Fast Beam implements true byte tracking, instant resume (skips matching file sizes), and triggers MediaStore re-indexing on completion.

## 🎨 Design Tokens (MagicOS Dark 9.0)
- **Background (Obsidian)**: `#0b0f19`
- **Sidebar (Deep Slate)**: `#0f172a` (Border `#1e293b`)
- **Card Background**: `#151c2c` (Border `#232f46`, Radius 14px)
- **Primary Accent (Honor Cyan)**: `#38bdf8`
- **Success / Optimal (Emerald)**: `#10b981`
- **Warning / Caution (Amber)**: `#f59e0b`
- **Danger / Critical (Red)**: `#ef4444`
- **Primary Text**: `#f8fafc`
- **Muted Text**: `#94a3b8`
