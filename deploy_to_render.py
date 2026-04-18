#!/usr/bin/env python3
"""
Automated Render Deployment Script for OptiResume AI Backend
Run this script to deploy your backend to Render with one command
"""

import subprocess
import sys
import json
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# Get these from environment variables or user input
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
RENDER_API_TOKEN = os.getenv("RENDER_API_TOKEN", "")

# These are already set correctly
SERVICE_NAME = "optiresume-ai-backend"
GITHUB_REPO = "https://github.com/Nikita-baghela07/resume-checker-.git"
BRANCH = "main"
RUNTIME = "python-3.11"

# ============================================================================
# DEPLOYMENT CONFIGURATION
# ============================================================================

DEPLOYMENT_CONFIG = {
    "name": SERVICE_NAME,
    "type": "web_service",
    "repo": GITHUB_REPO,
    "branch": BRANCH,
    "runtime": RUNTIME,
    "buildCommand": "pip install -r backend/requirements-deploy.txt",
    "startCommand": "cd backend && gunicorn -w 2 -b 0.0.0.0:8000 --timeout 120 --access-logfile - app.main:app",
    "envVars": [
        {
            "key": "GROQ_API_KEY",
            "value": GROQ_API_KEY,
        },
        {
            "key": "ENABLE_SBERT_MODEL",
            "value": "false",  # Lightweight mode - saves 200MB
        },
        {
            "key": "ALLOWED_ORIGINS",
            "value": "http://localhost:5173,http://localhost:3000",
        },
        {
            "key": "PYTHONUNBUFFERED",
            "value": "1",
        },
    ],
    "region": "ohio",
    "plan": "free",  # Free tier with 512MB RAM
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")

def print_step(step_num, text):
    """Print step indicator"""
    print(f"[Step {step_num}] {text}")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def validate_config():
    """Validate configuration before deployment"""
    print_header("VALIDATING CONFIGURATION")
    
    errors = []
    
    # Check GROQ API Key
    if GROQ_API_KEY == "YOUR_GROQ_API_KEY_HERE" or not GROQ_API_KEY:
        errors.append("❌ GROQ_API_KEY not set")
    else:
        print_success(f"GROQ_API_KEY set (starts with: {GROQ_API_KEY[:10]}...)")
    
    # Check Render API Token
    if RENDER_API_TOKEN == "YOUR_RENDER_API_TOKEN_HERE" or not RENDER_API_TOKEN:
        errors.append("❌ RENDER_API_TOKEN not set")
    else:
        print_success(f"RENDER_API_TOKEN set (starts with: {RENDER_API_TOKEN[:10]}...)")
    
    # Check GitHub repo
    print_success(f"GitHub Repo: {GITHUB_REPO}")
    print_success(f"Branch: {BRANCH}")
    
    # Check backend files
    backend_path = Path("backend")
    if not backend_path.exists():
        errors.append("❌ 'backend' directory not found")
    else:
        req_file = backend_path / "requirements-deploy.txt"
        if not req_file.exists():
            errors.append("❌ 'backend/requirements-deploy.txt' not found")
        else:
            print_success("✓ backend/requirements-deploy.txt found")
    
    if errors:
        print_header("VALIDATION FAILED")
        for error in errors:
            print(error)
        return False
    
    print_success("All validations passed!\n")
    return True

def check_git_status():
    """Check if code is committed to GitHub"""
    print_step(1, "Checking Git Status")
    
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd="."
        )
        
        if result.stdout.strip():
            print_warning("You have uncommitted changes:")
            print(result.stdout)
            response = input("\nContinue with deployment anyway? (y/n): ").strip().lower()
            if response != 'y':
                print_error("Deployment cancelled")
                return False
        else:
            print_success("All changes committed to Git")
        
        return True
    except Exception as e:
        print_error(f"Could not check git status: {e}")
        return False

def deploy_with_render_api():
    """Deploy using Render API"""
    print_step(2, "Deploying to Render via API")
    
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {RENDER_API_TOKEN}",
            "Content-Type": "application/json",
        }
        
        # First, check if service exists
        print("  → Checking if service already exists...")
        
        response = requests.get(
            f"https://api.render.com/v1/services/{SERVICE_NAME}",
            headers=headers,
        )
        
        if response.status_code == 200:
            service_id = response.json()["id"]
            print_success(f"Found existing service: {service_id}")
            print("  → Updating service configuration...")
            
            # Update existing service
            update_payload = {
                "buildCommand": DEPLOYMENT_CONFIG["buildCommand"],
                "startCommand": DEPLOYMENT_CONFIG["startCommand"],
                "envVars": DEPLOYMENT_CONFIG["envVars"],
            }
            
            response = requests.patch(
                f"https://api.render.com/v1/services/{service_id}",
                json=update_payload,
                headers=headers,
            )
            
            if response.status_code in [200, 201]:
                print_success("Service configuration updated")
                return True
            else:
                print_error(f"Failed to update service: {response.text}")
                return False
        
        elif response.status_code == 404:
            print("  → Service not found, creating new one...")
            
            create_payload = {
                "name": DEPLOYMENT_CONFIG["name"],
                "type": DEPLOYMENT_CONFIG["type"],
                "repo": DEPLOYMENT_CONFIG["repo"],
                "branch": DEPLOYMENT_CONFIG["branch"],
                "runtime": DEPLOYMENT_CONFIG["runtime"],
                "buildCommand": DEPLOYMENT_CONFIG["buildCommand"],
                "startCommand": DEPLOYMENT_CONFIG["startCommand"],
                "envVars": DEPLOYMENT_CONFIG["envVars"],
                "region": DEPLOYMENT_CONFIG["region"],
                "plan": DEPLOYMENT_CONFIG["plan"],
            }
            
            response = requests.post(
                "https://api.render.com/v1/services",
                json=create_payload,
                headers=headers,
            )
            
            if response.status_code in [200, 201]:
                service_data = response.json()
                print_success(f"Service created: {service_data.get('id')}")
                return True
            else:
                print_error(f"Failed to create service: {response.text}")
                return False
        else:
            print_error(f"API error: {response.status_code} - {response.text}")
            return False
    
    except ImportError:
        print_warning("requests library not installed")
        print("  → Falling back to manual deployment instructions")
        return None
    except Exception as e:
        print_error(f"Deployment error: {e}")
        return False

def manual_deployment_instructions():
    """Print manual deployment instructions"""
    print_header("MANUAL DEPLOYMENT INSTRUCTIONS")
    
    print("Since API deployment requires 'requests' library, here's the manual process:\n")
    
    print("1. Go to: https://dashboard.render.com")
    print("2. Click 'New +' → Select 'Web Service'")
    print("3. Connect your GitHub account and select 'resume-checker-' repo")
    print("4. Enter these settings exactly:\n")
    
    print("   NAME: optiresume-ai-backend")
    print("   BRANCH: main")
    print("   RUNTIME: Python 3.11")
    print("   BUILD COMMAND:")
    print("   pip install -r backend/requirements-deploy.txt")
    print("   START COMMAND:")
    print("   cd backend && gunicorn -w 2 -b 0.0.0.0:8000 --timeout 120 --access-logfile - app.main:app")
    print("   REGION: Ohio")
    print("   PLAN: Free\n")
    
    print("5. Scroll to 'Environment' and add these variables:")
    print("   GROQ_API_KEY = " + GROQ_API_KEY[:10] + "...")
    print("   ENABLE_SBERT_MODEL = false")
    print("   ALLOWED_ORIGINS = http://localhost:5173,http://localhost:3000")
    print("   PYTHONUNBUFFERED = 1\n")
    
    print("6. Click 'Create Web Service' button")
    print("7. Wait 5-10 minutes for build and deployment")

def show_deployment_summary():
    """Show deployment summary"""
    print_header("DEPLOYMENT SUMMARY")
    
    print("Service Configuration:")
    print(f"  Name: {DEPLOYMENT_CONFIG['name']}")
    print(f"  Runtime: Python 3.11")
    print(f"  Plan: Free (512 MB RAM)")
    print(f"  Region: Ohio")
    print(f"  Repository: {GITHUB_REPO}")
    print(f"  Branch: {BRANCH}\n")
    
    print("Build Settings:")
    print(f"  Build Command: {DEPLOYMENT_CONFIG['buildCommand']}")
    print(f"  Start Command: {DEPLOYMENT_CONFIG['startCommand']}\n")
    
    print("Environment Variables:")
    for var in DEPLOYMENT_CONFIG['envVars']:
        if var['key'] == 'GROQ_API_KEY':
            print(f"  {var['key']}: {var['value'][:10]}... (redacted)")
        else:
            print(f"  {var['key']}: {var['value']}")
    
    print("\n" + "=" * 70)
    print("After deployment, your backend will be available at:")
    print("  https://optiresume-ai-backend.onrender.com")
    print("  API Docs: https://optiresume-ai-backend.onrender.com/docs")
    print("=" * 70 + "\n")

# ============================================================================
# MAIN DEPLOYMENT FLOW
# ============================================================================

def main():
    """Main deployment function"""
    print_header("🚀 OPTIRESUME AI - RENDER DEPLOYMENT SCRIPT")
    
    # Validate configuration
    if not validate_config():
        print_error("Configuration validation failed")
        sys.exit(1)
    
    # Show summary
    show_deployment_summary()
    
    # Check git status
    if not check_git_status():
        sys.exit(1)
    
    # Try API deployment
    print_header("DEPLOYING TO RENDER")
    result = deploy_with_render_api()
    
    if result is None:
        # API not available, show manual instructions
        manual_deployment_instructions()
    elif result:
        print_success("Deployment completed successfully!")
        print("\n📊 Next Steps:")
        print("  1. Monitor deployment at: https://dashboard.render.com")
        print("  2. Wait for 'Live' status (5-10 minutes)")
        print("  3. Test API at: https://optiresume-ai-backend.onrender.com/docs")
    else:
        print_error("Deployment failed. Please try manual deployment instructions above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
