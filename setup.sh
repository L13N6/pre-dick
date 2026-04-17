#!/bin/sh
# ================================================
# Predict Bot Setup Script
# Install dependency + awp-wallet + predict-agent
# Support: Alpine Linux & Ubuntu/Debian
# ================================================

set -e

echo "================================================"
echo " Predict Bot Setup"
echo "================================================"

# Detect OS
if [ -f /etc/alpine-release ]; then
    OS="alpine"
    echo "Detected: Alpine Linux"
elif [ -f /etc/debian_version ]; then
    OS="debian"
    echo "Detected: Ubuntu/Debian"
else
    OS="unknown"
    echo "Unknown OS, trying debian mode..."
    OS="debian"
fi

# Install dependencies
echo ""
echo "Step 1: Installing dependencies..."
if [ "$OS" = "alpine" ]; then
    apk add --no-cache nodejs npm git python3 python3-dev py3-pip curl bash
else
    apt-get update -qq
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y nodejs git python3 python3-pip python3-venv curl
fi

# Verify versions
echo ""
echo "Step 2: Verifying installations..."
node --version
npm --version
python3 --version
git --version

# Install awp-wallet
echo ""
echo "Step 3: Installing AWP Wallet..."
npm install -g https://github.com/awp-core/awp-wallet
awp-wallet --version

# Install predict-agent
echo ""
echo "Step 4: Installing Predict Agent..."
curl -sSL https://raw.githubusercontent.com/awp-worknet/prediction-skill/main/install.sh | sh
predict-agent --version

# Init wallet
echo ""
echo "Step 5: Initializing wallet..."
awp-wallet init || true

# Get wallet address
echo ""
echo "Step 6: Checking wallet address..."
WALLET_ADDR=$(awp-wallet receive | python3 -c "import sys,json; print(json.load(sys.stdin)['eoaAddress'])")
echo "Wallet agent address: $WALLET_ADDR"

echo ""
echo "================================================"
echo " Setup Complete!"
echo " Wallet agent: $WALLET_ADDR"
echo "================================================"
echo ""
echo "Next: jalankan run_predict.sh buat unlock + start loop"
echo ""
echo "Useful Commands:"
echo "  Wallet check : awp-wallet receive"
echo "  Run bot      : bash run_predict.sh"
echo "  Preflight    : predict-agent preflight"
