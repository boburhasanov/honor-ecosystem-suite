#!/usr/bin/env bash
# ==============================================================================
# Honor Ecosystem Suite for Linux - Automated Installer
# MagicOS Wireless Hub, Fast Beam, Real-Time Telemetry & Debloater
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "==================================================================="
echo "           Honor Ecosystem Suite for Linux - Installer             "
echo "        MagicOS 9.0 Wireless Control Center & Debloat Suite       "
echo "==================================================================="
echo -e "${NC}"

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Please run this installer with root privileges:${NC}"
  echo "    sudo ./install.sh"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}[*] Checking required system dependencies...${NC}"
MISSING_PKGS=()

command -v adb >/dev/null 2>&1 || MISSING_PKGS+=("adb")
command -v scrcpy >/dev/null 2>&1 || MISSING_PKGS+=("scrcpy")
command -v python3 >/dev/null 2>&1 || MISSING_PKGS+=("python3")
command -v ffmpeg >/dev/null 2>&1 || MISSING_PKGS+=("ffmpeg")

# Check Python GObject introspection
if ! python3 -c "import gi; gi.require_version('Gtk', '3.0')" >/dev/null 2>&1; then
    MISSING_PKGS+=("python3-gi" "gir1.2-gtk-3.0")
fi

if [ ${#MISSING_PKGS[@]} -gt 0 ]; then
    echo -e "${YELLOW}[!] Missing dependencies: ${MISSING_PKGS[*]}${NC}"
    if command -v apt-get >/dev/null 2>&1; then
        echo -e "${BLUE}[*] Installing dependencies via apt...${NC}"
        apt-get update -qq
        apt-get install -y "${MISSING_PKGS[@]}"
    elif command -v dnf >/dev/null 2>&1; then
        echo -e "${BLUE}[*] Installing dependencies via dnf...${NC}"
        dnf install -y "${MISSING_PKGS[@]}"
    elif command -v pacman >/dev/null 2>&1; then
        echo -e "${BLUE}[*] Installing dependencies via pacman...${NC}"
        pacman -S --noconfirm "${MISSING_PKGS[@]}"
    else
        echo -e "${RED}[!] Package manager not recognized. Please manually install: ${MISSING_PKGS[*]}${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}[✓] All core dependencies verified.${NC}"
fi

echo -e "${BLUE}[*] Installing Honor Ecosystem Suite to /usr/local...${NC}"

# Create directories
mkdir -p /usr/local/bin
mkdir -p /usr/local/lib/honor-suite
mkdir -p /usr/share/applications
mkdir -p /usr/share/icons/hicolor/scalable/apps
mkdir -p /usr/share/pixmaps

# Copy files
rm -rf /usr/local/lib/honor-suite/*
cp -r "${SCRIPT_DIR}/lib/honor-suite/"* /usr/local/lib/honor-suite/
cp "${SCRIPT_DIR}/bin/honor-control-center" /usr/local/bin/honor-control-center
chmod 755 /usr/local/bin/honor-control-center

# Copy desktop and icon assets
cp "${SCRIPT_DIR}/desktop/honor-control-center.desktop" /usr/share/applications/
cp "${SCRIPT_DIR}/desktop/honor-hub.svg" /usr/share/icons/hicolor/scalable/apps/
cp "${SCRIPT_DIR}/desktop/honor-hub.svg" /usr/share/pixmaps/honor-hub.svg

# Install udev auto-wifi trigger
cp "${SCRIPT_DIR}/bin/honor-auto-wifi" /usr/local/bin/honor-auto-wifi
chmod 755 /usr/local/bin/honor-auto-wifi
if [ -d "${SCRIPT_DIR}/udev" ]; then
    cp "${SCRIPT_DIR}/udev/99-honor-auto-wifi.rules" /etc/udev/rules.d/
    if command -v udevadm >/dev/null 2>&1; then
        udevadm control --reload-rules || true
    fi
fi

# Update desktop cache
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi

echo -e "${GREEN}${BOLD}[✓] Honor Ecosystem Suite has been successfully installed!${NC}"
echo ""
echo -e "You can launch it from:"
echo -e "  1. Applications Menu -> ${BOLD}Honor Ecosystem Hub${NC}"
echo -e "  2. Terminal -> ${CYAN}honor-control-center${NC}"
echo ""
