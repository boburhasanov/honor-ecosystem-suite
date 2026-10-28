# ==============================================================================
# Honor Ecosystem Suite - Automated Windows Installer & Environment Setup
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = "Continue"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Honor Ecosystem Suite - Windows Installation Wizard" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Determine Project Directory
$ProjectDir = (Resolve-Path "$PSScriptRoot\..").Path
Write-Host "[*] Project Directory: $ProjectDir" -ForegroundColor Gray

# 2. Check Python
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    Write-Host "[!] Python is not found in PATH! Please install Python from https://python.org" -ForegroundColor Red
    Exit 1
}
$PyVer = python -c "import sys; print(sys.version.split()[0])"
Write-Host "[*] Python Version: $PyVer (OK)" -ForegroundColor Green

# 3. Check / Install PySide6
Write-Host "[*] Verifying PySide6 (Qt 6)..." -ForegroundColor Yellow
$HasPySide6 = python -c "import PySide6; print('OK')"
if ($HasPySide6 -notmatch "OK") {
    Write-Host "[*] Installing PySide6..." -ForegroundColor Yellow
    pip install PySide6
} else {
    Write-Host "[OK] PySide6 is already installed!" -ForegroundColor Green
}

# 4. Check External Binaries (ADB, Scrcpy, FFmpeg)
$Binaries = @("adb", "scrcpy", "ffmpeg")
foreach ($bin in $Binaries) {
    $found = Get-Command $bin -ErrorAction SilentlyContinue
    if (-not $found) {
        Write-Host "[!] $bin is not in PATH. Attempting installation via winget..." -ForegroundColor Yellow
        if ($bin -eq "adb") {
            winget install --id Google.PlatformTools --accept-source-agreements --accept-package-agreements
        } elseif ($bin -eq "scrcpy") {
            winget install --id Genymobile.scrcpy --accept-source-agreements --accept-package-agreements
        } elseif ($bin -eq "ffmpeg") {
            winget install --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
        }
    } else {
        Write-Host "[OK] Found $bin at $($found.Source)" -ForegroundColor Green
    }
}

# 5. Create Desktop Shortcut (Using pythonw.exe for clean zero-console execution)
Write-Host "[*] Creating Desktop and Start Menu Shortcuts..." -ForegroundColor Yellow

$PythonwCmd = (Get-Command pythonw -ErrorAction SilentlyContinue).Source
if (-not $PythonwCmd) {
    $PythonwCmd = $PythonCmd.Source
}

$WScriptShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop)
$ShortcutPath = Join-Path $DesktopPath "Honor Ecosystem Hub.lnk"
$StartMenuPath = Join-Path ([System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Programs)) "Honor Ecosystem Hub.lnk"

foreach ($linkPath in @($ShortcutPath, $StartMenuPath)) {
    $Shortcut = $WScriptShell.CreateShortcut($linkPath)
    $Shortcut.TargetPath = $PythonwCmd
    $Shortcut.Arguments = "`"$ProjectDir\honor-control-center.py`""
    $Shortcut.WorkingDirectory = $ProjectDir
    $Shortcut.Description = "Honor Ecosystem Suite - MagicOS PC Suite for Android"
    $Shortcut.Save()
}

Write-Host "[OK] Desktop shortcut created at: $ShortcutPath" -ForegroundColor Green
Write-Host "[OK] Start Menu shortcut created!" -ForegroundColor Green

# 6. Create root launcher batch file for terminal access
$BatContent = "@echo off`r`nstart `"`" `"$PythonwCmd`" `"$ProjectDir\honor-control-center.py`" %*`r`n"
[System.IO.File]::WriteAllText("$ProjectDir\honor-hub.bat", $BatContent)
Write-Host "[OK] honor-hub.bat created for 1-click execution!" -ForegroundColor Green

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Installation Complete! You can now launch the app from:   " -ForegroundColor Green
Write-Host "  1. Desktop shortcut: 'Honor Ecosystem Hub'               " -ForegroundColor White
Write-Host "  2. Terminal command: python honor-control-center.py      " -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
