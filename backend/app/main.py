import logging
import sys
import os
import re
from contextlib import asynccontextmanager

import numpy as np
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
    """Load BERT embedding model and LLM provider once at startup — not per request."""
    logger.info("Loading BERT embedding model...")
    try:
        # Create database tables
        logger.info("Initializing database...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables initialized")

        from ai_engine.embedding.bert_embedder import BertEmbedder
        app.state.sbert_model = BertEmbedder(settings.EMBEDDING_MODEL)
        logger.info(
            f"✅ BERT model '{settings.EMBEDDING_MODEL}' loaded successfully "
            f"(hidden_size={app.state.sbert_model.hidden_size})"
        )
    except Exception as e:
        logger.warning(f"⚠️ Could not load BERT model: {e}")
        logger.warning("⚠️ Using dummy model for similarity scoring (output may be less accurate)")
        # Create a dummy model object with encode and encode_words methods
        class DummyModel:
            hidden_size = 768

            def encode(self, texts):
                n = len(texts) if isinstance(texts, list) else 1
                return np.random.rand(n, self.hidden_size)

            def encode_words(self, text):
                words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
                return {w: np.random.rand(self.hidden_size) for w in set(words)}
        app.state.sbert_model = DummyModel()

    # ── Initialise LLM provider ───────────────────────────────────────────────
    logger.info(f"Initialising LLM provider '{settings.LLM_PROVIDER}'...")
    try:
        from ai_engine.llm.provider import get_provider
        app.state.llm_provider = get_provider(settings.LLM_PROVIDER)
        logger.info(f"✅ LLM provider '{app.state.llm_provider.name}' ready")
    except Exception as e:
        logger.warning(f"⚠️ Could not initialise LLM provider: {e}")
        logger.warning("⚠️ Resume rewriting will be unavailable until a valid provider is configured")
        app.state.llm_provider = None

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "model_loaded": hasattr(app.state, "sbert_model"),
        "version": "1.0.0"
    }