# 🚀 RENDER DEPLOYMENT - STEP BY STEP GUIDE

## BEFORE YOU START
- [ ] You have a GitHub account
- [ ] Code is pushed to GitHub (all optimizations committed)
- [ ] You have GROQ_API_KEY ready
- [ ] You're logged into Render.com

---

## STEP 1: Prepare GitHub (5 minutes)

```bash
# In your local optiresume folder, run:
cd c:\Users\VINITA\Desktop\optiresume

git add .
git commit -m "Optimized: SBERT disabled, 330MB lightweight deployment"
git push origin main

# Verify it's pushed:
git log --oneline -5
git status  # Should say "nothing to commit"
```

**✅ Your code is now on GitHub and ready to deploy**

---

## STEP 2: Deploy on Render (10 minutes)

### Option A: Using Gunicorn (EASIEST - Recommended for first deployment)

1. Go to **https://render.com**
2. Sign in with GitHub account
3. Click **"New +"** → **"Web Service"**
4. Click **"Connect GitHub account"**
   - Authorize Render to access your repos
   - Select your `optiresume` repository
5. Click **"Connect"**

---

### STEP 3: Configure Web Service

Fill in these settings:

| Field | Value |
|-------|-------|
| Name | `optiresume-ai-backend` |
| Branch | `main` |
| Root Directory | *(leave empty)* |
| Runtime | `Python 3.11` |
| Build Command | `pip install -r resume-checker-/backend/requirements-deploy.txt` |
| Start Command | `cd resume-checker-/backend && gunicorn -w 2 -b 0.0.0.0:8000 --timeout 120 --access-logfile - run:app` |
| Region | `Ohio` (or your closest region) |
| Plan | **`Starter`** ($7/month, 512 MB RAM) |

---

### STEP 4: Add Environment Variables

Scroll down to **"Environment"** section and click **"Add Environment Variable"**

Add these variables one by one:

1. **GROQ_API_KEY**
   - Key: `GROQ_API_KEY`
   - Value: `gsk_your_actual_api_key_here` (get from https://console.groq.com)
   - Click "Add"

2. **ENABLE_SBERT_MODEL** (CRITICAL!)
   - Key: `ENABLE_SBERT_MODEL`
   - Value: `false`
   - Click "Add"

3. **ALLOWED_ORIGINS**
   - Key: `ALLOWED_ORIGINS`
   - Value: `http://localhost:5173,https://yourdomain.vercel.app`
   - Click "Add"

4. **PYTHONUNBUFFERED**
   - Key: `PYTHONUNBUFFERED`
   - Value: `1`
   - Click "Add"

---

### STEP 5: Deploy!

1. Scroll to bottom
2. Click **"Create Web Service"** (blue button)
3. **Wait 5-10 minutes** for deployment
4. Watch the build logs in real-time

---

## STEP 6: Verify Deployment Success

### Check Build Logs
- Go to your service dashboard
- Click **"Logs"** tab
- Look for these messages:
  ```
  ✅ SBERT model DISABLED [LIGHTWEIGHT MODE - 200MB saved]
  INFO:     Application startup complete.
  ```

### Test API Endpoint
```bash
# Replace with your actual Render URL
curl https://optiresume-ai-backend.onrender.com/docs

# You should see the Swagger API documentation
```

### Check Memory Usage
- Logs tab → Look for Python process memory
- Should be **~350 MB** (well under 512 MB limit!)

---

## YOUR RENDER URL

Once deployed, your backend will be available at:
```
https://optiresume-ai-backend.onrender.com
```

(Render creates a unique subdomain - you can customize in settings)

---

## TROUBLESHOOTING

### Deploy Failed - "Build Failed"
❌ Check build logs:
1. Go to Logs tab
2. Look for error messages
3. Common issues:
   - Missing `requirements-deploy.txt` → Ensure file exists and is committed
   - Wrong path in build command → Use exact path from root
   - Network timeout → Try deploying again

**Solution**: Make sure `resume-checker-/backend/requirements-deploy.txt` exists and is pushed to GitHub

---

### Deploy Failed - "Start Failed"
❌ Check start logs:
1. Go to Logs tab
2. Likely issue: `GROQ_API_KEY` not set

**Solution**: 
- Go to Environment variables
- Verify `GROQ_API_KEY` is correct (starts with `gsk_`)
- Redeploy: Click "Manual Deploy" → "Latest"

---

### Running but API gives errors
❌ Check if SBERT is loading:
1. Logs should show: `✅ SBERT model DISABLED`
2. If not, ENABLE_SBERT_MODEL might be `true`

**Solution**:
- Set `ENABLE_SBERT_MODEL=false` in environment
- Redeploy

---

## NEXT: Deploy Frontend on Vercel

After backend is deployed and working:

1. Go to **https://vercel.com**
2. Click "Add New" → "Project"
3. Import `optiresume` from GitHub
4. Set Root Directory: `resume-checker-/frontend`
5. Set Environment Variable:
   - `VITE_API_URL=https://optiresume-ai-backend.onrender.com`
6. Deploy!

---

## 💰 COSTS

- **Render (Backend)**: $7/month (Starter plan)
- **Vercel (Frontend)**: FREE
- **Groq API**: ~$2-5/month (pay-as-you-go)
- **TOTAL**: ~$9-12/month ✨

---

## 🎉 SUCCESS!

You now have:
- ✅ Backend running on Render (512 MB limit with room to spare)
- ✅ Frontend on Vercel (free)
- ✅ Total cost: ~$10/month
- ✅ All features working: resume upload, scoring, optimization
- ✅ Lightweight mode: TF-IDF + Groq API

---

## QUICK CHECKLIST

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Environment variables set (GROQ_API_KEY, ENABLE_SBERT_MODEL=false)
- [ ] Build successful (watch logs for ~5 min)
- [ ] API responding (test /docs endpoint)
- [ ] Logs show "LIGHTWEIGHT MODE"
- [ ] Memory usage acceptable (~350 MB)
- [ ] Ready to deploy frontend on Vercel

---

Need help? Check these files:
- `DEPLOYMENT_CHECKLIST.md` - Full checklist
- `DEPLOYMENT_GUIDE.md` - Detailed guide
- `QUICK_REFERENCE.txt` - Quick reference
