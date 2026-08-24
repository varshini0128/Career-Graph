"""Cypher query strings for CognoDB.

All queries use parameters ($name) — user input is NEVER concatenated into Cypher.
"""
from __future__ import annotations

# --- Catalog queries -------------------------------------------------------

ALL_JOBS = """
MATCH (j:Job)
RETURN j.title AS title, j.category AS category, j.description AS description,
       j.avg_salary AS avg_salary
ORDER BY j.title
"""

ALL_SKILLS = """
MATCH (s:Skill)
RETURN s.name AS name, s.category AS category, s.description AS description
ORDER BY s.name
"""

ALL_TECHNOLOGIES = """
MATCH (t:Technology)
RETURN t.name AS name, t.category AS category, t.description AS description
ORDER BY t.name
"""

ALL_COURSES = """
MATCH (c:Course)
RETURN c.title AS title, c.provider AS provider, c.url AS url,
       c.level AS level, c.hours AS hours
ORDER BY c.title
"""

ALL_PROJECTS = """
MATCH (p:Project)
RETURN p.title AS title, p.description AS description, p.difficulty AS difficulty
ORDER BY p.title
"""

# --- Job detail queries ----------------------------------------------------

JOB_DETAIL = """
MATCH (j:Job {title: $title})
RETURN j.title AS title, j.category AS category, j.description AS description,
       j.avg_salary AS avg_salary
"""

JOB_SKILLS = """
MATCH (j:Job {title: $title})-[:REQUIRES]->(s:Skill)
RETURN s.name AS name, s.category AS category, s.description AS description
ORDER BY s.category, s.name
"""

# Multi-hop traversal: Job -> Skill -> Technology (MANDATORY)
JOB_SKILLS_TECHNOLOGIES = """
MATCH (j:Job {title: $title})-[:REQUIRES]->(s:Skill)-[:IMPLEMENTED_WITH]->(t:Technology)
RETURN s.name AS skill, collect(DISTINCT t.name) AS technologies
ORDER BY s.name
"""

# Job -> Skill <- Course
JOB_SKILLS_COURSES = """
MATCH (j:Job {title: $title})-[:REQUIRES]->(s:Skill)<-[:TEACHES]-(c:Course)
RETURN s.name AS skill, collect(DISTINCT {
  title: c.title, provider: c.provider, url: c.url, level: c.level, hours: c.hours
}) AS courses
ORDER BY s.name
"""

# Job -> Skill <- Project
JOB_SKILLS_PROJECTS = """
MATCH (j:Job {title: $title})-[:REQUIRES]->(s:Skill)<-[:DEMONSTRATES]-(p:Project)
RETURN s.name AS skill, collect(DISTINCT {
  title: p.title, description: p.description, difficulty: p.difficulty
}) AS projects
ORDER BY s.name
"""

# Related jobs: explicit RELATED_TO edges
JOB_RELATED_EXPLICIT = """
MATCH (j:Job {title: $title})-[r:RELATED_TO]->(related:Job)
RETURN related.title AS title, related.category AS category,
       toString(r.strength) AS relation
ORDER BY r.strength DESC, related.title
"""

# Related jobs: shared skills (Job -> Skill <- Job)
JOB_RELATED_BY_SKILLS = """
MATCH (j:Job {title: $title})-[:REQUIRES]->(s:Skill)<-[:REQUIRES]-(other:Job)
WHERE other.title <> $title
WITH other, collect(DISTINCT s.name) AS shared
RETURN other.title AS title, other.category AS category, shared AS shared_skills
ORDER BY size(shared) DESC, other.title
LIMIT 10
"""

# --- Skill-gap analysis ----------------------------------------------------

SKILL_GAP = """
MATCH (j:Job {title: $title})-[:REQUIRES]->(s:Skill)
WITH j, collect(s.name) AS required
RETURN required
"""

GAP_COURSES = """
MATCH (s:Skill)<-[:TEACHES]-(c:Course)
WHERE s.name IN $skills
RETURN s.name AS skill, collect(DISTINCT {
  title: c.title, provider: c.provider, url: c.url, level: c.level, hours: c.hours
}) AS courses
"""

GAP_PROJECTS = """
MATCH (s:Skill)<-[:DEMONSTRATES]-(p:Project)
WHERE s.name IN $skills
RETURN s.name AS skill, collect(DISTINCT {
  title: p.title, description: p.description, difficulty: p.difficulty
}) AS projects
"""

# --- Connection explorer (graph viz) --------------------------------------

CONNECTION_GRAPH = """
MATCH path = (j:Job {title: $title})-[:REQUIRES]->(s:Skill)
OPTIONAL MATCH (s)-[:IMPLEMENTED_WITH]->(t:Technology)
OPTIONAL MATCH (s)<-[:TEACHES]-(c:Course)
OPTIONAL MATCH (s)<-[:DEMONSTRATES]-(p:Project)
OPTIONAL MATCH (j)-[:RELATED_TO]->(r:Job)
WITH nodes(path) AS base_nodes,
     collect(DISTINCT t) AS techs,
     collect(DISTINCT c) AS courses,
     collect(DISTINCT p) AS projects,
     collect(DISTINCT r) AS related
RETURN base_nodes, techs, courses, projects, related
"""

# --- Health ----------------------------------------------------------------

HEALTH = "RETURN 1 AS ok"
