#!/bin/bash
# Test script to verify deployment readiness
# Run this locally before deploying to Render/Vercel

echo "=========================================="
echo "OptiResume Deployment Readiness Check"
echo "=========================================="
echo ""

# Check 1: Verify lightweight requirements exist
echo "✓ Checking requirements-deploy.txt..."
if [ -f "backend/requirements-deploy.txt" ]; then
    echo "  ✅ Found: backend/requirements-deploy.txt"
    echo "  Dependencies:"
    grep -v "^#" backend/requirements-deploy.txt | grep -v "^$" | sed 's/^/    - /'
else
    echo "  ❌ Missing: backend/requirements-deploy.txt"
fi
echo ""

# Check 2: Verify ENABLE_SBERT_MODEL setting
echo "✓ Checking ENABLE_SBERT_MODEL configuration..."
if grep -q "ENABLE_SBERT_MODEL" backend/app/core/config.py; then
    echo "  ✅ Found ENABLE_SBERT_MODEL in config"
else
    echo "  ❌ Missing ENABLE_SBERT_MODEL in config"
fi
echo ""

# Check 3: Verify production env template
echo "✓ Checking .env.production..."
if [ -f ".env.production" ]; then
    echo "  ✅ Found: .env.production"
    if grep -q "ENABLE_SBERT_MODEL=false" .env.production; then
        echo "  ✅ ENABLE_SBERT_MODEL=false is set"
    fi
else
    echo "  ⚠️  Missing: .env.production (create from template)"
fi
echo ""

# Check 4: Verify deployment configs exist
echo "✓ Checking deployment configurations..."
for file in "Dockerfile.render" "render.yaml" "frontend/vercel.json"; do
    if [ -f "$file" ]; then
        echo "  ✅ Found: $file"
    else
        echo "  ⚠️  Missing: $file"
    fi
done
echo ""

# Check 5: Verify documentation
echo "✓ Checking documentation..."
for file in "DEPLOYMENT_GUIDE.md" "512MB_OPTIMIZATION_SUMMARY.md"; do
    if [ -f "$file" ]; then
        echo "  ✅ Found: $file"
    else
        echo "  ⚠️  Missing: $file"
    fi
done
echo ""

# Check 6: Python dependencies test (optional)
echo "✓ Optional: Test Python dependencies"
echo "  Run: pip install -r backend/requirements-deploy.txt"
echo "  Then: cd backend && python run.py"
echo ""

echo "=========================================="
echo "✅ Ready for deployment to Render + Vercel!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. git add . && git commit -m 'Ready for deployment'"
echo "2. git push origin main"
echo "3. Deploy on Render (backend) and Vercel (frontend)"
echo "4. Set environment variables in Render dashboard"
echo ""
