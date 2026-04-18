import sys
import os
import logging

# Ensure imports work
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai_engine.rewriting.resume_rewriter import rewrite_resume
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)

def test_optimization():
    print("--- Diagnostic Optimization Test ---")
    
    resume = """
    Software Engineer
    - Developed APIs in Java.
    - Worked with SQL databases.
    """
    
    jd = "Seeking a Senior Backend Engineer proficient in Java, Spring Boot, and PostgreSQL (SQL)."
    
    print("Loading model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Running optimization...")
    optimized_text, diff = rewrite_resume(resume, jd, model, target_keywords=["Spring Boot", "PostgreSQL"])
    
    print("\n--- RESULTS ---")
    print(f"Optimized Text:\n{optimized_text}")
    print("\nDiff Items:")
    for item in diff:
        print(f"Original: {item['original']}")
        print(f"Rewritten: {item['rewritten']}")
        print(f"Changed: {item.get('changed', 'N/A')}")
        print("-" * 20)

if __name__ == "__main__":
    test_optimization()
