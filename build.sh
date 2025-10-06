#!/bin/bash
# Build script for LCSX using pyinstaller and staticx

# Check if virtual environment exists
if [ ! -d "venv" ]; then
  echo "Virtual environment 'venv' not found. Please create it first."
  exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Clean previous builds
rm -rf build dist lcsx.spec

# Run pyinstaller to create executable
pyinstaller --onefile --name lcsx \
  --paths . \
  --add-data "config:config" \
  --add-data "core:core" \
  --add-data "ui:ui" \
  --hidden-import psutil \
  __main__.py

# Check if pyinstaller succeeded
if [ $? -ne 0 ]; then
  echo "PyInstaller build failed"
  exit 1
fi

# Use staticx to create a static binary
if command -v staticx >/dev/null 2>&1; then
  staticx dist/lcsx dist/lcsx-static
  if [ $? -eq 0 ]; then
    echo "Staticx build succeeded: dist/lcsx-static"
  else
    echo "Staticx build failed"
    exit 1
  fi
else
  echo "staticx not found, skipping static build"
fi
