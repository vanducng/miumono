#!/bin/bash
# Install script for miu-code
# Usage: curl -LsSf https://raw.githubusercontent.com/vanducng/miumono/main/scripts/install.sh | bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Installing miu-code..."

# Detect OS
OS=$(uname -s)
case "$OS" in
    Linux*)  PLATFORM="linux" ;;
    Darwin*) PLATFORM="macos" ;;
    *)
        echo -e "${RED}Error: Unsupported OS: $OS${NC}"
        echo "For Windows, use PowerShell:"
        echo "  irm https://raw.githubusercontent.com/vanducng/miumono/main/scripts/install.ps1 | iex"
        exit 1
        ;;
esac

# Check for uv
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}uv not found. Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install miu-code
echo "Installing miu-code with uv..."
uv tool install miu-code

# Verify installation
if command -v miu &> /dev/null; then
    echo -e "${GREEN}miu-code installed successfully!${NC}"
    echo ""
    echo "Quick start:"
    echo "  miu --help              # Show help"
    echo "  miu \"read README.md\"    # Run a query"
    echo "  miu                     # Start interactive mode"
else
    echo -e "${YELLOW}Installation complete, but 'miu' not found in PATH.${NC}"
    echo ""
    echo "Add this to your shell profile (~/.bashrc, ~/.zshrc, etc.):"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Then restart your terminal or run:"
    echo "  source ~/.bashrc  # or ~/.zshrc"
fi
