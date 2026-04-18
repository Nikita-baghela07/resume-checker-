"""Module for rewriting resume content using LLM (Groq API)."""

import os
import re
import sys
import json
import logging
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from groq import Groq
from app.core.config import settings
from app.core.utils import extract_bullets
from ai_engine.embedding.semantic_match import compute_similarity, get_embedding

logger = logging.getLogger(__name__)

# Bullet prefixes to detect and preserve
_BULLET_PATTERN = re.compile(r'^([\s]*)([•\-\*●◦▪▸►✓✔◆■□▶→\d]+[.):]?\s+)(.*)')


def load_rewrite_prompt() -> str:
    """Load the rewrite prompt template."""
    prompt_path = os.path.join(
        os.path.dirname(__file__),
        '..', 'prompts', 'rewrite_prompt.txt'
    )
    if os.path.exists(prompt_path):
        with open(prompt_path, 'r') as f:
            return f.read()

    # Fallback prompt
    return (
        "You are an expert ATS resume optimizer.\n"
        "Rewrite each bullet to better match the job description using relevant keywords.\n"
        "Keep factual accuracy. Return ONLY a JSON array: "
        '[{"original": "...", "rewritten": "..."}]'
    )


def _extract_json_from_response(text: str) -> list:
    """
    Robustly extract a JSON array from LLM response text.
    Handles markdown code blocks, extra prose, nested JSON objects, etc.
    """
    # Strip markdown code fences
    text = re.sub(r'```(?:json)?', '', text).strip()

    # Try to find the outermost JSON array
    bracket_start = text.find('[')
    if bracket_start != -1:
        # Find the matching closing bracket
        depth = 0
        for i, ch in enumerate(text[bracket_start:], bracket_start):
            if ch == '[':
                depth += 1
            elif ch == ']':
                depth -= 1
                if depth == 0:
                    json_str = text[bracket_start:i+1]
                    try:
                        parsed = json.loads(json_str)
                        if isinstance(parsed, list):
                            return parsed
                    except json.JSONDecodeError:
                        break

    # Try to find a JSON object with rewritten_bullets key
    obj_start = text.find('{')
    if obj_start != -1:
        depth = 0
        for i, ch in enumerate(text[obj_start:], obj_start):
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    json_str = text[obj_start:i+1]
                    try:
                        parsed = json.loads(json_str)
                        if isinstance(parsed, dict):
                            return parsed.get('rewritten_bullets', [])
                    except json.JSONDecodeError:
                        break

    raise ValueError(f"Could not extract JSON array from response:\n{text[:500]}")


def _replace_bullet_in_text(full_text: str, original_bullet: str, rewritten_bullet: str) -> tuple[str, bool]:
    """
    Find the line in full_text that contains original_bullet and replace the WHOLE line.
    This is much more robust than partial string replacement.
    """
    original_clean = original_bullet.strip()
    if not original_clean:
        return full_text, False

    # 1. Exact or near-exact match for the content (ignoring leading bullet chars)
    # Escape for regex but be careful with whitespace
    escaped = re.escape(original_clean)
    
    # Pattern to find a line that HAS this bullet text, regardless of prefix
    # Matches: [Optional Prefix] [Original Bullet] [Optional Trailing Whitespace]
    line_pattern = re.compile(rf'(?m)^.*{escaped}.*$', re.IGNORECASE)
    
    match = line_pattern.search(full_text)
    if match:
        line_start, line_end = match.span()
        # We want to preserve the prefix if possible, OR let the LLM provide a new one.
        # Most professional resumes use the same bullet char consistently.
        # Let's try to see if there's a prefix on this specific line.
        current_line = match.group(0)
        prefix_match = _BULLET_PATTERN.match(current_line)
        
        if prefix_match:
            indent, bullet_char, _ = prefix_match.groups()
            new_line = f"{indent}{bullet_char}{rewritten_bullet}"
        else:
            # Fallback: if no prefix detected, just use the rewritten text
            new_line = rewritten_bullet

        new_text = full_text[:line_start] + new_line + full_text[line_end:]
        return new_text, True

    # 2. Fuzzy fallback: if exact line match fails, try matching first 20 chars
    if len(original_clean) > 20:
        short_escaped = re.escape(original_clean[:20])
        fuzzy_pattern = re.compile(rf'(?m)^.*{short_escaped}.*$', re.IGNORECASE)
        match = fuzzy_pattern.search(full_text)
        if match:
            line_start, line_end = match.span()
            new_text = full_text[:line_start] + rewritten_bullet + full_text[line_end:]
            return new_text, True

    return full_text, False




def rewrite_resume(resume_text: str, job_description: str, model, target_keywords: list[str] = None) -> tuple[str, list[dict]]:
    """
    Rewrite resume bullets using Groq API to match job description.

    Args:
        resume_text: Original resume text
        job_description: Target job description
        model: SBERT model (unused but kept for interface compatibility)
        target_keywords: Optional list of top keywords to prioritize

    Returns:
        Tuple of (optimized_full_text, list_of_diffs)
        where each diff is {"original": str, "rewritten": str}
    """
    # Validate API key
    api_key = settings.GROQ_API_KEY
    if not api_key or api_key.strip() == "" or "gsk_" not in api_key:
        logger.error(f"❌ GROQ_API_KEY is invalid or missing! Got: {repr(api_key[:20]) if api_key else 'EMPTY'}")
        bullets = extract_bullets(resume_text)
        return resume_text, [{"original": b, "rewritten": b} for b in bullets]

    logger.info(f"✅ Using Groq API key: {api_key[:20]}...")

    # Initialize Groq client
    try:
        import httpx
        client = Groq(
            api_key=api_key,
            http_client=httpx.Client()
        )
        logger.info("✅ Groq client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Groq client: {e}")
        bullets = extract_bullets(resume_text)
        return resume_text, [{"original": b, "rewritten": b} for b in bullets]

    # Extract bullets from resume
    bullets = extract_bullets(resume_text)
    
    # NEW: If extract_bullets still fails, treat paragraphs as bullets so AI always runs
    if not bullets and len(resume_text) > 100:
        logger.warning("⚠️ No formatted bullets found. Splitting by double-newlines as fallback.")
        bullets = [p.strip() for p in resume_text.split('\n\n') if 30 < len(p.strip()) < 500][:15]
    
    logger.info(f"[EXTRACT] Found {len(bullets)} bullets for optimization")

    if not bullets:
        logger.warning("[EXTRACT] No bullets found - returning unchanged")
        return resume_text, []

    # Load rewrite prompt
    system_prompt = load_rewrite_prompt()

    # Build user message — send bullets as a numbered list for clarity
    bullets_text = "\n".join(f"{i+1}. {b}" for i, b in enumerate(bullets[:20]))
    
    keywords_str = ""
    if target_keywords:
        keywords_str = f"\nTARGET KEYWORDS TO INCORPORATE:\n{', '.join(target_keywords)}\n"

    user_message = (
        f"Job Description:\n{job_description[:3000]}\n"
        f"{keywords_str}"
        f"\nResume Bullets to Optimize ({min(len(bullets), 20)} bullets):\n"
        f"{bullets_text}\n\n"
        "Rewrite every bullet to incorporate relevant keywords from the job description. "
        "Always improve — do NOT leave bullets unchanged unless truly impossible.\n"
        "Return ONLY a valid JSON array with no markdown fences:\n"
        '[{"original": "exact original text", "rewritten": "improved text"}, ...]'
    )

    try:
        logger.info(f"[GROQ] Calling Groq API with {settings.MODEL_NAME}...")
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            max_tokens=settings.MAX_TOKENS,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message}
            ],
            temperature=0.4  # Lower temperature = more consistent, keyword-accurate output
        )

        response_text = response.choices[0].message.content
        logger.info(f"[GROQ] Response length: {len(response_text)} chars")
        logger.info(f"[GROQ] Response preview: {response_text[:300]}")

        # Parse JSON robustly
        rewritten = _extract_json_from_response(response_text)
        logger.info(f"✅ Parsed {len(rewritten)} rewritten bullets from Groq")

    except Exception as e:
        logger.error(f"[ERROR] Groq API / JSON parse failed: {e}", exc_info=True)
        return resume_text, [{"original": b, "rewritten": b} for b in bullets]

    # Build diff list and reconstruct optimized text
    optimized_text = resume_text
    diff_list = []
    replacements_made = 0
    
    # Pre-calculate JD embedding for semantic validation
    jd_embedding = get_embedding(job_description, model) if model else None

    for i, original_bullet in enumerate(bullets[:20]):
        # Get corresponding rewritten item
        rewritten_text = original_bullet # Default
        if i < len(rewritten):
            item = rewritten[i]
            if isinstance(item, dict):
                rewritten_text = item.get("rewritten") or item.get("optimized") or original_bullet
            elif isinstance(item, str):
                rewritten_text = item
        
        rewritten_text = str(rewritten_text).strip()

        # --- HYBRID SEMANTIC VALIDATION ---
        # Only accept the change if it's semantically valid (similarity > 0.4) 
        # to prevent complete hallucinations, AND if it's better or different.
        is_changed = rewritten_text.lower() != original_bullet.strip().lower()
        
        if is_changed and model and jd_embedding is not None:
            # Optional: Ensure rewrite didn't lose the original meaning entirely
            # overlap = compute_similarity(original_bullet, rewritten_text, model)
            
            # Ensure rewrite is semantically helpful for the JD
            old_sim = compute_similarity(original_bullet, job_description, model, emb_b=jd_embedding)
            new_sim = compute_similarity(rewritten_text, job_description, model, emb_b=jd_embedding)
            
            # If the new version is worse semantically, discard it!
            if new_sim < old_sim - 5.0: # Allow slight variations for keyword stuffing
                logger.warning(f"⚠ Discarding low-quality rewrite for bullet {i} (semantic score dropped)")
                rewritten_text = original_bullet
                is_changed = False

        # Replace in full text if the bullet actually changed
        if is_changed:
            optimized_text, replaced = _replace_bullet_in_text(
                optimized_text, original_bullet, rewritten_text
            )
            if replaced:
                replacements_made += 1
                logger.info(f"✓ Optimized [{i}]: '{original_bullet[:30]}...' -> '{rewritten_text[:30]}...'")
            else:
                logger.warning(f"⚠ Match failed for bullet [{i}]: '{original_bullet[:40]}...'")
                is_changed = False # Set to false since replacement failed

        diff_list.append({
            "original": original_bullet.strip(),
            "rewritten": rewritten_text,
            "changed": is_changed
        })

    logger.info(f"✅ Optimization complete: {replacements_made} bullets updated in text")
    return optimized_text, diff_list

