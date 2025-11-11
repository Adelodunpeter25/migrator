#!/bin/bash
set -e

echo "🧩 Installing Migrator..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required. Found: $PYTHON_VERSION"
    exit 1
fi

# Install using pip
echo "📦 Installing migrator..."
pip3 install --user git+https://github.com/Adelodunpeter25/migrator.git

echo "✅ Migrator installed successfully!"
echo ""
echo "📖 Quick start:"
echo "  1. Set DATABASE_URL in .env file"
echo "  2. Run: migrator init"
echo "  3. Run: migrator makemigrations \"your message\""
echo "  4. Run: migrator migrate"
echo ""
echo "For more info: https://github.com/Adelodunpeter25/migrator"
