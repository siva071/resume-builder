# resume_builder.py
# -----------------
# Streamlit ATS-friendly Resume Builder (No LaTeX)
# - Name & Job Title centered + thin lines
# - Education + Certificates included
# - Optional AI enhancement via Google Gemini (graceful fallback)
# - Single-page PDF: auto-compress (font/margins/bullets) to fit A4
#
# Run:
#   pip install streamlit reportlab google-generativeai
#   streamlit run resume_builder.py

import os
import time
from typing import List, Dict, Any

import streamlit as st

# Optional AI (works only if installed and API key provided)

# PDF (ReportLab)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, Flowable
)
from reportlab.pdfgen import canvas
from gemini_optimizer import ResumeOptimizer

# -------------------- Utilities --------------------

def standardize_name(name: str) -> str:
    if not name or not isinstance(name, str):
        return ""
    return " ".join(part.capitalize() for part in name.strip().split())

def clean_multiline(text: str) -> str:
    if not text:
        return ""
    lines = [re.sub(r'^\s*[-*•]\s*', '', ln).strip() for ln in str(text).splitlines()]
    return "\n".join([ln for ln in lines if ln])

def data_to_text(data: dict) -> str:
    """Converts the session state data into a single string for the AI."""
    lines = []
    for key, value in data.items():
        if isinstance(value, list) and value:
            lines.append(f"# {key.replace('_', ' ').title()}\n")
            for entry in value:
                for k, v in entry.items():
                    if v:
                        lines.append(f"{k.title()}: {v}")
                lines.append("\n")
        elif isinstance(value, str) and value:
            lines.append(f"# {key.replace('_', ' ').title()}\n{value}\n")
    return "\n".join(lines)


# -------------------- PDF Helpers --------------------

def add_or_update_style(styles, name: str, **kwargs):
    """
    Safely add or update a ParagraphStyle in the stylesheet.
    """
    if name in styles.byName:
        s = styles[name]
        for k, v in kwargs.items():
            setattr(s, k, v)
        return s
    s = ParagraphStyle(name=name, **kwargs)
    styles.add(s)
    return s

class HRLine(Flowable):
    """
    A horizontal rule that can auto-center within the available width.
    """
    def __init__(self, width="80%", thickness=1.0, color=colors.black, space_before=2, space_after=4, align="CENTER"):
        super().__init__()
        self.req_width = width          # "100%" or numeric points
        self.thickness = float(thickness)
        self.color = color
        self.space_before = float(space_before)
        self.space_after = float(space_after)
        self.align = align
        self._w = 0.0
        self._h = self.thickness + self.space_before + self.space_after

    def wrap(self, availWidth, availHeight):
        if isinstance(self.req_width, str) and self.req_width.endswith("%"):
            pct = float(self.req_width.strip("%")) / 100.0
            self._w = max(1.0, availWidth * pct)
        else:
            self._w = min(float(self.req_width), availWidth)
        return (availWidth, self._h)

    def drawOn(self, canv, x, y, _sW=0):
        dx = 0
        if self.align == "CENTER":
            dx = _sW / 2.0
        elif self.align == "RIGHT":
            dx = _sW
        canv.saveState()
        canv.setStrokeColor(self.color)
        canv.setLineWidth(self.thickness)
        y_mid = y + self.space_after
        canv.line(x + dx, y_mid, x + dx + self._w, y_mid)
        canv.restoreState()

def _make_flow(data: Dict[str, Any],
               name_size=18, title_size=11,
               section_size=11.5, body_size=10, small_size=9, bullet_size=10,
               line_thick=0.8, max_bullets_per_exp=5, max_bullets_per_proj=5) -> List[Flowable]:
    """
    Build a flowable list using given sizes/limits (used by the one-page fitter).
    """
    styles = getSampleStyleSheet()
    add_or_update_style(styles, "Name",    fontName="Helvetica-Bold", fontSize=name_size,   leading=name_size+2, alignment=TA_CENTER, spaceBefore=0, spaceAfter=0)
    add_or_update_style(styles, "Title",   fontName="Helvetica",      fontSize=title_size,  leading=title_size+2, alignment=TA_CENTER, spaceBefore=0, spaceAfter=0)
    add_or_update_style(styles, "Section", fontName="Helvetica-Bold", fontSize=section_size,leading=section_size+2, spaceBefore=0, spaceAfter=0)
    add_or_update_style(styles, "Body",    fontName="Helvetica",      fontSize=body_size,   leading=body_size+2)
    add_or_update_style(styles, "BodyCenter", parent=styles["Body"], alignment=TA_CENTER, spaceBefore=0, spaceAfter=0)
    add_or_update_style(styles, "Small",   fontName="Helvetica",      fontSize=small_size,  leading=small_size+1)
    add_or_update_style(styles, "Bullet",  fontName="Helvetica",      fontSize=bullet_size, leading=bullet_size * 1.4, leftIndent=4)

    class NoLeadingParagraph(Paragraph):
        """A Paragraph with no leading space in its height calculation."""
        def wrap(self, availWidth, availHeight):
            # Call the parent wrap to calculate width and lines
            width, _ = super().wrap(availWidth, availHeight)
            # Override height to be just the font size, removing leading
            return width, self.style.fontSize

    flow: List[Flowable] = []



    def add_section(title: str, elements: List[Flowable]):
        if not elements:
            return
        flow.append(Paragraph(title, styles["Section"]))
        flow.append(HRLine(width="100%", thickness=line_thick, space_before=0, space_after=0, align="CENTER"))
        flow.extend(elements)

    # Professional Summary
    if data.get("professional_summary"):
        add_section("Professional Summary", [Paragraph(data["professional_summary"], styles["Body"])])

    # Skills
    skills_data = data.get("skills", {})
    if isinstance(skills_data, dict) and any(skills_data.values()):
        skills_flowables = []
        for category, skills_text in skills_data.items():
            if skills_text and skills_text.strip():
                line = f"•&nbsp;&nbsp;<b>{category}:</b> {skills_text.strip()}"
                skills_flowables.append(Paragraph(line, styles["Body"]))
        if skills_flowables:
            add_section("SKILLS", skills_flowables)

    # Education (ALWAYS INCLUDED if data exists)
    edu_flow: List[Flowable] = []
    for e in data.get("education_entries", []):
        if not (e.get("degree") and e.get("institution")):
            continue
        when = f"{e.get('start_year','')}" + (f" — {e['end_year']}" if e.get("end_year") else "")
        edu_flow.append(Paragraph(f"<b>{e.get('degree','')}</b> &nbsp;&nbsp; {when}", styles["Body"]))
        inst_line = e.get("institution","")
        if e.get("location"):
            inst_line += f" ({e['location']})"
        if e.get("gpa"):
            inst_line += f" | GPA: {e['gpa']}"
        if inst_line:
            edu_flow.append(Paragraph(inst_line, styles["Small"]))
        if e.get("courses"):
            edu_flow.append(Paragraph(f"Relevant Courses: {e['courses']}", styles["Small"]))
        if e.get("description"):
            edu_flow.append(Paragraph(e["description"], styles["Small"]))
    add_section("Education", edu_flow)

    # Experience
    exp_flow: List[Flowable] = []
    for i, x in enumerate(data.get("experience_entries", [])):
        if not (x.get("job_title") and x.get("company")):
            continue

        when = f"{x.get('start_year', '')}" + (f" — {x['end_year']}" if x.get("end_year") else "")
        exp_flow.append(Paragraph(f"<b>{x.get('job_title','')}</b>, <i>{x.get('company','')}</i> &nbsp;&nbsp; {when}", styles["Body"]))

        bullets = x.get("description_bullets") or [b.strip() for b in x.get("description", "").split('\n') if b.strip()]
        if bullets:
            for b in bullets[:max_bullets_per_exp]:
                exp_flow.append(Paragraph(f"•&nbsp;&nbsp;{b}", styles["Bullet"]))

        if i < len(data.get("experience_entries", [])) - 1:
            exp_flow.append(Spacer(1, 4)) # Small space between entries
    add_section("EXPERIENCE", exp_flow)

    # Projects
    proj_flow: List[Flowable] = []
    for i, p in enumerate(data.get("project_entries", [])):
        if not p.get("title"):
            continue

        parts = [f"<b>{p.get('title','')}</b>"]
        if p.get('start_year') or p.get('end_year'):
            parts.append(f"({p.get('start_year', '')} - {p.get('end_year', '')})")
        if p.get('link'):
            parts.append(f'<a href="{p["link"]}" color="blue"><u>Project Link</u></a>')
        proj_flow.append(Paragraph(" &nbsp;&nbsp; ".join(parts), styles["Body"]))

        bullets = p.get("description_bullets") or [b.strip() for b in p.get("description", "").split('\n') if b.strip()]
        if bullets:
            for b in bullets[:max_bullets_per_proj]:
                proj_flow.append(Paragraph(f"•&nbsp;&nbsp;{b}", styles["Bullet"]))

        if i < len(data.get("project_entries", [])) - 1:
            proj_flow.append(Spacer(1, 4))
    add_section("PROJECTS", proj_flow)

    # Certificates (ALWAYS INCLUDED if data exists)
    cert_flow: List[Flowable] = []
    for c in data.get("certificate_entries", []):
        if not c.get("name"):
            continue
        line = f"• <b>{c['name']}</b>"
        extras = []
        if c.get("organization"):
            extras.append(c["organization"])
        if c.get("year"):
            extras.append(str(c["year"]))
        if c.get("url"):
            extras.append(f'<a href="{c["url"]}" color="blue"><u>Credential</u></a>')
        if extras:
            line += " — " + " | ".join(extras)
        cert_flow.append(Paragraph(line, styles["Body"]))
    add_section("Certificates", cert_flow)

    # Achievements
    ach_flow: List[Flowable] = []
    for a in data.get("achievement_entries", []):
        if not a.get("title"):
            continue
        line = f"• {a['title']}"
        if a.get("year"):
            line += f" — {a['year']}"
        if a.get("description"):
            line += f": {a['description']}"
        ach_flow.append(Paragraph(line, styles["Body"]))
    add_section("Achievements", ach_flow)

    # Languages
    if data.get("languages"):
        add_section("Languages Known", [Paragraph(data["languages"], styles["Body"])])

    return flow

def run_ai_optimizer(data: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """
    Uses Gemini to optimize the content of the resume data.
    """
    optimizer = ResumeOptimizer(api_key)
    st.toast("Running AI optimizations... this may take a moment.")

    # Optimize Professional Summary
    if data.get("professional_summary"):
        data["professional_summary"] = optimizer.optimize_summary(data["professional_summary"])

    # Optimize Experience Bullets
    for exp in data.get("experience_entries", []):
        if exp.get("description"):
            bullets = [b for b in exp["description"].split("\n") if b.strip()]
            optimized_bullets = optimizer.optimize_bullet_points(bullets)
            exp["description"] = "\n".join(optimized_bullets)
    
    # Optimize Project Bullets
    for proj in data.get("project_entries", []):
        if proj.get("description"):
            bullets = [b for b in proj["description"].split("\n") if b.strip()]
            optimized_bullets = optimizer.optimize_bullet_points(bullets)
            proj["description"] = "\n".join(optimized_bullets)

    # Optimize Achievements (condense to single lines)
    for ach in data.get("achievement_entries", []):
        if ach.get("description"):
            ach["title"] = f'{ach["title"]}: {ach["description"]}'
            ach["description"] = ""
        ach["title"] = optimizer.make_single_line(ach["title"])

    st.toast("AI optimizations complete!")
    return data

def _draw_header(c, width, height, data, styles):
    """Draws the header directly on the canvas for precise control."""
    top_margin = 8 * mm
    y_pos = height - top_margin

    # Name
    full_name = standardize_name(data.get("full_name", ""))
    if full_name:
        style = styles["Name"]
        c.setFont(style.fontName, style.fontSize)
        y_pos -= style.leading * 0.8 # Reduced gap
        c.drawCentredString(width / 2.0, y_pos, full_name)

    # Title
    job_title = (data.get("job_title") or "").strip()
    if job_title:
        style = styles["Title"]
        c.setFont(style.fontName, style.fontSize)
        y_pos -= style.leading * 0.8 # Reduced gap
        c.drawCentredString(width / 2.0, y_pos, job_title)

    # Contact Info
    contact_items = []
    if data.get("address"): contact_items.append(data["address"])
    if data.get("email"): contact_items.append(data["email"])
    if data.get("phone"): contact_items.append(data["phone"])
    if data.get("linkedin_url"): contact_items.append(f'<a href="{data["linkedin_url"]}" color="blue"><u>LinkedIn</u></a>')
    if data.get("github_url"): contact_items.append(f'<a href="{data["github_url"]}" color="blue"><u>GitHub</u></a>')
    if data.get("website"): contact_items.append(f'<a href="{data["website"]}" color="blue"><u>Portfolio</u></a>')
    contact_line = " | ".join(contact_items)

    if contact_line:
        style = styles["BodyCenter"]
        p = Paragraph(contact_line, style)
        p_w, p_h = p.wrapOn(c, width - 50, height) # wrap on canvas
        y_pos -= p_h * 1.2
        p.drawOn(c, (width - p_w) / 2.0, y_pos)

    # Add a small gap before the rest of the content
    y_pos -= 4 * mm
    return y_pos

def build_pdf_single_page(data: Dict[str, Any]) -> bytes:
    """
    Builds a single-page PDF by drawing directly to the canvas for precise layout control.
    """
    import io
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Get the full flow of content
    # We use the most compact settings by default
    sizes = {"name": 16, "title": 10, "section": 10, "body": 9, "small": 8, "bullet": 9, "line": 0.5}
    limits = {"exp": 4, "proj": 4}
    flowables = _make_flow(
        data,
        name_size=sizes["name"], title_size=sizes["title"],
        section_size=sizes["section"], body_size=sizes["body"],
        small_size=sizes["small"], bullet_size=sizes["bullet"],
        line_thick=sizes["line"],
        max_bullets_per_exp=limits["exp"], max_bullets_per_proj=limits["proj"]
    )

    # Define margins
    left_margin = 12 * mm
    right_margin = 12 * mm
    top_margin = 4 * mm
    bottom_margin = 10 * mm

    frame_width = width - left_margin - right_margin
    frame_height = height - top_margin - bottom_margin
    
    # Draw the header first and get the new y_pos
    styles_for_header = getSampleStyleSheet()
    add_or_update_style(styles_for_header, "Name", fontName="Helvetica-Bold", fontSize=sizes["name"], leading=sizes["name"]+2, alignment=TA_CENTER)
    add_or_update_style(styles_for_header, "Title", fontName="Helvetica", fontSize=sizes["title"], alignment=TA_CENTER)
    add_or_update_style(styles_for_header, "Body", fontName="Helvetica", fontSize=sizes["body"])
    add_or_update_style(styles_for_header, "BodyCenter", parent=styles_for_header["Body"], alignment=TA_CENTER, fontSize=sizes["body"])
    
    y_pos = _draw_header(c, width, height, data, styles_for_header)

    for f in flowables:
        w, h = f.wrapOn(c, frame_width, frame_height)
        if y_pos - h < bottom_margin:
            # This content doesn't fit, stop here or raise error
            # For simplicity, we'll just stop drawing.
            break 
        f.drawOn(c, left_margin, y_pos - h)
        y_pos -= h

    c.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

# -------------------- Streamlit UI --------------------

def render_welcome_page():
    st.set_page_config(page_title="Welcome to FresherHub", page_icon="👋", layout="centered")
    st.title("👋 Welcome to FresherHub")
    st.markdown("We build an ATS-friendly Resume Builder tool that helps you land your dream job.")
    st.markdown("---")

    st.subheader("Enter Your Google Gemini API Key")
    api_key = st.text_input(
        "API Key",
        type="password",
        placeholder="Paste your API key here",
        help="Your API key is required to enable AI-powered resume enhancements."
    )

    with st.expander("How to get your Gemini API Key"):
        st.markdown("""
        1. Go to the [Google AI Studio](https://aistudio.google.com/).
        2. Sign in with your Google account.
        3. Click on **"Get API key"** in the top left corner.
        4. Click **"Create API key in new project"**.
        5. Copy the generated key and paste it above.
        """)

    if st.button("Save & Continue", use_container_width=True):
        if api_key:
            st.session_state.api_key = api_key
            st.session_state.page = 'builder'
            st.rerun()
        else:
            st.error("A Google Gemini API key is mandatory to proceed.")

def clear_form_data():
    """Clears all the user-entered data from the session state."""
    # Keep api_key and page, clear everything else
    keys_to_clear = [k for k in st.session_state.keys() if k not in ['api_key', 'page', 'theme']]
    for key in keys_to_clear:
        del st.session_state[key]
    st.toast("Form fields have been cleared!")

def render_builder_page():
    st.set_page_config(page_title="ATS-Friendly Resume Builder", page_icon="📄", layout="centered")
    c1, c2 = st.columns([3, 1])
    with c1:
        st.title("📄 ATS-Friendly Resume Builder (One-Page PDF)")
    with c2:
        st.button("🔄 Refresh Page", on_click=clear_form_data, use_container_width=True)
    st.caption("Your resume will be automatically enhanced using the provided Gemini API key.")

    def init_state():
        ss = st.session_state
        # API key is already set from the welcome page and is mandatory.
        ss.setdefault('model', None)

        # Ensure lists exist
        ss.setdefault('education_entries', [{'degree':'', 'institution':'', 'start_year':'', 'end_year':'', 'description':'', 'location':'', 'gpa':'', 'courses':''}])
        ss.setdefault('experience_entries', [
            {
                'job_title': 'Freelance Web Developer & Designer',
                'company': 'edutech',
                'location': 'Bangalore',
                'start_year': '2022',
                'end_year': '2026',
                'description': ('Engineered and launched custom WordPress websites for Ed-Tech clients, managing the full project lifecycle from client consultation to final deployment.\n'
                                'Designed compelling social media creatives and marketing visuals using Adobe Creative Suite, enhancing brand visibility and engagement.\n'
                                'Produced and edited short-form promotional videos, contributing to successful product marketing campaigns.'),
                'team_size': '5',
                'technologies': 'WordPress, CSS, Adobe Creative Suite'
            }
        ])
        ss.setdefault('project_entries', [
            {
                'title': 'Resumate Quantum Forge – AI Resume Builder',
                'link': '',
                'start_year': '2023',
                'end_year': '2024',
                'description': ('Developed a full-stack AI-powered resume generator using Streamlit for the front end and Google\'s Gemini API for intelligent content enhancement.\n'
                                'Implemented features for ATS-aligned bullet point optimization and guided user inputs, demonstrating proficiency in AI integration and application development.'),
                'outcome': 'Demonstrated AI integration & full-stack skills.'
            }
        ])
        ss.setdefault('certificate_entries', [{'name':'', 'organization':'', 'year':'', 'url':''}])
        ss.setdefault('achievement_entries', [{'title':'', 'year':'', 'description':''}])
        ss.setdefault('skills', {
            'programming': 'Python',
            'frameworks': 'Streamlit, WordPress',
            'databases': '',
            'tools': 'Google Gemini API, Adobe Creative Suite, CSS'
        })

    init_state()
    ss = st.session_state

    # Target Job Description
    st.subheader("🎯 Target Job Description")
    job_description = st.text_area(
        "Paste the job description (improves ATS alignment)",
        height=140,
        placeholder="e.g., Seeking a software engineer with 3+ years of Python and Django..."
    )

    # Personal Info
    st.subheader("👤 Personal Information")
    c1, c2 = st.columns(2)
    full_name = c1.text_input("Full Name *")
    job_title = c2.text_input("Job Title *")
    address = c1.text_input("Address *")
    email = c2.text_input("Email *")
    phone = c1.text_input("Phone *")
    linkedin_url = c2.text_input("LinkedIn URL *")
    github_url = c1.text_input("GitHub URL *")
    website = c2.text_input("Personal Website", key="personal_website")

    # Summary
    st.subheader("📝 Professional Summary")
    professional_summary = st.text_area("Professional Summary *",
        value="Versatile Web Developer and Designer with 4 years of freelance experience delivering custom WordPress solutions for Ed-Tech clients. Proficient in front-end technologies, UI/UX design, and video production. Adept at leveraging AI to build innovative applications, as demonstrated by creating a Streamlit and Gemini API-powered resume builder. Seeking to apply full-stack development and creative skills to produce high-quality digital products.",
        height=160)

    # Skills
    st.subheader("🛠️ Skills")
    ss.skills['programming'] = st.text_input("Programming", ss.skills.get('programming',''))
    ss.skills['frameworks']  = st.text_input("Frameworks & Libraries", ss.skills.get('frameworks',''))
    ss.skills['databases']   = st.text_input("Databases", ss.skills.get('databases',''))
    ss.skills['tools']       = st.text_input("Tools / Platforms", ss.skills.get('tools',''))

    # Education
    st.subheader("🎓 Education")
    if st.button("＋ Add Education"):
        ss.education_entries.append({'degree':'', 'institution':'', 'start_year':'', 'end_year':'', 'description':'', 'location':'', 'gpa':'', 'courses':''})
    for i, edu in enumerate(ss.education_entries):
        with st.expander(f"Education #{i+1}", expanded=True):
            edu['degree'] = st.text_input("Degree *", edu.get('degree',''), key=f"edu_degree_{i}")
            edu['institution'] = st.text_input("Institution *", edu.get('institution',''), key=f"edu_inst_{i}")
            edu['location'] = st.text_input("Location", edu.get('location',''), key=f"edu_loc_{i}")
            c1, c2 = st.columns(2)
            edu['start_year'] = c1.text_input("Start Year *", edu.get('start_year',''), key=f"edu_start_{i}")
            edu['end_year'] = c2.text_input("End Year", edu.get('end_year',''), key=f"edu_end_{i}")
            edu['gpa'] = st.text_input("GPA", edu.get('gpa',''), key=f"edu_gpa_{i}")
            edu['courses'] = st.text_input("Relevant Courses", edu.get('courses',''), key=f"edu_courses_{i}")
            if i > 0 and st.button("Remove Education", key=f"edu_remove_{i}"):
                ss.education_entries.pop(i)
                st.rerun()

    # Experience
    st.subheader("💼 Experience")
    if len(st.session_state.experience_entries) < 3:
        if st.button("＋ Add Experience"):
            st.session_state.experience_entries.append({'job_title':'', 'company':'', 'start_year':'', 'end_year':'', 'description':''})
            st.rerun()
    for i, exp in enumerate(st.session_state.experience_entries):
        with st.expander(f"Experience #{i+1}", expanded=True):
            exp['job_title'] = st.text_input("Job Title *", exp.get('job_title',''), key=f"exp_title_{i}")
            exp['company'] = st.text_input("Company *", exp.get('company',''), key=f"exp_company_{i}")
            c1, c2 = st.columns(2)
            exp['start_year'] = c1.text_input("Start Year *", exp.get('start_year',''), key=f"exp_start_{i}")
            exp['end_year'] = c2.text_input("End Year", exp.get('end_year',''), key=f"exp_end_{i}")
            st.markdown("**Description (bullets or lines)**")
            exp['description'] = st.text_area("Description", value=exp.get('description', ''), height=100, key=f"exp_desc_{i}")
            if i > 0 and st.button("Remove Experience", key=f"exp_remove_{i}"):
                st.session_state.experience_entries.pop(i)
                st.rerun()

    # Projects
    st.subheader("🚀 Projects")
    if len(st.session_state.project_entries) < 3:
        if st.button("＋ Add Project"):
            st.session_state.project_entries.append({'title':'', 'link':'', 'start_year':'', 'end_year':'', 'description':''})
            st.rerun()
    for i, proj in enumerate(st.session_state.project_entries):
        with st.expander(f"Project #{i+1}", expanded=True):
            proj['title'] = st.text_input("Title *", proj.get('title',''), key=f"proj_title_{i}")
            proj['link'] = st.text_input("Link", proj.get('link',''), key=f"proj_link_{i}")
            c1, c2 = st.columns(2)
            proj['start_year'] = c1.text_input("Start Year *", proj.get('start_year',''), key=f"proj_start_{i}")
            proj['end_year'] = c2.text_input("End Year", proj.get('end_year',''), key=f"proj_end_{i}")
            st.markdown("**Description (bullets or lines)**")
            proj['description'] = st.text_area("Description", value=proj.get('description', ''), height=100, key=f"proj_desc_{i}")
            if i > 0 and st.button("Remove Project", key=f"proj_remove_{i}"):
                ss.project_entries.pop(i)
                st.rerun()

    # Certificates
    st.subheader("📜 Certificates")
    if st.button("＋ Add Certificate"):
        ss.certificate_entries.append({'name':'', 'organization':'', 'year':'', 'url':''})
    for i, cert in enumerate(ss.certificate_entries):
        with st.expander(f"Certificate #{i+1}", expanded=True):
            cert['name'] = st.text_input("Certificate Name *", cert.get('name',''), key=f"cert_name_{i}")
            cert['organization'] = st.text_input("Organization *", cert.get('organization',''), key=f"cert_org_{i}")
            cert['year'] = st.text_input("Year *", cert.get('year',''), key=f"cert_year_{i}")
            cert['url'] = st.text_input("Credential URL", cert.get('url',''), key=f"cert_url_{i}")
            if i > 0 and st.button("Remove Certificate", key=f"cert_remove_{i}"):
                ss.certificate_entries.pop(i)
                st.rerun()

    # Achievements
    st.subheader("🏅 Achievements")
    if st.button("＋ Add Achievement"):
        ss.achievement_entries.append({'title':'', 'year':'', 'description':''})
    for i, ach in enumerate(ss.achievement_entries):
        with st.expander(f"Achievement #{i+1}", expanded=True):
            ach['title'] = st.text_input("Title *", ach.get('title',''), key=f"ach_title_{i}")
            ach['year'] = st.text_input("Year *", ach.get('year',''), key=f"ach_year_{i}")
            ach['description'] = st.text_input("Short Description", ach.get('description',''), key=f"ach_desc_{i}")
            if i > 0 and st.button("Remove Achievement", key=f"ach_remove_{i}"):
                ss.achievement_entries.pop(i)
                st.rerun()

    # Languages
    st.subheader("🌍 Languages")
    languages = st.text_input("Languages *", value="English, Telugu")

    # AI Enhanced Preview
    if 'enhanced_resume_content' in st.session_state and st.session_state.enhanced_resume_content:
        st.subheader("✨ AI Enhanced Preview")
        st.text_area("Review the AI-enhanced content below. It will be used for the PDF.", st.session_state.enhanced_resume_content, height=300)

    # Generate Button
    if st.button("🚀 Generate resume ", use_container_width=True):
        try:
            # Collect all data from UI
            data = {
                'full_name': standardize_name(full_name),
                'job_title': job_title, 'address': address, 'email': email, 'phone': phone,
                'linkedin_url': linkedin_url, 'github_url': github_url, 'website': website,
                'job_description': job_description, 'professional_summary': professional_summary,
                'languages': languages, 'education_entries': st.session_state.education_entries,
                'experience_entries': st.session_state.experience_entries,
                'project_entries': st.session_state.project_entries,
                'certificate_entries': st.session_state.certificate_entries,
                'achievement_entries': st.session_state.achievement_entries,
                'skills': st.session_state.skills
            }

            api_key = st.session_state.get('api_key')
            if api_key:
                with st.spinner("Running full resume enhancement... this may take a moment."):
                    optimizer = ResumeOptimizer(api_key)
                    raw_resume_text = data_to_text(data)
                    enhanced_text = optimizer.enhance_resume_content(raw_resume_text)
                    st.session_state.enhanced_resume_content = enhanced_text
                    st.toast("AI enhancement complete!")

            with st.spinner("Generating single-page PDF..."):

                # Minimal validation
                required = {
                    "Full Name": data['full_name'],
                    "Job Title": data['job_title'],
                    "Address": data['address'],
                    "Email": data['email'],
                    "Phone": data['phone'],
                    "LinkedIn URL": data['linkedin_url'],
                    "Professional Summary": data['professional_summary'],
                    "Languages": data['languages']
                }
                missing = [k for k, v in required.items() if not str(v or "").strip()]
                if missing:
                    st.error("Please fill in the required fields:\n- " + "\n- ".join(missing))
                else:
                    pdf_bytes = build_pdf_single_page(data)
                    st.success("✅ One-page resume generated!")
                    st.download_button(
                        label="📥 Download Resume (PDF)",
                        data=pdf_bytes,
                        file_name=f"{data['full_name'].replace(' ','_')}_Resume.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        except Exception as e:
            st.exception(e)

def main():
    # Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state.page = 'welcome'

    # Page router
    if st.session_state.page == 'welcome':
        render_welcome_page()
    else:
        render_builder_page()

if __name__ == "__main__":
    main()
