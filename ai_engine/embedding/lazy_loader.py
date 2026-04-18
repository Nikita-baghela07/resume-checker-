"""
Optimized embedding service with lazy loading for production deployment.
Falls back to TF-IDF when SBERT model is unavailable (saves ~200 MB).
"""

import os
import logging
from typing import Optional
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)

# Global model cache
_sbert_model = None
_model_load_attempted = False

def _try_load_sbert_model():
    """Lazy load SBERT model only if explicitly enabled."""
    global _sbert_model, _model_load_attempted
    
    if _model_load_attempted:
        return _sbert_model
    
    _model_load_attempted = True
    enable_sbert = os.getenv("ENABLE_SBERT_MODEL", "false").lower() == "true"
    
    if not enable_sbert:
        logger.info("SBERT model disabled (production mode). Using TF-IDF fallback.")
        return None
    
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading SBERT model (all-MiniLM-L6-v2)...")
        _sbert_model = SentenceTransformer("all-MiniLM-L6-v2", cache_folder="/tmp/sbert_cache")
        logger.info("✓ SBERT model loaded successfully")
        return _sbert_model
    except Exception as e:
        logger.warning(f"Failed to load SBERT model: {e}. Using TF-IDF fallback.")
        return None

def get_embedding(text: str, model=None):
    """Get embedding - uses provided model or falls back to TF-IDF."""
    if not text or len(text.strip()) < 10:
        return None
    
    if model is None:
        model = _try_load_sbert_model()
    
    if model is None:
        # TF-IDF fallback (no embedding, just for compatibility)
        return None
    
    try:
        return model.encode([text])[0]
    except Exception as e:
        logger.warning(f"Embedding error: {e}")
        return None

def get_sbert_model(force_load: bool = False):
    """
    Get SBERT model if enabled.
    Args:
        force_load: Override ENABLE_SBERT_MODEL setting
    """
    if force_load:
        try:
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer("all-MiniLM-L6-v2", cache_folder="/tmp/sbert_cache")
        except Exception as e:
            logger.error(f"Failed to load SBERT: {e}")
            return None
    
    return _try_load_sbert_model()

def is_sbert_available() -> bool:
    """Check if SBERT model is available."""
    model = _try_load_sbert_model()
    return model is not None
