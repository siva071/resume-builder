@echo off
echo ========================================
echo    ATS-Friendly Resume Builder
echo ========================================
echo.
echo Setting up environment...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show streamlit >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
)

echo.
echo Starting Resume Builder...
echo The application will open in your default web browser
echo.
echo Note: You can enter your Google Gemini API key directly in the app's sidebar
echo Get your free API key from: https://makersuite.google.com/app/apikey
echo.
echo Press Ctrl+C to stop the application
echo.

REM Run the Streamlit application
streamlit run resume_builder.py

pause
