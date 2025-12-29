# Install script for miu-code (Windows)
# Usage: irm https://raw.githubusercontent.com/vanducng/miumono/main/scripts/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "Installing miu-code..." -ForegroundColor Cyan

# Check for uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv not found. Installing uv..." -ForegroundColor Yellow
    irm https://astral.sh/uv/install.ps1 | iex

    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

# Install miu-code
Write-Host "Installing miu-code with uv..." -ForegroundColor Cyan
uv tool install miu-code

# Verify installation
if (Get-Command miu -ErrorAction SilentlyContinue) {
    Write-Host "miu-code installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Quick start:"
    Write-Host "  miu --help              # Show help"
    Write-Host '  miu "read README.md"    # Run a query'
    Write-Host "  miu                     # Start interactive mode"
} else {
    Write-Host "Installation complete. Restart your terminal to use 'miu'." -ForegroundColor Yellow
}
