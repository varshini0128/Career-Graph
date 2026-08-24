"""Shared Pydantic response models."""
from __future__ import annotations

from pydantic import BaseModel


class Job(BaseModel):
    title: str
    category: str | None = None
    description: str | None = None
    avg_salary: float | None = None


class Skill(BaseModel):
    name: str
    category: str | None = None
    description: str | None = None


class Technology(BaseModel):
    name: str
    category: str | None = None
    description: str | None = None


class Course(BaseModel):
    title: str
    provider: str | None = None
    url: str | None = None
    level: str | None = None
    hours: float | None = None


class Project(BaseModel):
    title: str
    description: str | None = None
    difficulty: str | None = None


class RelatedJob(BaseModel):
    title: str
    category: str | None = None
    shared_skills: list[str] = []
    relation: str | None = None


class SkillGapResult(BaseModel):
    target_job: str
    have_skills: list[str]
    missing_skills: list[str]
    matching_skills: list[str]
    coverage_pct: float
    recommended_courses: list[Course] = []
    recommended_projects: list[Project] = []


class ConnectionNode(BaseModel):
    id: str
    label: str
    type: str
    properties: dict = {}


class ConnectionEdge(BaseModel):
    source: str
    target: str
    type: str


class ConnectionGraph(BaseModel):
    nodes: list[ConnectionNode]
    edges: list[ConnectionEdge]
