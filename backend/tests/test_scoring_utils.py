"""Tests for scoring_service utilities."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app.core.utils import normalize_score, extract_sections


class TestNormalizeScore:
    def test_midpoint_value(self):
        score = normalize_score(0.55)
        assert 10.0 <= score <= 100.0

    def test_maximum_clamp(self):
        assert normalize_score(1.0) == 100.0

    def test_minimum_clamp(self):
        assert normalize_score(0.0) == 10.0

    def test_perfect_similarity(self):
        assert normalize_score(0.9) == 100.0

    def test_returns_float(self):
        assert isinstance(normalize_score(0.5), float)


class TestExtractSections:
    SAMPLE_RESUME = """
John Doe

SKILLS
Python, FastAPI, Docker

EXPERIENCE
Backend Developer at Acme Corp (2022-Present)
Built REST APIs

EDUCATION
B.S. Computer Science, State University (2020)

SUMMARY
Experienced developer.
"""

    def test_returns_four_sections(self):
        sections = extract_sections(self.SAMPLE_RESUME)
        assert set(sections.keys()) == {"skills", "experience", "education", "summary"}

    def test_skills_section_populated(self):
        sections = extract_sections(self.SAMPLE_RESUME)
        assert "Python" in sections["skills"]

    def test_experience_section_populated(self):
        sections = extract_sections(self.SAMPLE_RESUME)
        assert "Acme Corp" in sections["experience"]

    def test_education_section_populated(self):
        sections = extract_sections(self.SAMPLE_RESUME)
        assert "Computer Science" in sections["education"]

    def test_empty_resume(self):
        sections = extract_sections("")
        for v in sections.values():
            assert v == ""
