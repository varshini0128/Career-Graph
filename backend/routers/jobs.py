"""Job-related API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import db, queries
from ..deps import require_db
from ..models import Job, RelatedJob, Skill, Technology, Course, Project

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[Job], dependencies=[Depends(require_db)])
def list_jobs():
    return db.run_query(queries.ALL_JOBS)


@router.get("/{title}", response_model=Job, dependencies=[Depends(require_db)])
def job_detail(title: str):
    rows = db.run_query(queries.JOB_DETAIL, {"title": title})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Job '{title}' not found")
    return rows[0]


@router.get("/{title}/skills", response_model=list[Skill], dependencies=[Depends(require_db)])
def job_skills(title: str):
    return db.run_query(queries.JOB_SKILLS, {"title": title})


@router.get("/{title}/technologies", response_model=list[Technology], dependencies=[Depends(require_db)])
def job_technologies(title: str):
    """Multi-hop: Job -> Skill -> Technology, flattened to distinct technologies."""
    rows = db.run_query(queries.JOB_SKILLS_TECHNOLOGIES, {"title": title})
    tech_names: dict[str, dict] = {}
    for row in rows:
        for tech in row["technologies"]:
            if tech not in tech_names:
                tech_names[tech] = {"name": tech, "category": None, "description": None}
    return list(tech_names.values())


@router.get("/{title}/technologies-by-skill", dependencies=[Depends(require_db)])
def job_technologies_by_skill(title: str):
    """Multi-hop traversal result grouped by skill."""
    return db.run_query(queries.JOB_SKILLS_TECHNOLOGIES, {"title": title})


@router.get("/{title}/courses", dependencies=[Depends(require_db)])
def job_courses(title: str):
    """Job -> Skill <- Course, flattened."""
    rows = db.run_query(queries.JOB_SKILLS_COURSES, {"title": title})
    courses: dict[str, dict] = {}
    for row in rows:
        for c in row["courses"]:
            if c["title"] not in courses:
                courses[c["title"]] = c
    return list(courses.values())


@router.get("/{title}/projects", dependencies=[Depends(require_db)])
def job_projects(title: str):
    """Job -> Skill <- Project, flattened."""
    rows = db.run_query(queries.JOB_SKILLS_PROJECTS, {"title": title})
    projects: dict[str, dict] = {}
    for row in rows:
        for p in row["projects"]:
            if p["title"] not in projects:
                projects[p["title"]] = p
    return list(projects.values())


@router.get("/{title}/related", response_model=list[RelatedJob], dependencies=[Depends(require_db)])
def related_jobs(title: str, limit: int = Query(10, ge=1, le=50)):
    explicit = db.run_query(queries.JOB_RELATED_EXPLICIT, {"title": title})
    by_skills = db.run_query(queries.JOB_RELATED_BY_SKILLS, {"title": title})

    merged: dict[str, dict] = {}
    for row in explicit:
        merged[row["title"]] = {
            "title": row["title"],
            "category": row["category"],
            "shared_skills": [],
            "relation": row.get("relation"),
        }
    for row in by_skills:
        if row["title"] in merged:
            merged[row["title"]]["shared_skills"] = row["shared_skills"]
        else:
            merged[row["title"]] = {
                "title": row["title"],
                "category": row["category"],
                "shared_skills": row["shared_skills"],
                "relation": "shared_skills",
            }
    return list(merged.values())[:limit]
