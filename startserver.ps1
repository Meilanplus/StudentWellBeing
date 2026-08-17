# Activates the project venv and starts the dev server with autoreload.
# Run from the project root: .\startserver.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Student Well-Being Support System" -ForegroundColor Cyan
Write-Host "Starting Local Development Server" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create a virtual environment first:" -ForegroundColor Yellow
    Write-Host "  python -m venv venv" -ForegroundColor White
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check Python
$pythonVersion = python --version 2>&1
Write-Host "Using: $pythonVersion" -ForegroundColor Green

# Start the development server
Write-Host ""
Write-Host "Starting Uvicorn server on port 8001..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 Application will be available at: http://localhost:8001" -ForegroundColor Green
Write-Host ""

try {
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
} catch {
    Write-Host "ERROR: Failed to start server" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
