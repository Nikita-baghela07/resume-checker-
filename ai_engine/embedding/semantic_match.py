# AI Engine - Embedding module
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

# Similarity threshold above which two words are considered a semantic match.
# 0.75 was chosen empirically: below this value BERT often matches unrelated
# domain words (e.g. "engineer" ≈ "company"); above 0.9 near-synonyms such as
# "developer" / "programmer" are incorrectly rejected.
_WORD_SIM_THRESHOLD = 0.75

_STOP_WORDS = {
    "the", "this", "that", "with", "from", "have", "which", "your",
    "their", "been", "were", "also", "more", "used", "such", "them",
    "will", "able", "good", "well", "must", "want", "work", "role",
}


def compute_similarity(text_a: str, text_b: str, model) -> float:
    """
    Compute semantic similarity between two texts using BERT sentence embeddings.

    The model is expected to expose ``model.encode(list[str]) -> np.ndarray``
    (compatible with both ``SentenceTransformer`` and ``BertEmbedder``).

    Returns score 0-100.
    """
    try:
        emb_a = model.encode([text_a])
        emb_b = model.encode([text_b])
        raw = cosine_similarity(emb_a, emb_b)[0][0]

        # Normalize from [0.2, 0.9] range to [0, 100]
        normalized = (raw - 0.2) / (0.9 - 0.2)
        score = max(10.0, min(100.0, normalized * 100))
        return round(score, 1)
    except Exception:
        return 50.0


def compute_semantic_keyword_overlap(
    resume_text: str,
    job_description: str,
    model,
    *,
    min_word_len: int = 4,
    similarity_threshold: float = _WORD_SIM_THRESHOLD,
) -> float:
    """
    Compute keyword coverage using **BERT word-level (contextual) embeddings**.

    For each meaningful JD keyword, the function checks whether the resume
    contains a word whose BERT embedding is close enough (cosine similarity ≥
    *similarity_threshold*) to count as a match.  This catches semantic
    near-matches such as "developer" ≈ "engineer" that regex/stem approaches
    would miss.

    Falls back to plain token-overlap scoring if the model does not expose
    ``encode_words()``.

    Parameters
    ----------
    resume_text:          Plain text of the resume.
    job_description:      Plain text of the job description.
    model:                ``BertEmbedder`` instance (or any object with
                          ``encode_words(str) -> dict[str, np.ndarray]``).
    min_word_len:         Ignore JD words shorter than this many characters.
    similarity_threshold: Cosine similarity required to count a word as matched.

    Returns
    -------
    float  Score 0-100.
    """
    try:
        if not hasattr(model, "encode_words"):
            return compute_keyword_overlap(resume_text, job_description)

        jd_word_embs     = model.encode_words(job_description)
        resume_word_embs = model.encode_words(resume_text)

        jd_keywords = [
            w for w in jd_word_embs
            if len(w) >= min_word_len and w not in _STOP_WORDS
        ]

        if not jd_keywords:
            return 10.0

        resume_words = list(resume_word_embs.keys())
        if not resume_words:
            return 10.0

        # Stack resume embeddings once for efficient batch cosine similarity
        resume_matrix = np.vstack([resume_word_embs[w] for w in resume_words])

        matched = 0
        for jd_word in jd_keywords:
            jd_vec  = jd_word_embs[jd_word].reshape(1, -1)
            sims    = cosine_similarity(jd_vec, resume_matrix)[0]
            if sims.max() >= similarity_threshold:
                matched += 1

        score = max(10.0, min(100.0, matched / len(jd_keywords) * 100))
        return round(score, 1)

    except Exception:
        return compute_keyword_overlap(resume_text, job_description)


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
            return {w for w in words if len(w) >= 4 and w not in _STOP_WORDS}

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
