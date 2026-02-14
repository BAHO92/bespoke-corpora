#!/usr/bin/env bash
set -e

# Bespoke Corpora — one-command setup & run

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found. Install Python 3.10+ first.${NC}"
    exit 1
fi

# Check Python version >= 3.10
PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo -e "${RED}Error: Python 3.10+ required (found $PY_VERSION).${NC}"
    exit 1
fi

# Resolve script directory (works even when called from elsewhere)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create venv if missing
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate
source .venv/bin/activate

# Install dependencies (quietly)
pip install -q -r requirements.txt

echo -e "${GREEN}Starting Bespoke Corpora...${NC}"
echo "http://127.0.0.1:5222"
echo ""

python3 app.py
