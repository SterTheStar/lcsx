#!/bin/bash
# Build script for LCSX using pyinstaller and staticx (isolated venv, no preinstalled pip)

set -e

VENV_DIR=".venv"

# Clean previous builds
rm -rf build dist lcsx.spec "$VENV_DIR"

echo "[*] Creating venv without pip..."
python3 -m venv "$VENV_DIR" --without-pip

# Download get-pip.py
echo "[*] Downloading get-pip.py..."
curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py

# Install pip into the venv
echo "[*] Installing pip inside venv..."
"$VENV_DIR/bin/python" get-pip.py
rm get-pip.py

# Install build dependencies
echo "[*] Installing pyinstaller, psutil, and staticx..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install pyinstaller psutil staticx

# Run pyinstaller from the venv
echo "[*] Running PyInstaller..."
"$VENV_DIR/bin/pyinstaller" --onefile --name lcsx \
  --paths . \
  --add-data "config:config" \
  --add-data "core:core" \
  --add-data "ui:ui" \
  --hidden-import psutil \
  __main__.py

# Check if pyinstaller succeeded
if [ $? -ne 0 ]; then
  echo "[!] PyInstaller build failed"
  exit 1
fi

# Use staticx if available
if "$VENV_DIR/bin/staticx" --version >/dev/null 2>&1; then
  echo "[*] Creating static binary with staticx..."
  "$VENV_DIR/bin/staticx" dist/lcsx dist/lcsx-static
  echo "[+] Staticx build succeeded: dist/lcsx-static"
else
  echo "[!] staticx not found, skipping static build"
fi

echo "[✓] Build complete."
