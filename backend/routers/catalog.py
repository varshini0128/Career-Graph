"""Catalog routes for skills, technologies, courses, projects."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from .. import db, queries
from ..deps import require_db
from ..models import Skill, Technology, Course, Project

router = APIRouter(tags=["catalog"])


@router.get("/skills", response_model=list[Skill], dependencies=[Depends(require_db)])
def list_skills():
    return db.run_query(queries.ALL_SKILLS)


@router.get("/technologies", response_model=list[Technology], dependencies=[Depends(require_db)])
def list_technologies():
    return db.run_query(queries.ALL_TECHNOLOGIES)


@router.get("/courses", response_model=list[Course], dependencies=[Depends(require_db)])
def list_courses():
    return db.run_query(queries.ALL_COURSES)


@router.get("/projects", response_model=list[Project], dependencies=[Depends(require_db)])
def list_projects():
    return db.run_query(queries.ALL_PROJECTS)
