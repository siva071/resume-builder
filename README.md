<<<<<<< HEAD
# 📄 ATS-Friendly Resume Builder

A professional resume builder web application built with Python and Streamlit that creates ATS-optimized resumes using AI-powered content enhancement and LaTeX compilation.

## ✨ Features

- **AI-Powered Content Enhancement**: Uses Google Gemini API to improve grammar, spelling, and professional language
- **ATS-Optimized**: Generates clean, simple resumes that pass through Applicant Tracking Systems
- **LaTeX Template**: Professional resume layout with your custom LaTeX template
- **Multi-Entry Support**: Add multiple education, experience, project, certificate, and achievement entries
- **Bullet Point Conversion**: Automatically converts descriptions into professional bullet points
- **PDF Generation**: Direct PDF output from LaTeX compilation
- **Clean UI**: Modern, responsive Streamlit interface

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed on your system
2. **LaTeX Distribution** (MiKTeX for Windows, TeX Live for Linux/Mac)
3. **Google Gemini API Key** (free tier available) - **Enter directly in the app!**

### Installation

1. **Clone or download** this repository
2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Google Gemini API**:
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - **No environment variables needed!** Enter your API key directly in the app's sidebar

4. **Install LaTeX**:
   - **Windows**: Download and install [MiKTeX](https://miktex.org/download)
   - **Linux**: `sudo apt-get install texlive-full` (Ubuntu/Debian)
   - **macOS**: Install [MacTeX](https://www.tug.org/mactex/)

### Running the Application

```bash
streamlit run resume_builder.py
```

The app will open in your default web browser at `http://localhost:8501`

**🔑 API Key Setup**: Once the app opens, enter your Google Gemini API key in the sidebar to enable AI features!

## 📋 Usage Guide

### 1. Fill in Personal Information
- Complete all required fields (marked with *)
- Provide accurate contact information and URLs

### 2. Write Professional Summary
- Describe your background, skills, and career objectives
- AI will enhance this text for better impact

### 3. Add Skills
- List your technical and soft skills
- Use comma-separated values for easy reading

### 4. Education Section
- Add multiple education entries
- Include degree, institution, years, and optional description

### 5. Work Experience
- Describe your roles and achievements in detail
- AI will convert descriptions into professional bullet points
- Focus on impact and quantifiable results

### 6. Projects
- Showcase your technical projects
- Include technologies used and outcomes
- AI will enhance descriptions and create bullet points

### 7. Certificates & Achievements
- Add professional certifications
- Include awards and recognitions

### 8. Generate Resume
- Click "Generate Resume" button
- AI will enhance all content
- LaTeX will be compiled to PDF
- Download your professional resume

## 🔧 Technical Details

### Architecture
- **Frontend**: Streamlit web interface
- **AI Enhancement**: Google Gemini Pro API
- **Document Generation**: LaTeX compilation with pdflatex
- **PDF Output**: Direct binary PDF generation

### Key Functions

#### `enhance_text_with_gemini(text, section_type)`
- Corrects spelling and grammar
- Improves professional language
- Maintains original meaning

#### `convert_to_bullet_points(text, section_type)`
- Converts descriptions to bullet points
- Uses strong action verbs
- Focuses on achievements and impact

#### `generate_latex_content(data)`
- Creates LaTeX content from user data
- Handles multi-entry sections
- Maintains template structure

#### `compile_latex_to_pdf(latex_content)`
- Compiles LaTeX to PDF
- Uses temporary directories
- Handles compilation errors

### LaTeX Template Features
- Professional typography with FontAwesome icons
- Clean section dividers
- Responsive layout for different content lengths
- ATS-friendly formatting (no tables, simple structure)

## 🎨 Customization

### Modifying the LaTeX Template
Edit the `create_latex_file()` function in `resume_builder.py` to:
- Change fonts and sizes
- Modify section layouts
- Add new sections
- Customize styling

### Adding New Fields
1. Add input fields in the Streamlit form
2. Include data in the `data` dictionary
3. Update LaTeX generation functions
4. Modify validation logic

## 🚨 Troubleshooting

### Common Issues

#### "LaTeX compilation failed"
- Ensure LaTeX is properly installed
- Check if `pdflatex` command is available in PATH
- Verify LaTeX packages are installed

#### "Could not enhance text with Gemini"
- Check your API key is entered correctly in the sidebar
- Verify internet connection
- Check API quota limits

#### "PDF file not generated"
- Check LaTeX compilation logs
- Ensure all required LaTeX packages are installed
- Verify file permissions

### LaTeX Package Dependencies
The template requires these LaTeX packages:
- `fontawesome5` - Icons
- `hyperref` - Clickable links
- `multicol` - Multi-column layout
- `tabularx` - Flexible tables
- `enumitem` - List customization
- `microtype` - Typography improvements

## 📱 Browser Compatibility
- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## 🔒 Security Notes
- API keys are stored securely in Streamlit session state
- No sensitive data is logged or stored permanently
- Temporary files are automatically cleaned up
- API keys are not saved to disk

## 📄 License
This project is open source and available under the MIT License.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📞 Support
If you encounter any issues:
1. Check the troubleshooting section
2. Verify all prerequisites are met
3. Check the console output for error messages
4. Open an issue with detailed error information

---

**Happy Resume Building! 🚀**
=======
# resume-builder
>>>>>>> 07c192d25a61587e2527a6834e544df9b33a0dd7
