"""Connection explorer — returns nodes/edges for graph visualization."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from .. import db, queries
from ..deps import require_db
from ..models import ConnectionGraph, ConnectionNode, ConnectionEdge

router = APIRouter(prefix="/connections", tags=["connections"])


@router.get(
    "/{title}",
    response_model=ConnectionGraph,
    dependencies=[Depends(require_db)],
)
def connection_graph(title: str):
    rows = db.run_query(queries.CONNECTION_GRAPH, {"title": title})

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{title}' not found",
        )

    nodes: dict[str, ConnectionNode] = {}
    edges: set[tuple[str, str, str]] = set()

    def add_node(node, type_label: str):
        if node is None:
            return

        name = node.get("title") or node.get("name")
        if not name:
            return

        nid = f"{type_label}:{name}"

        if nid not in nodes:
            props = {k: v for k, v in node.items() if v is not None}
            label = props.get("title") or props.get("name") or type_label

            nodes[nid] = ConnectionNode(
                id=nid,
                label=label,
                type=type_label,
                properties=props,
            )

    # ------------------------------------------------------------------
    # Nodes returned by the main connection query
    # ------------------------------------------------------------------

    for row in rows:
        for node in row.get("base_nodes", []):
            add_node(
                node,
                "Job" if "title" in node and "category" in node else "Skill",
            )

        for node in row.get("techs", []):
            add_node(node, "Technology")

        for node in row.get("courses", []):
            add_node(node, "Course")

        for node in row.get("projects", []):
            add_node(node, "Project")

        for node in row.get("related", []):
            add_node(node, "Job")

    # ------------------------------------------------------------------
    # Job -> Skill
    # ------------------------------------------------------------------

    job_id = f"Job:{title}"

    skill_rows = db.run_query(
        queries.JOB_SKILLS,
        {"title": title},
    )

    for skill in skill_rows:
        skill_id = f"Skill:{skill['name']}"

        add_node(skill, "Skill")
        edges.add(
            (job_id, skill_id, "REQUIRES")
        )

    # ------------------------------------------------------------------
    # Skill -> Technology
    # ------------------------------------------------------------------

    tech_rows = db.run_query(
        queries.JOB_SKILLS_TECHNOLOGIES,
        {"title": title},
    )

    for row in tech_rows:
        skill_id = f"Skill:{row['skill']}"

        for technology in row["technologies"]:
            technology_id = f"Technology:{technology}"

            edges.add(
                (skill_id, technology_id, "IMPLEMENTED_WITH")
            )

    # ------------------------------------------------------------------
    # Course -> Skill
    # ------------------------------------------------------------------

    course_rows = db.run_query(
        queries.JOB_SKILLS_COURSES,
        {"title": title},
    )

    for row in course_rows:
        skill_id = f"Skill:{row['skill']}"

        for course in row["courses"]:
            course_id = f"Course:{course['title']}"

            add_node(course, "Course")

            edges.add(
                (course_id, skill_id, "TEACHES")
            )

    # ------------------------------------------------------------------
    # Project -> Skill
    # ------------------------------------------------------------------

    project_rows = db.run_query(
        queries.JOB_SKILLS_PROJECTS,
        {"title": title},
    )

    for row in project_rows:
        skill_id = f"Skill:{row['skill']}"

        for project in row["projects"]:
            project_id = f"Project:{project['title']}"

            add_node(project, "Project")

            edges.add(
                (project_id, skill_id, "DEMONSTRATES")
            )

    # ------------------------------------------------------------------
    # Job -> Related Job
    # ------------------------------------------------------------------

    related_rows = db.run_query(
        queries.JOB_RELATED_BY_SKILLS,
        {"title": title},
    )

    for row in related_rows:
        related_id = f"Job:{row['title']}"

        add_node(
            {
                "title": row["title"],
                "category": row.get("category"),
            },
            "Job",
        )

        edges.add(
            (job_id, related_id, "RELATED_TO")
        )

    edge_list = [
        ConnectionEdge(
            source=source,
            target=target,
            type=relationship_type,
        )
        for source, target, relationship_type in edges
    ]

    return ConnectionGraph(
        nodes=list(nodes.values()),
        edges=edge_list,
    )