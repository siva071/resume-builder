# ATS-Friendly Resume Builder Launcher
# PowerShell Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    ATS-Friendly Resume Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if requirements are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$streamlit = pip show streamlit 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Streamlit is installed" -ForegroundColor Green
} else {
    Write-Host "Installing required packages..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Failed to install requirements" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Resume Builder..." -ForegroundColor Green
Write-Host "The application will open in your default web browser" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: You can enter your Google Gemini API key directly in the app's sidebar" -ForegroundColor Yellow
Write-Host "Get your free API key from: https://makersuite.google.com/app/apikey" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the application" -ForegroundColor Yellow
Write-Host ""

# Run the Streamlit application
try {
    streamlit run resume_builder.py
} catch {
    Write-Host "❌ ERROR: Failed to start Streamlit application" -ForegroundColor Red
    Write-Host "Error details: $_" -ForegroundColor Red
}

Read-Host "Press Enter to exit"
