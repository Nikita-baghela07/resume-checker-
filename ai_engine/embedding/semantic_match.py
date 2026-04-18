import re
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

def get_embedding(text: str, model):
    """Helper to get embedding for a single text string."""
    if not model or not text.strip():
        return None
    try:
        return model.encode([text])[0]
    except Exception as e:
        logger.warning(f"Embedding error: {e}")
        return None

def compute_similarity(text_a: str, text_b: str, model=None, emb_a=None, emb_b=None) -> float:
    """
    Compute semantic similarity using a Hybrid combination of SBERT semantics and TF-IDF.
    Supports pre-computed embeddings (emb_a, emb_b) to save time.
    Returns score 0-100.
    """
    try:
        # If texts are empty or too small, return baseline
        if not text_a or not text_b or len(text_a.strip()) < 10 or len(text_b.strip()) < 10:
            return 20.0
            
        # 1. TF-IDF Score (normalized consistently)
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        tfidf_matrix = vectorizer.fit_transform([text_a, text_b])
        tfidf_raw = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        # Normalize: TF-IDF values are [0, 1], scale to [0-100] with boost
        tfidf_score = min(100.0, max(10.0, tfidf_raw * 100))
        
        # 2. SBERT Score (if model/embeddings available)
        if model is not None or (emb_a is not None and emb_b is not None):
            # Use pre-computed embeddings if provided, otherwise compute them
            if emb_a is None and model is not None:
                emb_a = model.encode([text_a])[0]
            if emb_b is None and model is not None:
                emb_b = model.encode([text_b])[0]
            
            # Both embeddings must be available
            if emb_a is None or emb_b is None:
                return round(tfidf_score, 1)
                
            sbert_raw = cosine_similarity([emb_a], [emb_b])[0][0]
            # SBERT normalization (cosine similarity is [-1, 1], typically [0, 1])
            # Normalize to 0-1 range first, then boost to 0-100
            sbert_normalized = max(0.0, (sbert_raw + 1.0) / 2.0)  # Map [-1, 1] → [0, 1]
            sbert_score = max(10.0, min(100.0, sbert_normalized * 100))
            
            # Hybrid Score (50% SBERT, 50% TF-IDF) - both synchronized to 0-100
            hybrid_score = (sbert_score * 0.5) + (tfidf_score * 0.5)
            return round(hybrid_score, 1)
        
        # Fallback to pure TF-IDF
        return round(tfidf_score, 1)
    except Exception as e:
        print(f"Similarity Error: {e}")
        return 50.0

def compute_similarity_batch(text_a: str, texts_b: list[str], model):
    """Compute similarities between one text and many others in one batch using SBERT."""
    if not model or not text_a or not texts_b:
        return [50.0] * len(texts_b)
    
    try:
        embeddings = model.encode([text_a] + texts_b)
        emb_a = embeddings[0]
        embs_b = embeddings[1:]
        
        sims = cosine_similarity([emb_a], embs_b)[0]
        scores = []
        for raw in sims:
            # Consistent normalization: [-1, 1] → [0, 1] → [0, 100]
            norm = max(0.0, (raw + 1.0) / 2.0)
            scores.append(max(10.0, min(100.0, norm * 100)))
        return scores
    except Exception as e:
        print(f"Batch similarity error: {e}")
        return [50.0] * len(texts_b)



def compute_keyword_overlap(resume_text: str, job_description: str) -> float:
    """
    Compute keyword overlap between resume and job description.
    Extracts keywords (words 4+ chars) and calculates overlap percentage.
    Returns score 0-100.
    """
    try:
        # Extract keywords (words of 4+ characters, case-insensitive)
        def extract_keywords(text: str) -> set:
            words = re.findall(r'\b\w+\b', text.lower())
            # Filter: 4+ chars, exclude common words
            common = {'the', 'this', 'that', 'with', 'from', 'have', 'which', 'your',
                     'their', 'been', 'were', 'also', 'more', 'used', 'such', 'them'}
            return {w for w in words if len(w) >= 4 and w not in common}
        
        resume_keywords = extract_keywords(resume_text)
        jd_keywords = extract_keywords(job_description)
        
        if not jd_keywords:
            return 10.0
        
        # Calculate overlap
        overlap = len(resume_keywords & jd_keywords)
        coverage = overlap / len(jd_keywords)
        
        # Normalize to 0-100 scale
        score = max(10.0, min(100.0, coverage * 100))
        return round(score, 1)
    
    except Exception:
        return 50.0
