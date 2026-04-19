import logging
import sys
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Allow ai_engine imports from project root
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.routes import upload, optimize, download, auth
from app.core.config import settings
from app.db.session import engine, Base
import app.models.user # Ensure models are loaded for create_all

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(name)s — %(message)s"
)
logger = logging.getLogger(__name__)

# Debug: Check if Groq API key is loaded
if not settings.GROQ_API_KEY:
    logger.warning("⚠️  GROQ_API_KEY not found in environment!")
    logger.warning("⚠️  Set GROQ_API_KEY in .env file for resume rewriting to work")
else:
    logger.info("✅ GROQ_API_KEY loaded from environment")


# ─── Startup / Shutdown ───────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Hybrid semantic mode (SBERT + TF-IDF) with graceful fallback."""
    mode = "TF-IDF Only" if not settings.ENABLE_SBERT_MODEL else "SBERT + TF-IDF"
    logger.info(f"Initializing Resume Optimizer [{mode}]...")
    
    try:
        # Create database tables
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"⚠️ Database initialization failed: {e}")

    app.state.sbert_model = None
    
    # Only load SBERT if explicitly enabled (saves 200+ MB RAM)
    if settings.ENABLE_SBERT_MODEL:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SBERT model: {settings.SBERT_MODEL}...")
            app.state.sbert_model = SentenceTransformer(settings.SBERT_MODEL)
            logger.info("✅ SBERT model loaded successfully [HYBRID MODE]")
        except Exception as e:
            logger.warning(f"⚠️ Failed to load SBERT: {e}. Falling back to Pure TF-IDF.")
            app.state.sbert_model = None
    else:
        logger.info("✅ SBERT model DISABLED [LIGHTWEIGHT MODE - 200MB saved]")

    yield  # App runs here

    logger.info("Shutting down OptiResume AI...")


# ─── App ──────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="OptiResume AI",
    description="Real-time ATS Simulator & Resume Optimizer",
    version="1.0.0",
    lifespan=lifespan
)

# CORS — allow React frontend
logger.info(f"Configuring CORS with allowed origins: {settings.ALLOWED_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("✅ CORS middleware configured")


# No additional custom middleware needed - FastAPI's CORSMiddleware handles it all


# ─── Global Error Handler ─────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "An unexpected error occurred. Please try again."}
    )


# ─── Routes ───────────────────────────────────────────────────────────────────

app.include_router(upload.router,   prefix="/api/v1", tags=["Upload"])
app.include_router(optimize.router, prefix="/api/v1", tags=["Optimize"])
app.include_router(download.router, prefix="/api/v1", tags=["Download"])
app.include_router(auth.router,     prefix="/api/v1", tags=["Auth"])


# ─── Health Check ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
def root():
    """Root endpoint - returns API information."""
    return {
        "status": "running",
        "service": "OptiResume AI",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "optimize": "POST /api/v1/optimize",
            "upload": "POST /api/v1/upload",
            "download": "POST /api/v1/download"
        }
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "model_loaded": hasattr(app.state, "sbert_model") and app.state.sbert_model is not None,
        "version": "1.0.0",
        "mode": "hybrid" if hasattr(app.state, "sbert_model") and app.state.sbert_model is not None else "tfidf"
    }

@app.get("/api/v1/health", tags=["Health"])
def api_health_check():
    """API health check endpoint (v1 path)."""
    return {
        "status": "ok",
        "service": "OptiResume AI Backend",
        "version": "1.0.0",
        "model_loaded": hasattr(app.state, "sbert_model") and app.state.sbert_model is not None
    }