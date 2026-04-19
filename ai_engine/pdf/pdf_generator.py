import os
import re
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx2pdf import convert
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
import logging

logger = logging.getLogger(__name__)

# ─── PROFESSIONAL COLOR PALETTE ──────────────────────────────────────────────
PRIMARY_COLOR = colors.HexColor('#1F4788')     # Deep Blue (Professional)
ACCENT_COLOR = colors.HexColor('#D95F2B')      # Burnt Orange (Accent)
HEADER_COLOR = colors.HexColor('#1A1714')      # Almost Black (Text)
SECTION_COLOR = colors.HexColor('#1F4788')     # Deep Blue for sections
LIGHT_TEXT = colors.HexColor('#505050')        # Dark Gray text
DIVIDER_COLOR = colors.HexColor('#D95F2B')     # Orange divider

def _clean_text_reportlab(text: str) -> str:
    """Sanitize text for ReportLab — handles XML escaping and non-ASCII."""
    if not text: return ""
    replacements = {
        '\u2022': '•', '\u2023': '•', '\u2043': '•', '\u2013': '-', '\u2014': '--',
        '\u2018': "'", '\u2019': "'", '\u201c': '"', '\u201d': '"',
        '\u2026': '...', '\u00a0': ' '
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return text

def _parse_resume_sections(resume_text: str) -> dict:
    """Parse resume into structured sections with proper formatting."""
    sections = {}
    current_section = None
    current_items = []
    
    lines = resume_text.split('\n')
    section_keywords = {
        'EXPERIENCE': ['EXPERIENCE', 'PROFESSIONAL EXPERIENCE', 'WORK EXPERIENCE', 'EMPLOYMENT'],
        'SKILLS': ['SKILLS', 'TECHNICAL SKILLS', 'CORE SKILLS', 'COMPETENCIES'],
        'EDUCATION': ['EDUCATION', 'ACADEMIC', 'DEGREE', 'UNIVERSITY'],
        'PROJECTS': ['PROJECTS', 'PROJECT EXPERIENCE', 'PORTFOLIO'],
        'CERTIFICATIONS': ['CERTIFICATIONS', 'CERTIFICATES', 'CERTIFICATION'],
        'SUMMARY': ['SUMMARY', 'PROFILE', 'OBJECTIVE', 'PROFESSIONAL SUMMARY']
    }
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        is_header = False
        for section_key, keywords in section_keywords.items():
            if any(kw in stripped.upper() for kw in keywords) and len(stripped) < 40:
                if current_section and current_items:
                    sections[current_section] = current_items
                current_section = section_key
                current_items = []
                is_header = True
                break
        
        if not is_header and current_section:
            current_items.append(stripped)
    
    if current_section and current_items:
        sections[current_section] = current_items
    
    return sections

def generate_pdf_reportlab(resume_text: str, output_path: str, candidate_name: str = "Candidate") -> str:
    """PREMIUM PROFESSIONAL PDF generator with modern design and superior typography."""
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        topMargin=0.5*inch, bottomMargin=0.5*inch,
        leftMargin=0.65*inch, rightMargin=0.65*inch
    )
    elements = []
    
    # ─── PROFESSIONAL STYLES ─────────────────────────────────────────────────
    
    # Name/Title at top
    title_style = ParagraphStyle(
        'Title',
        fontSize=26,
        textColor=PRIMARY_COLOR,
        spaceAfter=1,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=28
    )
    
    # Contact info
    contact_style = ParagraphStyle(
        'Contact',
        fontSize=9,
        textColor=LIGHT_TEXT,
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica',
        leading=10
    )
    
    # Section headers with modern look
    section_header_style = ParagraphStyle(
        'SectionHeader',
        fontSize=13,
        textColor=SECTION_COLOR,
        spaceAfter=10,
        spaceBefore=8,
        fontName='Helvetica-Bold',
        leftIndent=0
    )
    
    # Job title / company
    job_title_style = ParagraphStyle(
        'JobTitle',
        fontSize=11,
        textColor=HEADER_COLOR,
        spaceAfter=1,
        spaceBefore=6,
        fontName='Helvetica-Bold',
        leading=12
    )
    
    # Job subtitle (company + dates)
    job_subtitle_style = ParagraphStyle(
        'JobSubtitle',
        fontSize=10,
        textColor=ACCENT_COLOR,
        spaceAfter=5,
        fontName='Helvetica-Oblique',
        leading=11
    )
    
    # Bullet points
    bullet_style = ParagraphStyle(
        'Bullet',
        fontSize=10,
        leading=14,
        leftIndent=25,
        spaceAfter=5,
        textColor=LIGHT_TEXT,
        fontName='Helvetica',
        alignment=TA_JUSTIFY
    )
    
    # Regular text
    normal_style = ParagraphStyle(
        'Normal',
        fontSize=10,
        leading=13,
        spaceAfter=5,
        textColor=LIGHT_TEXT,
        fontName='Helvetica',
        alignment=TA_JUSTIFY
    )
    
    # Skills tags
    skill_style = ParagraphStyle(
        'Skill',
        fontSize=10,
        leading=13,
        spaceAfter=4,
        textColor=LIGHT_TEXT,
        fontName='Helvetica',
        alignment=TA_LEFT
    )
    
    # ─── HEADER SECTION ──────────────────────────────────────────────────────
    
    elements.append(Paragraph(_clean_text_reportlab(candidate_name.upper()), title_style))
    
    # Extract contact info if available
    contact_lines = []
    for line in resume_text.split('\n')[:5]:
        if any(x in line.lower() for x in ['email', '@', 'phone', '(', 'linkedin', 'github', 'linkedin.com']):
            clean = _clean_text_reportlab(line.strip())
            if clean and len(clean) < 80:
                contact_lines.append(clean)
    
    if contact_lines:
        contact_text = ' • '.join(contact_lines[:3])
        elements.append(Paragraph(contact_text, contact_style))
    
    # Professional divider
    elements.append(Spacer(1, 0.08*inch))
    divider = HRFlowable(width="100%", thickness=3, color=ACCENT_COLOR, spaceAfter=12)
    elements.append(divider)
    elements.append(Spacer(1, 0.05*inch))
    
    # ─── CONTENT SECTIONS ────────────────────────────────────────────────────
    
    sections = _parse_resume_sections(resume_text)
    section_order = ['SUMMARY', 'EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS', 'CERTIFICATIONS']
    
    for section_name in section_order:
        if section_name not in sections:
            continue
        
        items = sections[section_name]
        if not items:
            continue
        
        # Section Header with left accent bar
        section_para = Paragraph(section_name, section_header_style)
        elements.append(section_para)
        
        # Content rendering
        if section_name == 'SUMMARY':
            summary_text = ' '.join(items)
            clean_summary = _clean_text_reportlab(summary_text)
            if clean_summary:
                elements.append(Paragraph(clean_summary, normal_style))
        
        elif section_name == 'SKILLS':
            # Group skills better
            all_skills = ', '.join([item.lstrip('•-* ') for item in items if item.strip()])
            clean_skills = _clean_text_reportlab(all_skills)
            if clean_skills:
                elements.append(Paragraph(clean_skills, skill_style))
        
        elif section_name == 'EXPERIENCE':
            # Better job entry parsing
            i = 0
            while i < len(items):
                item = items[i].strip()
                if not item:
                    i += 1
                    continue
                
                # Job title/company line
                if len(item) < 100 and not item.startswith(('•', '-', '*')):
                    job_entry = _clean_text_reportlab(item)
                    elements.append(Paragraph(job_entry, job_title_style))
                    i += 1
                    
                    # Collect dates/company info and bullets
                    bullets = []
                    while i < len(items):
                        next_item = items[i].strip()
                        if not next_item:
                            i += 1
                            continue
                        
                        if next_item.startswith(('•', '-', '*')):
                            bullet_text = _clean_text_reportlab(next_item.lstrip('•-* '))
                            if bullet_text:
                                bullets.append(bullet_text)
                            i += 1
                        elif len(next_item) < 100 and not any(c.isdigit() for c in next_item[:10]):
                            # Subtitle (dates, company)
                            subtitle = _clean_text_reportlab(next_item)
                            elements.append(Paragraph(subtitle, job_subtitle_style))
                            i += 1
                            break
                        else:
                            break
                    
                    # Add bullets
                    for bullet in bullets:
                        elements.append(Paragraph(f"<bullet>•</bullet> {bullet}", bullet_style))
                    
                    elements.append(Spacer(1, 0.08*inch))
                else:
                    i += 1
        
        elif section_name == 'EDUCATION':
            # School info with better formatting
            i = 0
            while i < len(items):
                item = items[i].strip()
                if not item:
                    i += 1
                    continue
                
                if len(item) < 100 and not item.startswith(('•', '-', '*')):
                    school = _clean_text_reportlab(item)
                    elements.append(Paragraph(school, job_title_style))
                    i += 1
                    
                    # Collect degree and date
                    while i < len(items) and len(items[i].strip()) < 100:
                        detail = items[i].strip()
                        if detail:
                            clean_detail = _clean_text_reportlab(detail)
                            elements.append(Paragraph(clean_detail, job_subtitle_style))
                        i += 1
                    
                    elements.append(Spacer(1, 0.06*inch))
                else:
                    i += 1
        
        else:
            # Default handling for other sections
            for item in items:
                clean = _clean_text_reportlab(item.lstrip('•-* '))
                if clean:
                    if item.strip().startswith(('•', '-', '*')):
                        elements.append(Paragraph(f"<bullet>•</bullet> {clean}", bullet_style))
                    else:
                        elements.append(Paragraph(clean, normal_style))
        
        elements.append(Spacer(1, 0.1*inch))
    
    # ─── BUILD PDF ───────────────────────────────────────────────────────────
    
    doc.build(elements)
    logger.info(f"✅ Premium professional PDF generated: {output_path}")
    return output_path


def generate_pdf(resume_text: str, output_path: str, candidate_name: str = "Candidate") -> str:
    """
    Primary Entry Point: Use ReportLab PDF generation (cross-platform compatible).
    """
    # Generate PDF directly using ReportLab
    return generate_pdf_reportlab(resume_text, output_path, candidate_name)


def generate_docx(resume_text: str, output_path: str, candidate_name: str = "Candidate") -> str:
    """Helper to return path to the docx specifically."""
    return output_path.replace('.pdf', '.docx')
