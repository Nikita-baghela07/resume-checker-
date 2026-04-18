# ✅ Deployment Checklist (512 MB Limit)

## Pre-Deployment (Local)

- [ ] Review `512MB_OPTIMIZATION_SUMMARY.md`
- [ ] Read `DEPLOYMENT_GUIDE.md` completely
- [ ] Test locally:
  ```bash
  pip install -r backend/requirements-deploy.txt
  cd backend
  export ENABLE_SBERT_MODEL=false
  python run.py
  ```
- [ ] Verify output shows: `✅ SBERT model DISABLED [LIGHTWEIGHT MODE - 200MB saved]`
- [ ] Test upload resume at http://localhost:8000/docs
- [ ] Create `.env.production` from template with your Groq API key
- [ ] Ensure `.gitignore` includes `.env` (don't commit secrets!)

---

## GitHub Preparation

- [ ] Commit all optimization changes:
  ```bash
  git add .
  git commit -m "Optimized for 512MB deployment: SBERT disabled, lightweight deps"
  git push origin main
  ```
- [ ] Verify all changes pushed:
  ```bash
  git log --oneline -5
  git status  # Should be clean
  ```

---

## Render Backend Deployment

### Option A: Docker (Recommended)

- [ ] Go to [render.com](https://render.com)
- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub account and select repository
- [ ] Configure:
  - [ ] Service name: `optiresume-ai`
  - [ ] Select branch: `main`
  - [ ] Environment: `Docker`
  - [ ] Region: `Oregon` (cheapest)
  - [ ] Plan: `Starter` (512 MB RAM, $7/month)
- [ ] Add environment variables:
  - [ ] `GROQ_API_KEY` = your API key
  - [ ] `ENABLE_SBERT_MODEL` = `false`
  - [ ] `DATABASE_URL` = PostgreSQL URL (or leave for SQLite)
  - [ ] `ALLOWED_ORIGINS` = `https://yourdomain.vercel.app`
  - [ ] `JWT_SECRET` = random 32-char string
- [ ] Click "Deploy"
- [ ] Wait 5-10 minutes for build
- [ ] Verify deployment: Check logs for "LIGHTWEIGHT MODE"

### Option B: Gunicorn (Simpler Setup)

- [ ] Go to [render.com](https://render.com)
- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub → select repo
- [ ] Configure:
  - [ ] Service name: `optiresume-ai`
  - [ ] Environment: `Python 3.11`
  - [ ] Build command:
    ```
    pip install -r resume-checker-/backend/requirements-deploy.txt
    ```
  - [ ] Start command:
    ```
    cd resume-checker-/backend && gunicorn -w 2 -b 0.0.0.0:8000 --timeout 120 run:app
    ```
  - [ ] Plan: `Starter` (512 MB, $7/month)
- [ ] Add environment variables (same as Option A above)
- [ ] Click "Deploy"
- [ ] Monitor logs

---

## Vercel Frontend Deployment

- [ ] Go to [vercel.com](https://vercel.com)
- [ ] Click "Add New" → "Project"
- [ ] Import from GitHub → select repository
- [ ] Configure:
  - [ ] Framework: Auto-detected (Vite)
  - [ ] Root directory: `resume-checker-/frontend`
  - [ ] Build command: `npm run build` (auto)
  - [ ] Output directory: `dist` (auto)
- [ ] Add environment variables:
  - [ ] `VITE_API_URL` = `https://optiresume-ai.onrender.com` (your Render URL)
- [ ] Click "Deploy"
- [ ] Wait 2-3 minutes
- [ ] Verify at vercel.app URL

---

## Database Setup (Optional)

If using PostgreSQL instead of SQLite:

- [ ] On Render dashboard: "New +" → "PostgreSQL"
- [ ] Configure:
  - [ ] Name: `optiresume-db`
  - [ ] Region: `Oregon`
  - [ ] Plan: Free tier
- [ ] Copy connection string
- [ ] Add to backend as `DATABASE_URL`

---

## Post-Deployment Testing

### Test Backend API

```bash
# Replace with your Render URL
curl https://optiresume-ai.onrender.com/docs
curl https://optiresume-ai.onrender.com/health
```

- [ ] API responds successfully
- [ ] Check logs: "LIGHTWEIGHT MODE" message appears
- [ ] Memory usage: ~300-400 MB (not exceeding limit)

### Test Frontend

- [ ] Go to your Vercel URL
- [ ] Upload a resume
- [ ] Score should calculate
- [ ] Diff viewer should display changes
- [ ] Optimization should work
- [ ] Check browser console for errors

### End-to-End Test

- [ ] Upload resume
- [ ] Wait for scoring
- [ ] Click optimize
- [ ] View results
- [ ] Download PDF

---

## Monitoring & Troubleshooting

### If Backend Crashes

- [ ] Check Render logs: "Out of memory"?
  - Solution: Ensure `ENABLE_SBERT_MODEL=false`
  - Or upgrade plan to Standard (1GB)
- [ ] Check Render logs: "Database connection error"?
  - Solution: Verify `DATABASE_URL` is correct
- [ ] Check Render logs: "GROQ_API_KEY not found"?
  - Solution: Add to Render environment variables

### If Frontend Shows Errors

- [ ] Check browser console
- [ ] Verify `VITE_API_URL` matches Render backend
- [ ] Check network tab for API calls
- [ ] Verify CORS origins in backend config

### Memory Monitoring

- [ ] Render dashboard → Web Service → Logs
- [ ] Look for memory usage
- [ ] Should be 300-400 MB, not exceeding 512 MB
- [ ] If exceeding: Something loaded SBERT (check config)

---

## Cost Verification

After deployment:

- [ ] Render: ~$7/month (Starter plan)
- [ ] Vercel: Free (Pro is optional)
- [ ] Groq API: ~$2-5/month (pay-as-you-go)
- [ ] **Total: ~$9-12/month** ✅

---

## Success Criteria ✅

- [ ] Frontend deployed on Vercel
- [ ] Backend deployed on Render
- [ ] Both services are "Up" (green status)
- [ ] Resume upload works
- [ ] Scoring displays correctly
- [ ] Optimization generates suggestions
- [ ] Logs show "LIGHTWEIGHT MODE"
- [ ] Memory stays below 512 MB
- [ ] No 500 errors in logs

---

## If Anything Fails

1. Check `DEPLOYMENT_GUIDE.md` troubleshooting section
2. Review Render/Vercel logs carefully
3. Verify all environment variables are set
4. Test locally: `pip install -r backend/requirements-deploy.txt && python run.py`
5. Ensure GROQ_API_KEY is valid

---

## Rollback Plan

If deployment has issues:

```bash
# Revert to previous commit
git revert HEAD
git push origin main

# Both services auto-redeploy from main branch
```

---

**Status:** Ready for production deployment! 🚀
