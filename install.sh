#!/bin/bash
set -e

INSTALL_DIR="/usr/local/share/munadi"

sudo mkdir -p "$INSTALL_DIR/resources"
sudo cp munadi.py "$INSTALL_DIR/"
sudo cp resources/ezan_istanbul_2026.json "$INSTALL_DIR/resources/"
sudo cp com.mfo.munadi.desktop /usr/share/applications/

echo "Kurulum tamamlandı. Uygulama menüden açılabilir."