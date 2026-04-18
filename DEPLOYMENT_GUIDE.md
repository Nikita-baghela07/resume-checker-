# OptiResume AI - Deployment Guide (512 MB Limit)

## 📊 Size Optimization Summary

### Original Size (Unoptimized)
- PyTorch (CPU): ~500 MB ❌
- SBERT Model: ~200 MB ❌
- Sentence-transformers: ~100 MB ❌
- Other dependencies: ~150 MB
- **TOTAL: ~950 MB** ❌ (exceeds limits)

### Optimized Size (For Deployment)
- FastAPI + Uvicorn: ~80 MB ✅
- scikit-learn + numpy: ~100 MB ✅
- PDF processing: ~50 MB ✅
- Other dependencies: ~100 MB ✅
- **TOTAL: ~330 MB** ✅ (SBERT disabled)

### Savings: **620 MB removed** (65% reduction!)

---

## 🚀 Deployment Steps

### 1. Render Backend Deployment

#### Option A: Using Docker (Recommended)

```bash
# Push code to GitHub
git add .
git commit -m "Optimized for deployment"
git push origin main

# On Render dashboard:
1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Select branch: main
4. Configure:
   - Name: optiresume-ai
   - Environment: Docker
   - Region: Oregon (cheaper)
   - Plan: Starter ($7/month) or Standard ($12/month)

5. Add environment variables:
   - GROQ_API_KEY=<your_key>
   - ENABLE_SBERT_MODEL=false  # CRITICAL!
   - DATABASE_URL=<PostgreSQL_URL>
   - ALLOWED_ORIGINS=https://<vercel-domain>.vercel.app

6. Build command: (leave default)
7. Start command: Leave default (Docker)
8. Deploy!
```

#### Option B: Using Gunicorn (Simpler)

```bash
# On Render dashboard:
1. Click "New +" → "Web Service"
2. Connect GitHub repository
3. Select branch: main
4. Configure:
   - Name: optiresume-ai
   - Environment: Python 3.11
   - Build command: pip install -r backend/requirements-deploy.txt
   - Start command: cd resume-checker-/backend && gunicorn -w 2 -b 0.0.0.0:8000 --timeout 120 run:app
   - Plan: Starter (512 MB) or Standard (1 GB)

5. Add environment variables (same as above)
6. Deploy!
```

**Render Cost**: ~$7/month (Starter) or $12/month (Standard with 1GB RAM)

---

### 2. Vercel Frontend Deployment

```bash
# One-time setup:
cd frontend
npm install -g vercel
vercel login

# Deploy:
vercel deploy --prod

# Or through dashboard:
1. Go to vercel.com
2. Import project from GitHub
3. Build settings:
   - Framework: Vite
   - Build command: npm run build
   - Output directory: dist
4. Environment variables:
   - VITE_API_URL=https://optiresume-ai.onrender.com
5. Deploy!
```

**Vercel Cost**: Free tier (perfect for static frontend)

---

### 3. Database Setup (PostgreSQL on Render)

```bash
# On Render dashboard:
1. Click "New +" → "PostgreSQL"
2. Configure:
   - Name: optiresume-db
   - Region: Oregon
   - Plan: Free tier or $15/month (1GB)
3. Copy connection string
4. Add to backend environment variables:
   DATABASE_URL=<postgresql://...>
```

---

## 🔧 Critical Environment Variables

```env
# BACKEND (.env on Render)
GROQ_API_KEY=gsk_...
ENABLE_SBERT_MODEL=false      # THIS SAVES 200 MB!
DATABASE_URL=postgresql://...
ALLOWED_ORIGINS=https://<frontend>.vercel.app
```

---

## 📈 Performance Characteristics

### With SBERT Disabled (Lightweight Mode)
- ✅ Memory usage: ~300-350 MB
- ✅ Cold start: 5-10 seconds
- ✅ Inference speed: Still fast (TF-IDF + Groq API)
- ✅ Cost: ~$7-20/month total

### With SBERT Enabled (Full Hybrid)
- ⚠️ Memory usage: ~800 MB-1 GB
- ⚠️ Requires 2GB+ plan on Render (~$25/month)
- ✅ Better semantic matching accuracy
- ✅ Faster local inference (no API call latency)

**Recommendation**: Start with SBERT disabled, upgrade if needed.

---

## 🧪 Testing Before Deployment

```bash
# Test production build locally
cd backend
pip install -r requirements-deploy.txt
export ENABLE_SBERT_MODEL=false
python run.py

# Test endpoints
curl http://localhost:8000/docs
curl http://localhost:8000/health
```

---

## 🔍 Monitoring & Troubleshooting

### Check Memory Usage (Render)
```bash
# SSH into container
# View memory: top or free -h
```

### View Logs
```bash
# Render dashboard → your service → logs
# Look for "LIGHTWEIGHT MODE" confirmation at startup
```

### Size Verification
```bash
# Check if SBERT was loaded
grep "SBERT" render.log
# Should see: "✅ SBERT model DISABLED [LIGHTWEIGHT MODE - 200MB saved]"
```

---

## 💰 Total Monthly Cost Estimate

| Component | Cost | Notes |
|-----------|------|-------|
| **Frontend (Vercel)** | Free | Static hosting |
| **Backend (Render)** | $7-12 | Starter/Standard |
| **Database (Render)** | Free-15 | Free or PostgreSQL |
| **API Calls (Groq)** | ~$2-5 | Pay-as-you-go |
| **TOTAL** | **$9-32** | Very affordable! |

---

## ✅ Deployment Checklist

- [ ] Update `.env.production` with correct keys
- [ ] Set `ENABLE_SBERT_MODEL=false` in Render
- [ ] Test locally with `requirements-deploy.txt`
- [ ] Ensure Groq API key is active
- [ ] Configure PostgreSQL connection string
- [ ] Set CORS origins for Vercel domain
- [ ] Deploy backend first, then frontend
- [ ] Test resume upload and scoring
- [ ] Verify diff viewer works
- [ ] Check error logs for any issues

---

## 🚨 Common Issues & Fixes

### Issue: 512 MB limit exceeded
**Fix**: Ensure `ENABLE_SBERT_MODEL=false` in environment

### Issue: "Service timeout"
**Fix**: Increase timeout in gunicorn command (already set to 120s)

### Issue: CORS errors
**Fix**: Update `ALLOWED_ORIGINS` to match Vercel domain

### Issue: Database connection fails
**Fix**: Verify `DATABASE_URL` is correct in Render environment

---

## 📚 References

- [Render Deployment Docs](https://render.com/docs)
- [Vercel Deployment Docs](https://vercel.com/docs)
- [FastAPI Production Guide](https://fastapi.tiangolo.com/deployment/)
