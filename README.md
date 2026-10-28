# Honor Ecosystem Suite (MagicOS PC Suite for Windows & Linux)

<p align="center">
  <img src="desktop/honor-hub.svg" width="128" height="128" alt="Honor Ecosystem Hub Logo" />
</p>

<p align="center">
  <b>Flagship Cross-Platform PC Suite for Honor & MagicOS Smartphones</b><br>
  120 FPS Motion UI • 70+ MB/s Fast Beam • Live RAM & Battery Telemetry • 1440p Screen Mirror • Xiaomi Flash Tool Style Debloater • Zero-Resource Architecture
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows%2011%20%7C%2010%20%7C%20Linux-blue?style=flat-square&logo=windows" alt="Platform Windows & Linux" />
  <img src="https://img.shields.io/badge/Motion%20UI-120%20FPS%20(Edge%20Chromium)-38bdf8?style=flat-square" alt="120 FPS Motion UI" />
  <img src="https://img.shields.io/badge/UI%20Engines-PyWebView%20%7C%20PySide6%20%7C%20GTK3-8a2be2?style=flat-square" alt="UI Engines" />
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python" alt="Python Version" />
  <img src="https://img.shields.io/badge/Android-12%20%7C%2014%20%7C%2015%20%7C%2016-3DDC84?style=flat-square&logo=android" alt="Android Compatibility" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License" />
</p>

---

## 🌐 Language Navigation
- [English](#-english)
- [O'zbekcha](#-ozbekcha)
- [Русский](#-русский)

---

<a name="english"></a>
## 🇬🇧 English

### Overview
**Honor Ecosystem Suite** is a modern, high-performance desktop application engineered to bring the seamless MagicOS ecosystem experience to **Windows 11/10** and **Linux** distributions (Ubuntu, Linux Mint, Debian, Fedora, Arch Linux).

Featuring the **Obsidian & MagicOS 9.0 Design System**, the Windows Flagship Edition is powered by a hardware-accelerated **120 FPS Motion Engine (PyWebView + Edge Chromium WebView2)** coupled with an asynchronous Python backend, delivering zero-stutter animations, magnetic card glows, and instant sub-millisecond tab switching.

Tested and optimized for **Honor 400 Pro**, **Magic6 / Magic7 Series**, and all devices running **MagicOS 7 / 8 / 9 (Android 12 to 16)**.

---

### ✨ Flagship Features

1. **120 FPS GPU-Accelerated Motion UI:**
   - **Obsidian Dark & Cyber-Cyan Aesthetics:** Modern glassmorphism, dynamic radial mouse-following card glow, and spring cubic-bezier transitions.
   - **Decoupled Architecture:** Asynchronous event bridge ensures large file transfers or network ADB delays never block UI frame rates.

2. **Live System Dashboard & Hardware Telemetry:**
   - **Real-Time RAM State:** True `/proc/meminfo` parser displaying Active/Used RAM, Buffers/Cache, and Available RAM with animated circular SVG gauges.
   - **Battery Health Diagnostics:** Live voltage (\(3.7\text{V} - 4.4\text{V}\)), temperature, charge status, and hardware cycle/SOH detection via Android `batteryproperties`.
   - **Internal Storage Meter:** High-speed UFS 4.0 storage usage breakdown.

3. **Ultra-Fast Wireless File Beam (70+ MB/s):**
   - High-throughput direct wireless ADB stream with live MB/s speedometer and audio-waveform equalizer visualizer.
   - **Apple Media Guard:** Automatic background conversion of iPhone `.heic` photos to `.jpg` and `.mov` videos to `.mp4` using hardware-accelerated `ffmpeg`.
   - **Instant Resume:** Resumes interrupted multi-gigabyte transfers without re-transmitting existing files.
   - **Android 16 MediaStore Auto-Indexer:** Automatically invokes `scan_volume` so photos and 4K videos appear in the phone's native Gallery immediately without phone reboots.
   - **Flat Timeline Hierarchy:** Intelligently saves to `/sdcard/DCIM/Camera/` to preserve native MagicOS chronological timeline sorting.

4. **Xiaomi Flash Tool Style Debloater & App Manager:**
   - 360+ categorized package database covering System Bloatware, Carrier apps, Analytics, Honor Cloud, and User apps.
   - Color-coded safety tags: `Safe to Remove` (Green), `Caution` (Yellow), and `Dangerous/Essential` (Red).
   - 5 Quick-Filter tabs: All, Recommended (Bloat), System Apps, User Installed, and Recycle Bin.
   - Safe uninstallation (`pm uninstall -k --user 0`) with zero-risk safe mode.
   - **1-Click Restore:** Restores uninstalled packages (`cmd package install-existing`) at any time directly from the Recycle Bin tab.

5. **Wireless Multi-Screen Collaboration (Screen Mirror):**
   - Ultra low-latency 1440p / 1080p / 720p 60 FPS screen mirror and bi-directional audio bridge powered by `scrcpy`.
   - Smartphone display turn-off mode to prevent heat and save battery during screen mirroring.
   - Shared clipboard between PC and Honor device.

6. **Remote Device File Explorer:**
   - Browse smartphone storage over ADB with double-click directory navigation, search, and upload/download with glassmorphic toast notifications.

7. **Zero-Resource Background Guarantee:**
   - No persistent daemons, background polling loops, or memory leaks. Consumes **0% CPU and 0 MB RAM** when idle or closed.

---

### 🚀 Installation & Quick Start

#### 🪟 Windows 11 / 10 Installation (Recommended)
```powershell
git clone https://github.com/boburhasanov/honor-ecosystem-suite.git
cd honor-ecosystem-suite
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows.ps1
```
*Installs required dependencies (`pywebview`, `PySide6`), verifies `adb`, `scrcpy`, `ffmpeg`, and creates the **Honor Ecosystem Hub** desktop shortcut with the flagship 3D icon.*

To launch manually via terminal:
```powershell
# 120 FPS Flagship Motion Edition (Recommended)
python honor-hub-motion.py

# Native Qt6 Desktop Edition
python honor-control-center.py
```

To build a standalone Windows binary:
```powershell
python scripts\build_windows_dist.py
```

---

#### 🐧 Linux (Ubuntu / Mint / Debian / Arch / Fedora)

#### Option 1: Automated 1-Click Installer (Recommended)
```bash
git clone https://github.com/boburhasanov/honor-ecosystem-suite.git
cd honor-ecosystem-suite
chmod +x install.sh
sudo ./install.sh
```

#### Option 2: Portable Mode (Run without installation)
```bash
git clone https://github.com/boburhasanov/honor-ecosystem-suite.git
cd honor-ecosystem-suite
./bin/honor-control-center
```

---

<a name="ozbekcha"></a>
## 🇺🇿 O'zbekcha

### Umumiy Ma'lumot
**Honor Ecosystem Suite** — Honor va MagicOS smartfonlarini **Windows 11/10** va **Linux** (Ubuntu, Linux Mint, Debian, Arch, Fedora) bilan mukammal darajada birlashtiruvchi zamonaviy flagman grafik dasturi.

Ushbu dastur **120 FPS Motion UI (Edge Chromium WebView2)** va tezyurar asinxron Python yadrosi orqali ishlab, qotishlarsiz silliq animatsiyalar, magnitli neon yorug'lik effektlari va zumda ishlovchi ilovalar boshqaruvini taqdim etadi.

Honor 400 Pro, Magic6, Magic7 va boshqa MagicOS 7/8/9 (Android 12-16) qurilmalarida sinovdan o'tgan.

---

### ✨ Asosiy Imkoniyatlar

1. **120 FPS GPU-Tezlatkichli Motion UI:**
   - Obsidian Dark va Cyber-Cyan dizayn tizimi, magnitli kursor nuri, silliq o'tishlar.
   - Asinxron arxitektura: Fayl ko'chirish yoki tarmoq sekinligi interfeysni aslo qotirmaydi.

2. **Jonli Telemetriya va Dashboard:**
   - **Haqiqiy RAM Holati:** Smartfondagi `/proc/meminfo` drayveridan to'g'ridan-to'g'ri olingan Active, Cache va Bo'sh RAM ko'rsatkichlari.
   - **Batareya Diagnostikasi:** Kuchlanish (\(3.7\text{V} - 4.4\text{V}\)), harorat, zaryadlash holati va `batteryproperties` orqali zaryadlash sikllari / SOH salomatligi.
   - **Xotira Holati:** Telefon ichki xotirasining real-vaqtdagi bandligi.

3. **Ultra-Tezkor Simsiz Fayl Uzatish (70+ MB/s Fast Beam):**
   - Yuqori tezlikdagi simsiz ADB uzatish, jonli audio-to'lqinli visualizer spidometri.
   - **Apple Media Guard:** iPhone rasmlarini (`.heic`) avtomatik `.jpg` ga, videolarni (`.mov`) apparat tezlatkichli `ffmpeg` bilan `.mp4` ga o'girish.
   - **Instant Resume:** Tarmoq uzilsa ham, to'xtagan joyidan davom ettirish.
   - **Android 16 MediaStore Sinxronizatsiyasi:** Yuklangan medialarni telefonni o'chirib-yoqmasdan darhol "Galereya"da aks ettirish.
   - **To'g'ri Xronologiya:** Medialarni `/sdcard/DCIM/Camera/` papkasiga joylashtirib, sana tartibini saqlash.

4. **Xiaomi Flash Tool Uslubidagi Dasturlarni Tozalovchi (Debloater):**
   - 360+ tizim va foydalanuvchi ilovalarining xavfsizlik reytingi (Xavfsiz, Ehtiyotkorlik, Xavfli).
   - 5 ta qulay filtr: Hammasi, Tavsiya etilgan (Bloatware), Tizim, O'rnatilgan va Chiqindilar qutisi (Recycle Bin).
   - Bir vaqtning o'zida bir nechta dasturni xavfsiz o'chirish (`pm uninstall -k --user 0`).
   - **1-Bosishda Qayta Tiklash:** O'chirilgan dasturlarni 1 ta tugma orqali asliga qaytarish (`cmd package install-existing`).

5. **Simsiz Ekranni Boshqarish (Screen Mirror):**
   - 1440p / 1080p / 720p 60 FPS past kechikishli ekran oynasi (`scrcpy` negizida).
   - Telefon qizib ketmasligi uchun oyna paytida telefon ekranini o'chirish imkoniyati.
   - Kompyuter va telefon o'rtasida umumiy nusxalash buferi (clipboard).

6. **Masofaviy Fayl Menejeri (File Explorer):**
   - Telefon ichki xotirasini kompyuterdan bevosita ko'rish, fayllarni yuklash va tushirib olish.

7. **Nol Resurs Siyosati (Zero-Resource Guarantee):**
   - Fondagi keraksiz xizmatlarsiz. Dastur yopilganda CPU 0%, RAM 0 MB.

---

### 🚀 O'rnatish

#### 🪟 Windows 11 / 10 (Tavsiya etiladi)
```powershell
git clone https://github.com/boburhasanov/honor-ecosystem-suite.git
cd honor-ecosystem-suite
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows.ps1
```
*Ish stolida flagman 3D ikonka bilan **"Honor Ecosystem Hub"** yorlig'ini yaratadi.*

---

<a name="русский"></a>
## 🇷🇺 Русский

### Обзор
**Honor Ecosystem Suite** — флагманское кроссплатформенное приложение для бесшовной интеграции смартфонов Honor под управлением MagicOS с **Windows 11/10** и **Linux** (Ubuntu, Mint, Debian, Arch, Fedora).

Флагманская версия для Windows оснащена аппаратным **120 FPS Motion UI (Edge Chromium WebView2)** и асинхронным ядром Python, обеспечивая плавность работы без задержек и подвисаний.

---

### 🚀 Быстрый запуск на Windows 11 / 10
```powershell
git clone https://github.com/boburhasanov/honor-ecosystem-suite.git
cd honor-ecosystem-suite
powershell -ExecutionPolicy Bypass -File .\scripts\install_windows.ps1
```

---

## 📄 License
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

## 👤 Author
Developed with ❤️ by **Bobur Hasanov** ([@boburhasanov](https://github.com/boburhasanov)).
