# 🎯 RENDER DEPLOYMENT - VISUAL STEP-BY-STEP GUIDE

## ✅ BACKEND TESTED & CODE PUSHED TO GITHUB

Your backend is running successfully with:
```
✅ ENABLE_SBERT_MODEL=false
✅ GROQ_API_KEY loaded
✅ Database initialized
✅ Lightweight Mode: 200MB saved
```

All optimization code is now on GitHub and ready to deploy!

---

## 🚀 DEPLOY ON RENDER (Takes 10 minutes)

### Step 1: Go to Render
```
URL: https://render.com
Action: Sign in with GitHub
```

### Step 2: Create Web Service
```
Click: "New +" button (top right)
       ↓
Select: "Web Service"
       ↓
Action: Connect your GitHub account
        → Authorize Render
        → Select "resume-checker-" repository
        → Click "Connect"
```

### Step 3: Configure Web Service

**Copy these settings exactly:**

**NAME:** `optiresume-ai-backend`

**BRANCH:** `main`

**RUNTIME:** `Python 3.11`

**BUILD COMMAND:**
```
pip install -r backend/requirements-deploy.txt
```

**START COMMAND:**
```
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

**REGION:** `Ohio` (or closest to you)

**PLAN:** `Free` (512 MB RAM, $0/month - may spin down after 15 min inactivity)

### Step 4: Add Environment Variables

Scroll down to **"Environment"** section and click **"Add Environment Variable"** for each:

**1. GROQ_API_KEY**
- Key: `GROQ_API_KEY`
- Value: `gsk_your_actual_key_from_groq`
- Click "Add"

**2. ENABLE_SBERT_MODEL** ⚠️ **CRITICAL!**
- Key: `ENABLE_SBERT_MODEL`
- Value: `false` (lowercase)
- Click "Add"

**3. ALLOWED_ORIGINS**
- Key: `ALLOWED_ORIGINS`
- Value: `http://localhost:5173`
- Click "Add"

**4. PYTHONUNBUFFERED**
- Key: `PYTHONUNBUFFERED`
- Value: `1`
- Click "Add"

### Step 5: Deploy!

```
BUTTON: "Create Web Service" (bottom right, blue)
ACTION: Click it!
WAIT:   5-10 minutes for build
```

---

## 📊 MONITOR DEPLOYMENT

### Watch Build Logs

```
Dashboard → Your Service → "Logs" Tab
                ↓
        Watch these messages appear:
                ↓
        ✅ Building Docker image...
        ✅ pip install complete
        ✅ Starting Gunicorn server
        ✅ INFO: Uvicorn running
        ✅ ✅ SBERT model DISABLED
        ✅ Application startup complete
```

**If you see all these → SUCCESS! ✅**

---

## ✅ VERIFY YOUR DEPLOYMENT

### Check Status
```
Dashboard → Your Service
Should show: "Live" (green)
Your URL: https://optiresume-ai-backend.onrender.com
```

### Test API
```bash
# Open browser or use curl:
https://optiresume-ai-backend.onrender.com/docs

# You should see the Swagger API documentation
# Try the POST /score endpoint
```

### Check Memory
```
Dashboard → Logs Tab
Look for: "Memory: XXX MB"
Expected: ~350 MB (well under 512 MB limit)
```

---

## 🆘 TROUBLESHOOTING

### ❌ Build Failed
**Look in logs for:**
- "Build log retrieved"
- Check "Resume-checker" directory name
- Check file path is correct

**Solution:**
```
1. Check requirements-deploy.txt exists in GitHub
2. Verify build command path: 
   backend/requirements-deploy.txt (NOT resume-checker-/backend/...)
3. Click "Manual Deploy" to retry
```

### ❌ Start Failed
**Look in logs for:**
- "Application failed to start"
- "GROQ_API_KEY not found"

**Solution:**
```
1. Go to Environment variables
2. Verify GROQ_API_KEY is set correctly
3. Verify ENABLE_SBERT_MODEL=false
4. Click "Manual Deploy" button
```

### ❌ "Out of Memory"
**If you see memory errors:**

**Solution:**
```
1. Verify ENABLE_SBERT_MODEL=false is set
2. Check the logs say "LIGHTWEIGHT MODE"
3. If still failing, upgrade to Standard plan
```

---

## 🎯 YOUR DEPLOYED BACKEND URL

Once build completes, your backend will be available at:

```
┌──────────────────────────────────────────────┐
│ https://optiresume-ai-backend.onrender.com   │
└──────────────────────────────────────────────┘

Use this URL for:
✓ API calls from frontend
✓ Environment variable: VITE_API_URL
```

---

## 📋 WHAT'S HAPPENING

```
Your Local Code
     ↓ (git push)
GitHub Repository
     ↓ (webhook)
Render Detects Change
     ↓
Renders Reads:
  - requirements-deploy.txt
  - Build command
  - Start command
     ↓
Render Builds:
  1. Downloads Python 3.11
  2. Installs pip packages (~130MB)
  3. Copies your code
  4. Starts Gunicorn server
     ↓
Your Backend Goes Live! 🎉
```

---

## ⏱️ TIMELINE

```
Step 1 (Configure):    2 minutes
Step 2 (Deploy click): 1 minute
Step 3 (Build wait):   5-10 minutes
Step 4 (Verification): 2 minutes
────────────────────────────────
TOTAL:                 10-15 minutes
```

---

## 🎉 SUCCESS CHECKLIST

After deployment:

- [ ] Dashboard shows "Live" (green status)
- [ ] Logs show "✅ SBERT model DISABLED [LIGHTWEIGHT MODE - 200MB saved]"
- [ ] Logs show "Application startup complete"
- [ ] Memory usage ~350 MB (not exceeding 512 MB)
- [ ] API endpoint responds: `/docs` works
- [ ] Environment variables all set

---

## 📞 NEXT STEPS

After backend is deployed:

1. **Test Backend API:**
   ```
   Visit: https://optiresume-ai-backend.onrender.com/docs
   Try: POST /score endpoint with test data
   ```

2. **Deploy Frontend on Vercel:**
   ```
   Go to: https://vercel.com
   Import: Your GitHub repo
   Set VITE_API_URL = your Render backend URL
   Deploy!
   ```

3. **Test End-to-End:**
   ```
   Upload resume on Vercel URL
   Check scoring works
   Verify optimization runs
   ```

---

## 💰 COST CONFIRMATION

After deployment:
- Render: FREE (free tier, 512 MB)
- Vercel: FREE (deploy frontend)
- Groq API: $2-5/month (usage-based)
- **TOTAL: $2-5/month** ✨

**Note:** Free Render spins down after 15 minutes of inactivity. First request after spin-down takes ~30 seconds. For production, consider upgrading to Starter ($7/month).

---

## 📚 DOCUMENTATION

If you need more details:
- `RENDER_DEPLOYMENT.md` - Full detailed guide
- `DEPLOYMENT_CHECKLIST.md` - Complete checklist
- `512MB_OPTIMIZATION_SUMMARY.md` - Technical details
- `QUICK_REFERENCE.txt` - Quick commands

---

**YOU'RE READY TO DEPLOY! 🚀**

Go to https://render.com and follow the steps above.

If anything is unclear, re-read this document or check the documentation files.
