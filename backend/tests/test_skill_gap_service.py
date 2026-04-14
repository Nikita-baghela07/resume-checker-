"""Tests for skill_gap_service."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from app.services.skill_gap_service import detect_gaps, extract_skills, ALL_SKILLS, MASTER_SKILLS


def test_all_skills_no_duplicates():
    """Ensure the flattened skill list has no duplicates."""
    assert len(ALL_SKILLS) == len(set(ALL_SKILLS)), (
        "Duplicate skills found: "
        + str([s for s in ALL_SKILLS if ALL_SKILLS.count(s) > 1])
    )


def test_master_skills_no_cross_category_duplicates():
    """Ensure no skill appears in more than one category."""
    seen = {}
    for category, skills in MASTER_SKILLS.items():
        for skill in skills:
            assert skill not in seen, (
                f"Skill '{skill}' appears in both '{seen[skill]}' and '{category}'"
            )
            seen[skill] = category


def test_extract_skills_finds_known_skills():
    text = "We need Python, FastAPI, Docker and AWS experience."
    found = extract_skills(text)
    assert "Python" in found
    assert "FastAPI" in found
    assert "Docker" in found
    assert "AWS" in found


def test_extract_skills_empty_text():
    assert extract_skills("") == []


def test_extract_skills_no_match():
    assert extract_skills("We need a chef with cooking skills.") == []


@pytest.mark.asyncio
async def test_detect_gaps_returns_list():
    resume = "Python, React, Git"
    jd = "We need Python, Kubernetes, Docker, and AWS."
    gaps = await detect_gaps(resume, jd)
    assert isinstance(gaps, list)
    gap_skills = [g.skill for g in gaps]
    assert "Kubernetes" in gap_skills
    assert "Docker" in gap_skills


@pytest.mark.asyncio
async def test_detect_gaps_no_gaps():
    resume = "Python, Docker, Kubernetes, AWS"
    jd = "We need Python, Docker, Kubernetes, AWS."
    gaps = await detect_gaps(resume, jd)
    assert gaps == []


@pytest.mark.asyncio
async def test_detect_gaps_max_ten():
    resume = "nothing"
    jd = " ".join(ALL_SKILLS)  # JD mentions every skill
    gaps = await detect_gaps(resume, jd)
    assert len(gaps) <= 10


@pytest.mark.asyncio
async def test_detect_gaps_priority_order():
    """High priority gaps should come before low priority ones."""
    resume = "nothing"
    jd = "We need required Python. Docker is nice to have."
    gaps = await detect_gaps(resume, jd)
    priorities = [g.priority for g in gaps]
    priority_rank = {"High": 0, "Medium": 1, "Low": 2}
    for i in range(len(priorities) - 1):
        assert priority_rank[priorities[i]] <= priority_rank[priorities[i + 1]]
