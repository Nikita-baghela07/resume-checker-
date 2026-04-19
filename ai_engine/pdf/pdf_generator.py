import os
import re
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx2pdf import convert
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib import colors
import logging

logger = logging.getLogger(__name__)

# ─── PROFESSIONAL COLOR PALETTE ──────────────────────────────────────────────
PRIMARY_COLOR = colors.HexColor('#D95F2B')    # Burnt Orange (from modern design)
HEADER_COLOR = colors.HexColor('#1A1714')     # Dark text (from modern design)
ACCENT_COLOR = colors.HexColor('#1A7C4A')     # Green accent
LIGHT_TEXT = colors.HexColor('#6B6158')       # Gray text
DIVIDER_COLOR = colors.HexColor('#E5E0D8')    # Light divider

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
    # Better escaping for ReportLab
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
        
        # Check if this is a section header
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
    """PROFESSIONAL PDF generator using ReportLab with modern design."""
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        topMargin=0.4*inch, bottomMargin=0.4*inch,
        leftMargin=0.6*inch, rightMargin=0.6*inch
    )
    elements = []
    
    # CUSTOM STYLES - Professional formatting
    title_style = ParagraphStyle(
        'Title',
        fontSize=24,
        textColor=PRIMARY_COLOR,
        spaceAfter=2,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    section_header_style = ParagraphStyle(
        'SectionHeader',
        fontSize=12,
        textColor=PRIMARY_COLOR,
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold',
        leftIndent=0
    )
    
    subsection_style = ParagraphStyle(
        'Subsection',
        fontSize=11,
        textColor=HEADER_COLOR,
        spaceAfter=2,
        spaceBefore=6,
        fontName='Helvetica-Bold'
    )
    
    bullet_style = ParagraphStyle(
        'Bullet',
        fontSize=10,
        leading=12,
        leftIndent=20,
        spaceAfter=4,
        textColor=LIGHT_TEXT,
        fontName='Helvetica',
        bulletIndent=10
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        fontSize=10,
        leading=12,
        spaceAfter=4,
        textColor=LIGHT_TEXT,
        fontName='Helvetica'
    )
    
    # HEADER
    elements.append(Paragraph(_clean_text_reportlab(candidate_name.upper()), title_style))
    elements.append(Spacer(1, 0.15*inch))
    
    # DIVIDER LINE
    divider = HRFlowable(width="100%", thickness=2, color=PRIMARY_COLOR, spaceAfter=12)
    elements.append(divider)
    
    # Parse and render sections
    sections = _parse_resume_sections(resume_text)
    section_order = ['SUMMARY', 'EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS', 'CERTIFICATIONS']
    
    for section_name in section_order:
        if section_name not in sections:
            continue
        
        items = sections[section_name]
        if not items:
            continue
        
        # Section Header
        elements.append(Paragraph(section_name, section_header_style))
        
        # Section Content
        if section_name == 'SKILLS':
            # Skills in comma-separated or bullet format
            for item in items:
                clean_item = _clean_text_reportlab(item.lstrip('•-* '))
                if clean_item:
                    elements.append(Paragraph(f"<bullet>•</bullet> {clean_item}", bullet_style))
        
        elif section_name == 'EXPERIENCE':
            # Parse job entries (Company/Title, Date, Bullets)
            i = 0
            while i < len(items):
                item = items[i].strip()
                if not item:
                    i += 1
                    continue
                
                # Check if this looks like a job title/company
                if len(item) < 100 and not item.startswith('•'):
                    elements.append(Paragraph(_clean_text_reportlab(item), subsection_style))
                    i += 1
                    
                    # Collect bullets for this job
                    while i < len(items):
                        next_item = items[i].strip()
                        if next_item.startswith('•') or next_item.startswith('-') or next_item.startswith('*'):
                            bullet_text = _clean_text_reportlab(next_item.lstrip('•-* '))
                            if bullet_text:
                                elements.append(
                                    Paragraph(f"<bullet>•</bullet> {bullet_text}", bullet_style)
                                )
                            i += 1
                        elif len(next_item) < 100 and next_item and not next_item[0].isdigit():
                            # Next job entry
                            break
                        else:
                            i += 1
                    
                    elements.append(Spacer(1, 0.08*inch))
                else:
                    i += 1
        
        elif section_name == 'EDUCATION':
            # School, Degree, Date format
            i = 0
            while i < len(items):
                item = items[i].strip()
                if not item:
                    i += 1
                    continue
                
                if len(item) < 100 and not item.startswith('•'):
                    elements.append(Paragraph(_clean_text_reportlab(item), subsection_style))
                    i += 1
                    
                    # Collect details
                    while i < len(items) and len(items[i].strip()) < 100:
                        detail = items[i].strip()
                        if detail:
                            elements.append(Paragraph(_clean_text_reportlab(detail), normal_style))
                        i += 1
                    
                    elements.append(Spacer(1, 0.06*inch))
                else:
                    i += 1
        
        else:
            # Default: bullets or items
            for item in items:
                clean = _clean_text_reportlab(item.lstrip('•-* '))
                if clean:
                    if item.strip().startswith(('•', '-', '*')):
                        elements.append(Paragraph(f"<bullet>•</bullet> {clean}", bullet_style))
                    else:
                        elements.append(Paragraph(clean, normal_style))
        
        elements.append(Spacer(1, 0.08*inch))
    
    # Build PDF
    doc.build(elements)
    logger.info(f"✅ Professional PDF generated: {output_path}")
    return output_path

def generate_pdf(resume_text: str, output_path: str, candidate_name: str = "Candidate") -> str:
    """
    Primary Entry Point: Use Word Pipeline if possible, fallback to ReportLab on Linux.
    """
    docx_path = output_path.replace('.pdf', '.docx')
    
    # 1. Generate the professional Word Doc (python-docx works everywhere)
    try:
        doc = Document()
        # Narrow margins
        for section in doc.sections:
            section.top_margin = section.bottom_margin = Inches(0.5)
            section.left_margin = section.right_margin = Inches(0.7)
            
        # Header
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(candidate_name.upper())
        run.font.size = Pt(20); run.font.bold = True; run.font.color.rgb = RGBColor(17, 34, 68)
        
        # Body logic simplified for brevity
        headers = ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS', 'SUMMARY']
        for line in resume_text.split('\n'):
            stripped = line.strip()
            if not stripped: continue
            if any(h in stripped.upper() for h in headers) and len(stripped) < 40:
                h_para = doc.add_paragraph()
                run = h_para.add_run(stripped.upper())
                run.font.size = Pt(13); run.font.bold = True; run.font.color.rgb = RGBColor(17, 34, 68)
            elif stripped.startswith(('-', '*', '•')):
                doc.add_paragraph(stripped.lstrip('-*• '), style='List Bullet')
            else:
                doc.add_paragraph(stripped)
                
        doc.save(docx_path)
    except Exception as e:
        logger.error(f"DOCX Creation error: {e}")

    # 2. Attempt Word -> PDF conversion (Only works on Windows/Mac with Word installed)
    try:
        convert(docx_path, output_path)
        if os.path.exists(output_path):
            return output_path
    except Exception as e:
        logger.warning(f"⚠️ docx2pdf failed: {e}. Falling back to ReportLab...")

    # 3. Final Fallback: Generate PDF using ReportLab (Ensures a PDF is ALWAYS returned)
    return generate_pdf_reportlab(resume_text, output_path, candidate_name)

def generate_docx(resume_text: str, output_path: str, candidate_name: str = "Candidate") -> str:
    """Helper to return path to the docx specifically."""
    return output_path.replace('.pdf', '.docx')
