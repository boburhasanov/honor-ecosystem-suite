#!/usr/bin/env bash
# ==============================================================================
# Honor Ecosystem Suite for Linux - Uninstaller
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Please run with root privileges:${NC}"
  echo "    sudo ./uninstall.sh"
  exit 1
fi

echo -e "${BLUE}[*] Removing Honor Ecosystem Suite from system...${NC}"

rm -f /usr/local/bin/honor-control-center
rm -rf /usr/local/lib/honor-suite
rm -f /usr/share/applications/honor-control-center.desktop
rm -f /usr/share/icons/hicolor/scalable/apps/honor-hub.svg
rm -f /usr/share/pixmaps/honor-hub.svg

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi

echo -e "${GREEN}${BOLD}[✓] Honor Ecosystem Suite has been completely uninstalled.${NC}"
