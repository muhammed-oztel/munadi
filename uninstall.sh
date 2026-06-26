#!/bin/bash
set -e

sudo rm -rf /usr/local/share/munadi
sudo rm -f /usr/share/applications/com.mfo.munadi.desktop
sudo update-desktop-database

echo "Munadî kaldırıldı."