#!/bin/bash

# ATS-Friendly Resume Builder Launcher
# Shell Script for Linux/macOS

echo "========================================"
echo "    ATS-Friendly Resume Builder"
echo "========================================"
echo ""

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.8+ from https://python.org"
    read -p "Press Enter to exit"
    exit 1
fi

echo "✓ Python found: $($PYTHON_CMD --version)"

# Check if requirements are installed
echo "Checking dependencies..."
if pip show streamlit &> /dev/null; then
    echo "✓ Streamlit is installed"
else
    echo "Installing required packages..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Failed to install requirements"
        read -p "Press Enter to exit"
        exit 1
    fi
    echo "✓ Dependencies installed successfully"
fi

echo ""
echo "Starting Resume Builder..."
echo "The application will open in your default web browser"
echo ""
echo "Note: You can enter your Google Gemini API key directly in the app's sidebar"
echo "Get your free API key from: https://makersuite.google.com/app/apikey"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Run the Streamlit application
streamlit run resume_builder.py

read -p "Press Enter to exit"
