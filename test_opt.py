"""Test optimization with proper data"""
import requests
import json

print("=" * 70)
print("🧪 TESTING OPTIMIZATION WITH REAL DATA")
print("=" * 70)

# Test data
resume = """
John Doe
Senior Software Engineer

EXPERIENCE
Software Engineer at TechCorp (2020-2024)
- Developed Python microservices handling 1M+ requests/day
- Built real-time dashboards using React and D3.js
- Reduced API response time by 40% through optimization
- Led team of 5 engineers

SKILLS
Python, JavaScript, React, FastAPI, PostgreSQL, Docker, AWS

EDUCATION
B.S. Computer Science, State University (2020)
"""

job_desc = """
Senior Backend Engineer
- 5+ years Python development
- Experience with FastAPI/Django
- Database optimization
- Team leadership
- AWS cloud experience
"""

print("\n📍 Testing LOCAL backend...")
try:
    r = requests.post("http://localhost:8000/api/v1/optimize", 
                      json={"resume_text": resume, "job_description": job_desc}, 
                      timeout=20)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print("   ✅ OPTIMIZATION WORKING!")
        print(f"   Initial Score: {data['scores']['initial'].get('overall', 'N/A')}")
        print(f"   Optimized Score: {data['scores']['optimized'].get('overall', 'N/A')}")
    elif r.status_code == 422:
        print(f"   ❌ Validation Error: {r.json()}")
    else:
        print(f"   Response: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n📍 Testing PRODUCTION backend...")
try:
    r = requests.post("https://optiresume-ai-backend-payw.onrender.com/api/v1/optimize", 
                      json={"resume_text": resume, "job_description": job_desc}, 
                      timeout=20)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print("   ✅ OPTIMIZATION WORKING!")
        print(f"   Initial Score: {data['scores']['initial'].get('overall', 'N/A')}")
        print(f"   Optimized Score: {data['scores']['optimized'].get('overall', 'N/A')}")
    elif r.status_code == 422:
        print(f"   ❌ Validation Error: {r.json()}")
    else:
        print(f"   Response: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
