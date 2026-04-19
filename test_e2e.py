#!/usr/bin/env python3
"""
Test script to verify the full OptiResume pipeline works end-to-end
Tests: Upload, Optimize, Score Improvement, PDF Download
"""

import requests
import json
import time
import sys

# Configuration
BACKEND_URL = 'http://localhost:8000'
API_BASE = f'{BACKEND_URL}/api/v1'

# Test data
TEST_RESUME = """
JOHN DOE
john@example.com | +91 9876543210

EXPERIENCE
Software Developer Intern - XYZ Tech
2023 - Present
- Worked on the backend of a web application
- Did some coding in Python  
- Worked with the database team
- Helped fix bugs in the existing codebase
- Made a small API
- Wrote code using Python and JavaScript

SKILLS
Languages: Python, JavaScript, Java
Databases: MySQL, SQLite
"""

TEST_JD = """
Senior Backend Engineer - ABC Corp
Required: Python, FastAPI, PostgreSQL, Docker, CI/CD, REST APIs, Kubernetes
Responsibilities: Design scalable backend systems, build RESTful APIs, optimize database performance
"""

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def test_health():
    """Test backend health check"""
    print_header("1. Testing Backend Health")
    try:
        resp = requests.get(f'{BACKEND_URL}/health', timeout=5)
        if resp.status_code == 200:
            print("✅ Backend is healthy")
            print(f"   Response: {resp.json()}")
            return True
        else:
            print(f"❌ Backend returned status {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to backend: {e}")
        return False

def test_optimize():
    """Test the optimization endpoint"""
    print_header("2. Testing Optimization Pipeline")
    try:
        print("📤 Sending optimization request...")
        print(f"   Resume length: {len(TEST_RESUME)} chars")
        print(f"   Job description length: {len(TEST_JD)} chars")
        
        response = requests.post(
            f'{API_BASE}/optimize',
            json={
                'resume_text': TEST_RESUME,
                'job_description': TEST_JD
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Optimization failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return None
        
        data = response.json()
        print("✅ Optimization successful!")
        
        # Parse scores
        initial_score = data.get('scores', {}).get('initial', {}).get('overall', 0)
        optimized_score = data.get('scores', {}).get('optimized', {}).get('overall', 0)
        improvement = optimized_score - initial_score
        
        print(f"\n   📊 SCORE ANALYSIS")
        print(f"   Initial Score:   {initial_score:.1f}%")
        print(f"   Optimized Score: {optimized_score:.1f}%")
        print(f"   Improvement:     +{improvement:.1f}% {'✅ IMPROVED!' if improvement > 0 else '❌ NO IMPROVEMENT'}")
        
        # Parse skill gaps
        skill_gaps = data.get('skill_gaps', [])
        print(f"\n   🔍 SKILL GAPS")
        high = [s for s in skill_gaps if s.get('priority') == 'high']
        med = [s for s in skill_gaps if s.get('priority') == 'medium']
        low = [s for s in skill_gaps if s.get('priority') == 'low']
        print(f"   High Priority: {len(high)} - {[s['skill'] for s in high]}")
        print(f"   Medium:        {len(med)} - {[s['skill'] for s in med]}")
        print(f"   Low:           {len(low)} - {[s['skill'] for s in low]}")
        
        # Parse diffs
        diffs = data.get('diff', [])
        changed = [d for d in diffs if d.get('changed')]
        print(f"\n   📝 IMPROVEMENTS")
        print(f"   Total bullets:    {len(diffs)}")
        print(f"   Improved bullets: {len(changed)}")
        
        if changed:
            print(f"\n   Sample improvement:")
            sample = changed[0]
            print(f"   Original: {sample.get('original', '')[:70]}...")
            print(f"   Optimized: {sample.get('optimized', '')[:70]}...")
        
        return data
        
    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        return None

def test_download(optimized_resume):
    """Test PDF download"""
    print_header("3. Testing PDF Download")
    try:
        print("📥 Requesting PDF download...")
        response = requests.post(
            f'{API_BASE}/download',
            json={
                'optimized_resume': optimized_resume,
                'candidate_name': 'Test Candidate'
            },
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Download failed with status {response.status_code}")
            return False
        
        content_type = response.headers.get('content-type', '')
        if 'pdf' in content_type.lower():
            file_size = len(response.content)
            print(f"✅ PDF generated successfully!")
            print(f"   File size: {file_size} bytes")
            
            # Save to disk for verification
            with open('test_output.pdf', 'wb') as f:
                f.write(response.content)
            print(f"   Saved to: test_output.pdf")
            return True
        else:
            print(f"❌ Unexpected content type: {content_type}")
            return False
            
    except Exception as e:
        print(f"❌ Error during download: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  OptiResume AI - Backend E2E Test Suite")
    print("="*60)
    
    # Test 1: Health
    if not test_health():
        print("\n❌ Backend not available. Start it with: python run.py")
        return False
    
    # Test 2: Optimization
    results = test_optimize()
    if not results:
        return False
    
    # Check if score improved
    improvement = results.get('scores', {}).get('optimized', {}).get('overall', 0) - results.get('scores', {}).get('initial', {}).get('overall', 0)
    if improvement <= 0:
        print("\n⚠️  WARNING: Score did not improve!")
        print("   This might indicate the semantic validation threshold is too strict.")
        return False
    
    # Test 3: Download
    optimized_resume = results.get('optimized_resume', '')
    if not test_download(optimized_resume):
        return False
    
    # Summary
    print_header("✅ ALL TESTS PASSED!")
    print(f"Backend is fully functional and ready for production deployment.")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
