#!/bin/bash
set -e

echo "🧩 Uninstalling Migrator..."

# Uninstall using pip
pip3 uninstall -y migrator 2>/dev/null || true

echo "✅ Migrator uninstalled successfully!"
