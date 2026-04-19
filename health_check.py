#!/usr/bin/env python3
"""
🔍 OptiResume System Health Check
Verifies local and production deployments
"""

import requests
import sys
from typing import Dict, Tuple

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_endpoint(url: str, label: str, timeout: int = 5) -> Tuple[bool, str]:
    """Check if an endpoint is accessible"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True, f"{GREEN}✅{RESET} {label}: OK (Status {response.status_code})"
        else:
            return False, f"{RED}❌{RESET} {label}: Status {response.status_code}"
    except requests.exceptions.ConnectTimeout:
        return False, f"{RED}❌{RESET} {label}: Connection timeout (service might be sleeping)"
    except requests.exceptions.ConnectionError:
        return False, f"{RED}❌{RESET} {label}: Connection refused (service not running)"
    except Exception as e:
        return False, f"{RED}❌{RESET} {label}: {str(e)}"

def check_cors_header(url: str, origin: str) -> Tuple[bool, str]:
    """Check if CORS headers are properly set"""
    try:
        headers = {'Origin': origin}
        response = requests.get(url, headers=headers, timeout=5)
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        
        if cors_header == origin or cors_header == '*':
            return True, f"{GREEN}✅{RESET} CORS for {origin}: OK"
        else:
            return False, f"{RED}❌{RESET} CORS for {origin}: Missing or incorrect ({cors_header})"
    except Exception as e:
        return False, f"{RED}❌{RESET} CORS check failed: {str(e)}"

def test_local_setup():
    """Test local development setup"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🏠 LOCAL DEVELOPMENT SETUP{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    tests = [
        ("http://localhost:8000/health", "Backend (Port 8000)"),
        ("http://localhost:5174", "Frontend (Port 5174)"),
    ]
    
    results = []
    for url, label in tests:
        success, message = check_endpoint(url, label)
        results.append((success, message))
        print(message)
    
    if all(r[0] for r in results):
        print(f"\n{GREEN}✅ Local setup is WORKING{RESET}")
        return True
    else:
        print(f"\n{YELLOW}⚠️  Local setup has issues{RESET}")
        return False

def test_production_setup():
    """Test production setup (Vercel + Render)"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}🚀 PRODUCTION SETUP (VERCEL + RENDER){RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    backend_url = "https://optiresume-ai-backend-payw.onrender.com"
    frontend_url = "https://resume-checker-h4mi.vercel.app"
    
    print("Backend Tests:")
    backend_ok, msg = check_endpoint(f"{backend_url}/health", "Backend Health", timeout=10)
    print(msg)
    
    if backend_ok:
        print("\nCORS Tests (from Vercel):")
        cors_ok, msg = check_cors_header(f"{backend_url}/health", frontend_url)
        print(msg)
    else:
        print(f"\n{YELLOW}⚠️  Skipping CORS tests - backend not responding{RESET}")
        cors_ok = False
    
    print("\nFrontend Tests:")
    frontend_ok, msg = check_endpoint(frontend_url, "Frontend", timeout=10)
    print(msg)
    
    print(f"\n{BLUE}Production Status:{RESET}")
    print(f"  Backend:  {'🟢 Live' if backend_ok else '🔴 Down/Sleeping'}")
    print(f"  CORS:     {'🟢 OK' if cors_ok else '🟡 Check Render env vars'}")
    print(f"  Frontend: {'🟢 Live' if frontend_ok else '🔴 Down'}")
    
    if backend_ok and frontend_ok:
        print(f"\n{GREEN}✅ Production setup looks good!{RESET}")
        if not cors_ok:
            print(f"{YELLOW}⚠️  Note: CORS headers not properly set. Check Render environment variables.{RESET}")
        return True
    else:
        print(f"\n{YELLOW}⚠️  Production has issues. See RENDER_SETUP.md for fixes.{RESET}")
        return False

def main():
    """Run all tests"""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}📊 OptiResume System Health Check{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    local_ok = test_local_setup()
    prod_ok = test_production_setup()
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}📋 SUMMARY{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    print(f"Local Development:  {GREEN if local_ok else RED}{'✅ OK' if local_ok else '❌ ISSUES'}{RESET}")
    print(f"Production Deploy:  {GREEN if prod_ok else RED}{'✅ OK' if prod_ok else '❌ ISSUES'}{RESET}\n")
    
    if not local_ok:
        print(f"{YELLOW}💡 To fix local setup:{RESET}")
        print("   1. Terminal 1: cd backend && python run.py")
        print("   2. Terminal 2: cd frontend && npm run dev")
        print("   3. Open http://localhost:5174\n")
    
    if not prod_ok:
        print(f"{YELLOW}💡 To fix production:{RESET}")
        print("   1. Check RENDER_SETUP.md for detailed instructions")
        print("   2. Verify Render environment variables are set")
        print("   3. Check Vercel has VITE_API_URL environment variable\n")
    
    if local_ok and prod_ok:
        print(f"{GREEN}🎉 All systems operational!{RESET}\n")
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
