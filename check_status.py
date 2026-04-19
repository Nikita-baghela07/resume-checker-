"""Test current state of UI and APIs"""
import requests
import sys

print("=" * 70)
print("🔍 CHECKING CURRENT STATE")
print("=" * 70)

# Test local backend
print("\n1️⃣ LOCAL BACKEND (localhost:8000)")
try:
    r = requests.get("http://localhost:8000/", timeout=3)
    print(f"   ✅ Root endpoint: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   Service: {data.get('service')}")
except Exception as e:
    print(f"   ❌ Not running: {e}")

# Test local frontend
print("\n2️⃣ LOCAL FRONTEND (localhost:5175)")
try:
    r = requests.get("http://localhost:5175/", timeout=3)
    print(f"   ✅ Frontend: {r.status_code}")
except Exception as e:
    print(f"   ❌ Not running: {e}")

# Test production frontend
print("\n3️⃣ PRODUCTION FRONTEND (Vercel)")
try:
    r = requests.get("https://resume-checker-h4mi.vercel.app/", timeout=5)
    print(f"   ✅ Status: {r.status_code}")
    if r.status_code == 200:
        # Check if modern CSS is loaded
        if "F8F6F2" in r.text or "D95F2B" in r.text or "modern.css" in r.text:
            print("   ✅ Modern CSS colors found in HTML")
        else:
            print("   ⚠️ Modern CSS colors NOT found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test production backend
print("\n4️⃣ PRODUCTION BACKEND (Render)")
try:
    r = requests.get("https://optiresume-ai-backend-payw.onrender.com/", timeout=5)
    print(f"   Root: {r.status_code}")
except Exception as e:
    print(f"   ❌ Root: {str(e)[:30]}")

try:
    r = requests.get("https://optiresume-ai-backend-payw.onrender.com/api/v1/health", timeout=5)
    print(f"   Health: {r.status_code}")
except Exception as e:
    print(f"   ❌ Health: {str(e)[:30]}")

try:
    r = requests.post("https://optiresume-ai-backend-payw.onrender.com/api/v1/optimize", 
                      json={"resume_text": "test", "job_description": "test"}, timeout=5)
    print(f"   Optimize: {r.status_code}")
except Exception as e:
    print(f"   ❌ Optimize: {str(e)[:30]}")

print("\n" + "=" * 70)
