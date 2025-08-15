# 🪟 Windows Setup Guide for Resume Builder

This guide will help you set up and run the ATS-Friendly Resume Builder on Windows.

## 🚀 Quick Start (Recommended)

### Option 1: Use the Batch File (Easiest)
1. **Double-click** `run_resume_builder.bat`
2. The script will automatically:
   - Check if Python is installed
   - Install required packages
   - Start the application
3. Enter your Google Gemini API key in the app's sidebar

### Option 2: Use PowerShell Script
1. **Right-click** `run_resume_builder.ps1`
2. Select "Run with PowerShell"
3. If prompted about execution policy, type `Y` and press Enter

## 📋 Manual Setup

### Step 1: Install Python
1. Download Python from [python.org](https://python.org)
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Verify installation by opening Command Prompt and typing:
   ```cmd
   python --version
   ```

### Step 2: Install LaTeX (MiKTeX)
1. Download MiKTeX from [miktex.org](https://miktex.org/download)
2. Run the installer as Administrator
3. Choose "Install missing packages on-the-fly = Yes"
4. Add MiKTeX to PATH (should be automatic)

### Step 3: Get Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key

**Note:** You don't need to set environment variables anymore! Just enter your API key directly in the app's sidebar.

### Step 4: Install Python Packages
```cmd
pip install -r requirements.txt
```

### Step 5: Run the Application
```cmd
streamlit run resume_builder.py
```

## 🔧 Troubleshooting

### "Python is not recognized"
- Python is not in PATH
- Reinstall Python and check "Add to PATH"
- Or manually add Python to PATH

### "LaTeX compilation failed"
- MiKTeX not installed or not in PATH
- Install MiKTeX and restart Command Prompt
- Verify `pdflatex` command works

### "Could not enhance text with Gemini"
- API key not entered correctly in the app's sidebar
- Verify internet connection
- Check API quota limits

### "Streamlit not found"
- Packages not installed: `pip install -r requirements.txt`
- Check pip is in PATH

### PowerShell Execution Policy Error
Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 📁 File Structure
```
resume builder/
├── resume_builder.py          # Main application
├── requirements.txt           # Python dependencies
├── run_resume_builder.bat    # Windows batch file
├── run_resume_builder.ps1    # PowerShell script
├── README.md                 # Full documentation
└── config.example            # Configuration template
```

## 🎯 Next Steps
1. Run the application using one of the launcher scripts
2. Fill in your resume information
3. Generate and download your professional PDF resume
4. Customize the LaTeX template if needed

## 💡 Tips
- Use the batch file for the easiest experience
- Keep your API key secure and don't share it
- The application works offline for PDF generation (once LaTeX is installed)
- You can modify the LaTeX template in `resume_builder.py`

## 🆘 Need Help?
- Check the main README.md for detailed documentation
- Verify all prerequisites are installed
- Check console output for error messages
- Ensure firewall/antivirus isn't blocking the application

---

**Happy Resume Building on Windows! 🪟✨**
