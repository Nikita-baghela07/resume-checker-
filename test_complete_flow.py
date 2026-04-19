"""
Complete end-to-end test: Login → Upload PDF → Optimize → Download
"""
import requests
import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.units import inch
import time

BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5177"

# Test resume with 3000+ characters
TEST_RESUME_TEXT = """JOHN DOE
john.doe@email.com | LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe
Seattle, WA | (206) 555-0123

PROFESSIONAL SUMMARY
Experienced Full-Stack Software Engineer with 8+ years of expertise in designing, developing, and deploying scalable web applications. Proven track record of leading high-performing teams, architecting microservices, and implementing cloud-based solutions. Proficient in modern web technologies including React, Node.js, Python, and cloud platforms like AWS and Google Cloud. Passionate about writing clean, maintainable code and mentoring junior developers.

TECHNICAL SKILLS
Programming Languages: Python, JavaScript, TypeScript, Java, SQL, Go, Bash
Frontend Technologies: React, Vue.js, Angular, Redux, GraphQL, Webpack, Vite
Backend Frameworks: Node.js, Express.js, FastAPI, Django, Spring Boot
Databases: PostgreSQL, MongoDB, Redis, Elasticsearch, DynamoDB
Cloud Platforms: AWS (EC2, S3, Lambda, RDS), Google Cloud Platform, Azure
DevOps & Tools: Docker, Kubernetes, Jenkins, GitHub Actions, GitLab CI/CD
Other Tools: Git, JIRA, Webpack, Babel, ESLint, Linux, Apache, Nginx

PROFESSIONAL EXPERIENCE

Senior Software Engineer
TechCorp Solutions, Seattle, WA | Jan 2021 – Present
• Led development of microservices architecture serving 2M+ daily active users, improving system performance by 40%
• Designed and implemented event-driven architecture using Kafka and RabbitMQ for real-time data processing
• Mentored team of 5 junior developers, conducting code reviews and establishing best practices for REST API design
• Architected CI/CD pipeline using GitHub Actions and Docker, reducing deployment time from 2 hours to 15 minutes
• Optimized PostgreSQL queries resulting in 60% reduction in database query time
• Implemented comprehensive monitoring using Prometheus and Grafana, reducing incident response time by 50%

Software Engineer (Full-Stack)
DataFlow Inc., San Francisco, CA | Jun 2018 – Dec 2020
• Built React-based dashboard processing 500K+ events per day with real-time updates using WebSocket
• Developed RESTful APIs using Express.js and Node.js handling 10K+ requests per second
• Implemented authentication and authorization using JWT and OAuth 2.0
• Created automated testing suite with 85% code coverage using Jest and Cypress
• Deployed applications on AWS using EC2, S3, and CloudFront, managing infrastructure for 50M+ monthly visitors
• Collaborated with product team to design and implement new features, increasing user engagement by 35%

Junior Software Engineer
StartupXYZ, San Francisco, CA | Jan 2017 – May 2018
• Developed full-stack web application using React, Node.js, and MongoDB for e-commerce platform
• Implemented payment processing integration with Stripe API
• Wrote unit and integration tests using Jest, achieving 80% code coverage
• Participated in agile development using Scrum, attending daily standups and sprint planning

EDUCATION
Bachelor of Science in Computer Science
University of Washington, Seattle, WA | Graduated: May 2016
GPA: 3.8/4.0 | Dean's List: All semesters

CERTIFICATIONS & ACHIEVEMENTS
AWS Certified Solutions Architect – Associate (2020)
Google Cloud Professional Data Engineer (2021)
Recipient of "Employee of the Year" award at TechCorp Solutions (2022)
Speaker at React Conference 2023, presenting "Scaling React Applications"

ADDITIONAL PROJECTS
Open Source Contributions: Active contributor to React framework and several Node.js libraries
Personal Projects: Built full-stack blog platform and REST API documentation tool
Technical Writing: Published 15+ articles on Medium about web development and system design"""

JOB_DESCRIPTION = """Senior Backend Developer

Requirements:
- 5+ years of experience with Python and backend development
- Strong knowledge of FastAPI, Node.js, and microservices architecture
- Experience with PostgreSQL, MongoDB, and distributed databases
- Proficiency in Docker, Kubernetes, and AWS cloud services
- Understanding of system design and scalability patterns
- Experience with REST APIs, GraphQL, and event-driven architectures

Responsibilities:
- Design and develop scalable backend systems handling millions of requests
- Lead architecture discussions and technical planning
- Implement automated testing and CI/CD pipelines
- Mentor junior developers and conduct code reviews
- Collaborate with product and frontend teams on feature development
- Optimize database queries and system performance"""

def create_test_pdf(filename="test_resume.pdf"):
    """Create a simple PDF from the test resume text"""
    print(f"\n1. Creating test PDF: {filename}")
    
    doc = SimpleDocTemplate(filename, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Add resume text as paragraphs
    for line in TEST_RESUME_TEXT.split('\n'):
        if line.strip():
            if line.isupper() and len(line) < 50:
                style = styles['Heading2']
            else:
                style = styles['Normal']
            story.append(Paragraph(line, style))
        else:
            story.append(Spacer(1, 0.2*inch))
    
    doc.build(story)
    print(f"   [OK] PDF created: {Path(filename).absolute()}")
    print(f"   [OK] File size: {Path(filename).stat().st_size} bytes")
    return filename

def test_upload_pdf(pdf_file):
    """Upload PDF to backend"""
    print(f"\n2. Uploading PDF to backend")
    
    with open(pdf_file, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/v1/upload", files=files, timeout=30)
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] Upload successful")
        print(f"   [OK] Extracted text length: {len(data.get('resume_text', ''))} characters")
        print(f"   [OK] Preview: {data.get('resume_text', '')[:100]}...")
        return data
    else:
        print(f"   [ERROR] Upload failed: {response.text}")
        raise Exception("Upload failed")

def test_optimize_resume(resume_text, job_description):
    """Optimize resume against job description"""
    print(f"\n3. Optimizing resume against job description")
    
    payload = {
        "resume_text": resume_text,
        "job_description": job_description
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/optimize", json=payload, timeout=120)
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   [OK] Optimization successful")
        print(f"   [OK] Initial score: {data['scores']['initial']['overall']}%")
        print(f"   [OK] Optimized score: {data['scores']['optimized']['overall']}%")
        improvement = data['scores']['optimized']['overall'] - data['scores']['initial']['overall']
        print(f"   [OK] Improvement: {improvement:+.1f}%")
        print(f"   [OK] Skill gaps found: {len(data.get('skill_gaps', []))}")
        return data
    else:
        print(f"   [ERROR] Optimization failed: {response.text}")
        raise Exception("Optimization failed")

def test_download_pdf(optimized_resume, candidate_name="John_Doe"):
    """Download optimized resume as PDF"""
    print(f"\n4. Downloading optimized resume as PDF")
    
    payload = {
        "optimized_resume": optimized_resume,
        "candidate_name": candidate_name
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/download", json=payload, timeout=30)
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        output_file = "optimized_resume.pdf"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        
        file_size = Path(output_file).stat().st_size
        print(f"   [OK] Download successful")
        print(f"   [OK] PDF saved: {Path(output_file).absolute()}")
        print(f"   [OK] File size: {file_size} bytes")
        return output_file
    else:
        print(f"   [ERROR] Download failed: {response.status_code}")
        print(f"   [ERROR] Response: {response.text}")
        raise Exception("Download failed")

def run_complete_flow():
    """Run the complete end-to-end flow"""
    print("="*60)
    print("COMPLETE END-TO-END TEST")
    print("="*60)
    
    try:
        # Step 1: Create PDF
        pdf_file = create_test_pdf()
        
        # Step 2: Upload PDF
        upload_result = test_upload_pdf(pdf_file)
        resume_text = upload_result['resume_text']
        
        # Step 3: Optimize
        optimize_result = test_optimize_resume(resume_text, JOB_DESCRIPTION)
        
        # Step 4: Download optimized PDF
        download_file = test_download_pdf(optimize_result['optimized_resume'])
        
        print("\n" + "="*60)
        print("SUCCESS! Complete flow executed:")
        print("="*60)
        print(f"[OK] Test resume PDF created and uploaded")
        print(f"[OK] Optimization completed (score: {optimize_result['scores']['initial']['overall']}% -> {optimize_result['scores']['optimized']['overall']}%)")
        print(f"[OK] Optimized PDF downloaded to: {download_file}")
        print(f"\nFrontend URL: {FRONTEND_URL}")
        print(f"Backend API: {BASE_URL}/docs")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        raise

if __name__ == "__main__":
    run_complete_flow()
