# Directives: Honor Suite Architecture & Quality Rules

## 1. Domain Service Isolation
- All ADB command executions must flow through `AdbService`.
- No UI component is allowed to directly call `subprocess.run(["adb", ...])`.
- Domain services return structured typed dataclasses or dictionaries, not raw unparsed command output.

## 2. Multi-Threading & UI Responsiveness
- All blocking calls (file transfer, scrcpy launch, package query) must run in `QThread` or daemon worker threads.
- Worker threads communicate with UI exclusively via PySide6 `Signal`.
- Never block the Qt Main Event Loop.

## 3. Cross-Platform Path Invariants
- All file paths must use `pathlib.Path` or `os.path.normpath`.
- Remote Android paths strictly use POSIX slashes (`/`), while local paths respect Windows `\\`.
