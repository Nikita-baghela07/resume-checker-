# 🚀 Render Backend Production Setup

## Issue: Network Errors on Vercel Frontend Connecting to Render Backend

If your Vercel frontend shows **network errors** when accessing the production backend on Render, follow these steps.

---

## ✅ Step 1: Verify Render Backend is Running

1. Go to: https://dashboard.render.com
2. Find your backend service (should be named something like `optiresume-ai-backend`)
3. Check the **Status** is **Live** (green)
4. Note the **Backend URL** (should be `https://optiresume-ai-backend-payw.onrender.com` or similar)

**If it's not running:**
- Click **Deploy** to start the service
- Wait 2-3 minutes for it to become live
- Test the health endpoint: `https://optiresume-ai-backend-payw.onrender.com/health`

---

## ✅ Step 2: Set Environment Variables on Render

### Open Render Dashboard
1. Go to https://dashboard.render.com
2. Click on your backend service
3. Go to **Settings** → **Environment**

### Required Environment Variables

Copy and paste these exact settings:

```
GROQ_API_KEY=your_actual_groq_api_key_from_console_groq_com
MODEL_NAME=llama-3.1-8b-instant
ENABLE_SBERT_MODEL=false
MAX_TOKENS=2000
ALLOWED_ORIGINS=https://resume-checker-h4mi.vercel.app,http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:5176,http://localhost:5177,http://localhost:5178,http://localhost:5179,http://localhost:5180,http://localhost:3000
PYTHONUNBUFFERED=1
```

⚠️ **Get your GROQ_API_KEY from:** https://console.groq.com/keys (it starts with `gsk_`)

**Important Notes:**
- ✅ **Keep ENABLE_SBERT_MODEL=false** (saves 200+ MB RAM)
- ✅ **ALLOWED_ORIGINS** includes both production (Vercel) and local dev URLs
- ✅ Render auto-injects `DATABASE_URL` (PostgreSQL) - don't add it manually
- ✅ Render auto-injects `JWT_SECRET` if you generated one - don't add it manually

### After Adding Variables

1. Click **Save Changes**
2. The service will **automatically redeploy** (wait 2-3 minutes)
3. Check the deployment logs to confirm it started successfully

---

## ✅ Step 3: Verify Backend Connection

### Test from Local Machine

```bash
# Terminal 1: Start local backend
cd c:\Users\VINITA\Desktop\optiresume\resume-checker-\backend
python run.py

# Terminal 2: Test local connection
curl http://localhost:8000/health

# Terminal 3: Test production backend
curl https://optiresume-ai-backend-payw.onrender.com/health
```

Both should return:
```json
{"status": "ok", "model_loaded": false, "version": "1.0.0", "mode": "tfidf"}
```

### Test CORS from Frontend

Open your browser console (F12) and run:

```javascript
// Test local backend (should work)
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)

// Test production backend (check for CORS errors)
fetch('https://optiresume-ai-backend-payw.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

If you see CORS errors, the `ALLOWED_ORIGINS` are not set correctly on Render.

---

## ✅ Step 4: Verify Vercel Frontend Configuration

### Check Frontend Environment Variables

1. Go to https://vercel.com/dashboard
2. Click on `resume-checker` project
3. Go to **Settings** → **Environment Variables**

Should have (auto-deployed from git):
```
VITE_API_URL = https://optiresume-ai-backend-payw.onrender.com
```

If missing, add it and redeploy:
1. Click **Redeploy** on the **Deployments** tab
2. Wait for it to build and deploy (2-3 minutes)

---

## ✅ Step 5: Test End-to-End

### Local Test (Should Work Immediately)
1. Start backend: `python run.py` (port 8000)
2. Start frontend: `npm run dev` (port 5174)
3. Go to http://localhost:5174
4. Try: Upload resume → Get score → Optimize → Download PDF

### Production Test (After Render/Vercel Setup)
1. Go to https://resume-checker-h4mi.vercel.app
2. Sign up with a test email
3. Upload resume or paste text
4. Try: Paste job description → Click Optimize
5. Check browser console (F12) for any errors

**Expected Success:** ✅ "Optimization complete! Score improved by X%"

---

## 🔧 Common Issues & Fixes

### Issue 1: "Network Error" on Vercel Frontend

**Cause:** CORS headers not being sent by Render backend

**Fix:**
1. Verify `ALLOWED_ORIGINS` on Render includes `https://resume-checker-h4mi.vercel.app`
2. Check Render deployment logs for errors
3. Redeploy the Render backend

### Issue 2: Render Service Spins Down After Inactivity

**Cause:** Free Render tier spins down services after 15 minutes of inactivity

**Fix:** 
- Upgrade to paid tier ($7/month) for always-on service
- Or: Add a monitoring service (uptime robot) to ping the backend every 10 minutes

### Issue 3: Database Errors on Render

**Cause:** PostgreSQL addon not provisioned

**Fix:**
1. Go to Render dashboard
2. Click on your backend service
3. Go to **Data** → Add PostgreSQL
4. Render will auto-inject `DATABASE_URL`
5. Redeploy the service

### Issue 4: Groq API Key Invalid

**Cause:** API key not set or incorrect in Render

**Fix:**
1. Verify the key on https://console.groq.com/keys
2. Copy the exact key
3. Update in Render environment variables
4. Redeploy

---

## 📋 Deployment Checklist

- [ ] Render backend is **Live** (green status)
- [ ] All environment variables set on Render (GROQ_API_KEY, MODEL_NAME, ALLOWED_ORIGINS, etc.)
- [ ] Vercel frontend has `VITE_API_URL` environment variable
- [ ] `https://optiresume-ai-backend-payw.onrender.com/health` returns OK
- [ ] Local backend on `http://localhost:8000` works fine
- [ ] Local frontend on `http://localhost:5174` works fine
- [ ] Production frontend on `https://resume-checker-h4mi.vercel.app` can reach backend

---

## 🚀 Quick Redeploy Commands

### Redeploy Backend on Render (via Git Push)
```bash
git add .
git commit -m "Update production configuration"
git push origin main
# Render auto-deploys on push
```

### Verify Render Deployment Status
```bash
# Check backend is running
curl https://optiresume-ai-backend-payw.onrender.com/health

# Check frontend
curl https://resume-checker-h4mi.vercel.app
```

---

## 📞 Need Help?

If issues persist:

1. **Check Render logs**: https://dashboard.render.com → Your service → Logs
2. **Check Vercel logs**: https://vercel.com/dashboard → Your project → Deployments → Click latest
3. **Test locally first**: Make sure local setup works before debugging production
4. **Check network tab**: Browser F12 → Network → Look for failed requests

---

**Last Updated:** April 2026
**Status:** Production Ready ✅
