"""Skill-gap analysis endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Body, Depends, HTTPException

from .. import db, queries
from ..deps import require_db
from ..models import SkillGapResult, Course, Project

router = APIRouter(prefix="/skill-gap", tags=["skill-gap"])


@router.post("", response_model=SkillGapResult, dependencies=[Depends(require_db)])
def analyze_skill_gap(
    target_job: str = Body(..., embed=True),
    have_skills: list[str] = Body(default=[], embed=True),
):
    rows = db.run_query(queries.SKILL_GAP, {"title": target_job})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Job '{target_job}' not found")

    required = set(rows[0]["required"])
    have = set(have_skills)

    matching = sorted(required & have)
    missing = sorted(required - have)

    coverage = round(len(matching) / len(required) * 100, 1) if required else 0.0

    recommended_courses: list[Course] = []
    recommended_projects: list[Project] = []

    if missing:
        course_rows = db.run_query(queries.GAP_COURSES, {"skills": list(missing)})
        seen_c: set[str] = set()
        for row in course_rows:
            for c in row["courses"]:
                if c["title"] not in seen_c:
                    seen_c.add(c["title"])
                    recommended_courses.append(Course(**c))

        project_rows = db.run_query(queries.GAP_PROJECTS, {"skills": list(missing)})
        seen_p: set[str] = set()
        for row in project_rows:
            for p in row["projects"]:
                if p["title"] not in seen_p:
                    seen_p.add(p["title"])
                    recommended_projects.append(Project(**p))

    return SkillGapResult(
        target_job=target_job,
        have_skills=sorted(have),
        missing_skills=missing,
        matching_skills=matching,
        coverage_pct=coverage,
        recommended_courses=recommended_courses,
        recommended_projects=recommended_projects,
    )
