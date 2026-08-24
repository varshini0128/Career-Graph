"""Connection explorer — returns nodes/edges for graph visualization."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from .. import db, queries
from ..deps import require_db
from ..models import ConnectionGraph, ConnectionNode, ConnectionEdge

router = APIRouter(prefix="/connections", tags=["connections"])


@router.get("/{title}", response_model=ConnectionGraph, dependencies=[Depends(require_db)])
def connection_graph(title: str):
    rows = db.run_query(queries.CONNECTION_GRAPH, {"title": title})
    if not rows:
        raise HTTPException(status_code=404, detail=f"Job '{title}' not found")

    nodes: dict[str, ConnectionNode] = {}
    edges: set[tuple[str, str, str]] = set()

    def add_node(node, type_label: str):
        if node is None:
            return
        nid = f"{type_label}:{node.get('title') or node.get('name')}"
        if nid not in nodes:
            props = {k: v for k, v in node.items() if v is not None}
            label = props.get("title") or props.get("name") or type_label
            nodes[nid] = ConnectionNode(id=nid, label=label, type=type_label, properties=props)

    for row in rows:
        for node in row.get("base_nodes", []):
            add_node(node, "Job" if "title" in node and "category" in node else "Skill")
        for node in row.get("techs", []):
            add_node(node, "Technology")
        for node in row.get("courses", []):
            add_node(node, "Course")
        for node in row.get("projects", []):
            add_node(node, "Project")
        for node in row.get("related", []):
            add_node(node, "Job")

        for rel in row.get("base_rels", []):
            src = f"Job:{title}"
            s = rel.get("s") or {}
            tgt = f"Skill:{s.get('name', '')}"
            edges.add((src, tgt, rel.get("type", "REQUIRES")))

    # Build edges from base_nodes more reliably
    edges = set()
    job_id = f"Job:{title}"
    for row in rows:
        for node in row.get("base_nodes", []):
            if node.get("title") == title:
                continue
        # Job -> Skill
        skill_rows = db.run_query(queries.JOB_SKILLS, {"title": title})
        for s in skill_rows:
            sid = f"Skill:{s['name']}"
            edges.add((job_id, sid, "REQUIRES"))

    # Skill -> Technology
    tech_rows = db.run_query(queries.JOB_SKILLS_TECHNOLOGIES, {"title": title})
    for row in tech_rows:
        sid = f"Skill:{row['skill']}"
        for t in row["technologies"]:
            tid = f"Technology:{t}"
            edges.add((sid, tid, "IMPLEMENTED_WITH"))

    # Skill <- Course
    course_rows = db.run_query(queries.JOB_SKILLS_COURSES, {"title": title})
    for row in course_rows:
        sid = f"Skill:{row['skill']}"
        for c in row["courses"]:
            cid = f"Course:{c['title']}"
            edges.add((cid, sid, "TEACHES"))

    # Skill <- Project
    proj_rows = db.run_query(queries.JOB_SKILLS_PROJECTS, {"title": title})
    for row in proj_rows:
        sid = f"Skill:{row['skill']}"
        for p in row["projects"]:
            pid = f"Project:{p['title']}"
            edges.add((pid, sid, "DEMONSTRATES"))

    # Job -> Related Job
    related_rows = db.run_query(queries.JOB_RELATED_BY_SKILLS, {"title": title})
    for row in related_rows:
        rid = f"Job:{row['title']}"
        edges.add((job_id, rid, "RELATED_TO"))

    edge_list = [ConnectionEdge(source=s, target=t, type=ty) for s, t, ty in edges]
    return ConnectionGraph(nodes=list(nodes.values()), edges=edge_list)
