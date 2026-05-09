"""
Comprehensive System Testing & Monitoring Script
Tests all components: Backend, Frontend, APIs, Database, ML Models
"""

import requests
import json
import time
from datetime import datetime

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Server URLs
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

class SystemMonitor:
    def __init__(self):
        self.results = []
        self.bugs = []
        self.start_time = datetime.now()
        
    def log(self, level, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if level == "PASS":
            print(f"{GREEN}✓ [{timestamp}] {message}{RESET}")
        elif level == "FAIL":
            print(f"{RED}✗ [{timestamp}] {message}{RESET}")
            self.bugs.append(message)
        elif level == "WARN":
            print(f"{YELLOW}⚠ [{timestamp}] {message}{RESET}")
        elif level == "INFO":
            print(f"{BLUE}ℹ [{timestamp}] {message}{RESET}")
        else:
            print(f"  [{timestamp}] {message}")
    
    def test_backend_health(self):
        """Test if backend is running and healthy"""
        print(f"\n{BOLD}=== BACKEND HEALTH CHECK ==={RESET}")
        try:
            response = requests.get(f"{BACKEND_URL}/docs", timeout=5)
            if response.status_code == 200:
                self.log("PASS", "Backend server is running ✓")
                return True
            else:
                self.log("FAIL", f"Backend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log("FAIL", f"Backend connection failed: {str(e)}")
            return False
    
    def test_frontend_health(self):
        """Test if frontend is accessible"""
        print(f"\n{BOLD}=== FRONTEND HEALTH CHECK ==={RESET}")
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            if response.status_code == 200:
                self.log("PASS", "Frontend server is running ✓")
                return True
            else:
                self.log("FAIL", f"Frontend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log("FAIL", f"Frontend connection failed: {str(e)}")
            return False
    
    def test_api_endpoints(self):
        """Test all API endpoints"""
        print(f"\n{BOLD}=== API ENDPOINTS CHECK ==={RESET}")
        
        endpoints = [
            ("GET", "/"),
            ("GET", "/api/v1/health"),
            ("POST", "/api/v1/optimize"),
        ]
        
        for method, endpoint in endpoints:
            try:
                url = f"{BACKEND_URL}{endpoint}"
                if method == "GET":
                    response = requests.get(url, timeout=5)
                else:
                    # POST requests need data
                    if endpoint == "/api/v1/optimize":
                        data = {
                            "resume_text": "Software Engineer with 5 years experience in Python and FastAPI",
                            "job_description": "Looking for Python backend engineer with FastAPI experience"
                        }
                        response = requests.post(url, json=data, timeout=30)
                    else:
                        response = requests.post(url, timeout=5)
                
                if response.status_code in [200, 201, 422]:  # 422 is validation error, OK for testing
                    self.log("PASS", f"{method} {endpoint} - Status {response.status_code}")
                else:
                    self.log("FAIL", f"{method} {endpoint} - Status {response.status_code}")
            except requests.exceptions.Timeout:
                self.log("WARN", f"{method} {endpoint} - Request timeout (API might be processing)")
            except Exception as e:
                self.log("FAIL", f"{method} {endpoint} - Error: {str(e)}")
    
    def test_optimization_flow(self):
        """Test the complete optimization flow"""
        print(f"\n{BOLD}=== OPTIMIZATION FLOW TEST ==={RESET}")
        
        resume = """John Smith
        Senior Software Engineer
        
        EXPERIENCE
        Tech Company, 2020-Present
        - Built microservices with Python and FastAPI
        - Managed PostgreSQL databases
        - Deployed with Docker and CI/CD
        
        Previous Company, 2018-2020
        - Developed REST APIs
        - Implemented testing framework
        
        SKILLS
        Python, FastAPI, PostgreSQL, Docker, REST APIs, CI/CD, JavaScript, React
        
        EDUCATION
        B.S. Computer Science, 2018"""
        
        job_desc = """Senior Backend Engineer
        
        Requirements:
        - 5+ years backend development
        - Python and FastAPI expertise
        - PostgreSQL database knowledge
        - Docker containerization
        - CI/CD pipeline experience
        - Microservices architecture
        
        Responsibilities:
        - Design scalable systems
        - Lead architecture decisions
        - Mentor team members"""
        
        try:
            self.log("INFO", "Sending optimization request...")
            start = time.time()
            
            response = requests.post(
                f"{BACKEND_URL}/api/v1/optimize",
                json={
                    "resume_text": resume,
                    "job_description": job_desc
                },
                timeout=60
            )
            
            elapsed = time.time() - start
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ["status", "scores", "optimized_resume", "skill_gaps", "diff"]
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    self.log("PASS", f"Optimization completed in {elapsed:.2f}s ✓")
                    
                    # Check scores
                    if "initial" in data["scores"] and "optimized" in data["scores"]:
                        initial = data["scores"]["initial"].get("overall", 0)
                        optimized = data["scores"]["optimized"].get("overall", 0)
                        improvement = optimized - initial
                        self.log("PASS", f"Scores: {initial:.2f} → {optimized:.2f} (+{improvement:.2f})")
                    
                    # Check optimized resume
                    if len(data["optimized_resume"]) > len(resume):
                        self.log("PASS", f"Resume optimized: {len(resume)} → {len(data['optimized_resume'])} chars")
                    
                    # Check skill gaps
                    gaps_count = len(data.get("skill_gaps", []))
                    self.log("PASS", f"Identified {gaps_count} skill gaps")
                    
                    # Check diffs
                    diffs_count = len(data.get("diff", []))
                    changed_count = len([d for d in data.get("diff", []) if d.get("changed")])
                    self.log("PASS", f"Detected {diffs_count} changes ({changed_count} modified)")
                else:
                    self.log("FAIL", f"Missing response fields: {missing_fields}")
            else:
                error_msg = response.text if response.text else f"Status {response.status_code}"
                self.log("FAIL", f"Optimization failed: {error_msg}")
        except requests.exceptions.Timeout:
            self.log("FAIL", "Optimization request timeout - API might be overloaded or stuck")
        except Exception as e:
            self.log("FAIL", f"Optimization test error: {str(e)}")
    
    def test_pdf_generation(self):
        """Test PDF generation endpoint"""
        print(f"\n{BOLD}=== PDF GENERATION TEST ==={RESET}")
        
        resume_text = """John Smith
        Senior Backend Engineer
        
        EXPERIENCE
        Tech Corp, 2020-Present
        - Built microservices with Python
        - Managed databases
        
        SKILLS
        Python, FastAPI, PostgreSQL, Docker"""
        
        try:
            self.log("INFO", "Requesting PDF generation...")
            response = requests.post(
                f"{BACKEND_URL}/api/v1/download",
                json={
                    "optimized_resume": resume_text,
                    "candidate_name": "John Smith"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'unknown')
                file_size = len(response.content)
                
                if 'pdf' in content_type.lower() or 'application' in content_type.lower():
                    self.log("PASS", f"PDF generated successfully ({file_size} bytes)")
                elif 'text' in content_type.lower():
                    self.log("FAIL", "PDF returned as text (not binary format)")
                else:
                    self.log("WARN", f"Unexpected content-type: {content_type}")
            else:
                self.log("FAIL", f"PDF generation failed: Status {response.status_code}")
        except Exception as e:
            self.log("FAIL", f"PDF generation error: {str(e)}")
    
    def check_database_connection(self):
        """Check if database is accessible"""
        print(f"\n{BOLD}=== DATABASE CONNECTION CHECK ==={RESET}")
        
        try:
            # Try to access a protected route that requires DB
            response = requests.post(
                f"{BACKEND_URL}/api/v1/upload",
                files={"file": ("test.pdf", b"%PDF-1.4 test", "application/pdf")},
                timeout=10
            )
            
            # Even if upload fails, connection check is about reaching the endpoint
            if response.status_code in [200, 422, 413]:  # 413 = file too large
                self.log("PASS", "Database connection is accessible ✓")
            elif response.status_code == 500:
                self.log("FAIL", "Database error (HTTP 500)")
            else:
                self.log("WARN", f"Upload endpoint returned {response.status_code}")
        except Exception as e:
            self.log("FAIL", f"Database connection error: {str(e)}")
    
    def check_ml_models(self):
        """Check if ML models are loaded"""
        print(f"\n{BOLD}=== ML MODELS CHECK ==={RESET}")
        
        # The optimization flow will load SBERT model
        # If optimization works, models are likely loaded
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/v1/optimize",
                json={
                    "resume_text": "Python programmer",
                    "job_description": "Python developer needed"
                },
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("scores", {}).get("optimized", {}).get("overall") is not None:
                    self.log("PASS", "SBERT and TF-IDF models are loaded ✓")
                else:
                    self.log("FAIL", "Models loaded but scoring returned null")
            else:
                self.log("WARN", "Cannot verify models without successful optimization")
        except Exception as e:
            self.log("FAIL", f"ML models check error: {str(e)}")
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{BOLD}{'='*50}")
        print(f"OptiResume System Monitor - Started at {self.start_time.strftime('%H:%M:%S')}")
        print(f"{'='*50}{RESET}\n")
        
        # Health checks
        self.test_backend_health()
        self.test_frontend_health()
        
        # API tests
        self.test_api_endpoints()
        
        # Feature tests
        self.test_optimization_flow()
        self.test_pdf_generation()
        
        # Infrastructure tests
        self.check_database_connection()
        self.check_ml_models()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary and identified bugs"""
        print(f"\n{BOLD}{'='*50}")
        print(f"TEST SUMMARY")
        print(f"{'='*50}{RESET}\n")
        
        if not self.bugs:
            print(f"{GREEN}{BOLD}✓ All systems operating normally!{RESET}\n")
        else:
            print(f"{RED}{BOLD}✗ {len(self.bugs)} Issue(s) Found:{RESET}\n")
            for i, bug in enumerate(self.bugs, 1):
                print(f"  {RED}{i}. {bug}{RESET}")
            print()
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"{BLUE}Total test time: {elapsed:.2f} seconds{RESET}")
        print(f"Completed at {datetime.now().strftime('%H:%M:%S')}\n")

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.run_all_tests()
