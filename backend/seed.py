"""Seed CareerGraph data into CognoDB using parameterized Cypher.

Run:  python -m backend.seed

Creates constraints, clears existing data, then loads realistic jobs, skills,
technologies, courses, projects and all relationships.
"""
from __future__ import annotations

import logging
from neo4j import Driver

from .db import get_driver, verify_connectivity

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("careergraph.seed")

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

JOBS = [
    {"title": "Frontend Developer", "category": "Engineering", "description": "Builds user interfaces for web applications using modern JavaScript frameworks.", "avg_salary": 95000.0},
    {"title": "Backend Developer", "category": "Engineering", "description": "Designs and implements server-side logic, APIs, and data pipelines.", "avg_salary": 105000.0},
    {"title": "Full-Stack Developer", "category": "Engineering", "description": "Works across the entire stack — frontend, backend, and infrastructure.", "avg_salary": 110000.0},
    {"title": "Data Scientist", "category": "Data", "description": "Analyzes data to build predictive models and extract business insights.", "avg_salary": 120000.0},
    {"title": "Machine Learning Engineer", "category": "Data", "description": "Productionizes ML models and builds scalable inference systems.", "avg_salary": 140000.0},
    {"title": "DevOps Engineer", "category": "Engineering", "description": "Automates deployment, scaling, and monitoring of cloud infrastructure.", "avg_salary": 125000.0},
    {"title": "Cloud Solutions Architect", "category": "Engineering", "description": "Designs cloud architecture and migration strategies for enterprise systems.", "avg_salary": 150000.0},
    {"title": "Data Engineer", "category": "Data", "description": "Builds and maintains data pipelines, warehouses, and ETL systems.", "avg_salary": 115000.0},
    {"title": "Mobile Developer", "category": "Engineering", "description": "Develops native and cross-platform mobile applications.", "avg_salary": 100000.0},
    {"title": "Security Engineer", "category": "Security", "description": "Protects systems and applications from security threats and vulnerabilities.", "avg_salary": 130000.0},
]

SKILLS = [
    {"name": "JavaScript", "category": "Programming", "description": "Core language of the web — runs in browsers and on servers via Node.js."},
    {"name": "TypeScript", "category": "Programming", "description": "Typed superset of JavaScript that compiles to plain JavaScript."},
    {"name": "React", "category": "Frontend", "description": "Component-based UI library for building single-page applications."},
    {"name": "CSS", "category": "Frontend", "description": "Styling language for web pages — includes Flexbox and Grid layout."},
    {"name": "HTML", "category": "Frontend", "description": "Markup language for structuring web content."},
    {"name": "Python", "category": "Programming", "description": "High-level, general-purpose language popular in data, scripting, and backend development."},
    {"name": "SQL", "category": "Database", "description": "Query language for relational databases."},
    {"name": "NoSQL", "category": "Database", "description": "Design patterns for document, key-value, and graph databases."},
    {"name": "Distributed Systems", "category": "Architecture", "description": "Designing systems that span multiple nodes — consistency, availability, partition tolerance."},
    {"name": "Machine Learning", "category": "AI/ML", "description": "Building models that learn patterns from data."},
    {"name": "Deep Learning", "category": "AI/ML", "description": "Neural-network-based learning — CNNs, RNNs, transformers."},
    {"name": "Statistics", "category": "Math", "description": "Probability, hypothesis testing, regression, and Bayesian methods."},
    {"name": "Data Visualization", "category": "Data", "description": "Communicating insights through charts, dashboards, and interactive visualizations."},
    {"name": "Cloud Computing", "category": "Infrastructure", "description": "On-demand compute, storage, and services from cloud providers."},
    {"name": "Containerization", "category": "Infrastructure", "description": "Packaging applications and dependencies into portable containers."},
    {"name": "CI/CD", "category": "Infrastructure", "description": "Continuous integration and continuous delivery pipelines."},
    {"name": "System Design", "category": "Architecture", "description": "Designing scalable, reliable, and maintainable software systems."},
    {"name": "API Design", "category": "Architecture", "description": "Designing RESTful and GraphQL APIs — versioning, pagination, error handling."},
    {"name": "Mobile Development", "category": "Mobile", "description": "Building native and cross-platform mobile applications."},
    {"name": "Cybersecurity", "category": "Security", "description": "Threat modeling, vulnerability assessment, and secure coding practices."},
    {"name": "Data Modeling", "category": "Database", "description": "Designing schemas for relational and graph databases."},
    {"name": "Graph Theory", "category": "Math", "description": "Nodes, edges, traversal algorithms, and graph analytics."},
    {"name": "ETL Pipelines", "category": "Data", "description": "Extract, transform, load workflows for data integration."},
    {"name": "Kotlin", "category": "Programming", "description": "Modern JVM language used for Android and backend development."},
    {"name": "Swift", "category": "Programming", "description": "Apple's language for iOS, macOS, and server-side development."},
]

TECHNOLOGIES = [
    {"name": "Node.js", "category": "Runtime", "description": "JavaScript runtime built on Chrome's V8 engine."},
    {"name": "Next.js", "category": "Framework", "description": "React framework with SSR, routing, and API routes."},
    {"name": "Tailwind CSS", "category": "Framework", "description": "Utility-first CSS framework for rapid UI development."},
    {"name": "Vite", "category": "Build Tool", "description": "Fast frontend build tool and dev server."},
    {"name": "Django", "category": "Framework", "description": "Python web framework with ORM, auth, and admin built in."},
    {"name": "FastAPI", "category": "Framework", "description": "Modern Python async web framework with automatic OpenAPI docs."},
    {"name": "PostgreSQL", "category": "Database", "description": "Advanced open-source relational database."},
    {"name": "Neo4j", "category": "Database", "description": "Graph database storing data as nodes and relationships."},
    {"name": "MongoDB", "category": "Database", "description": "Document-oriented NoSQL database."},
    {"name": "Docker", "category": "DevOps", "description": "Container platform for building and running portable applications."},
    {"name": "Kubernetes", "category": "DevOps", "description": "Container orchestration for scaling and managing clusters."},
    {"name": "AWS", "category": "Cloud", "description": "Amazon Web Services — compute, storage, and managed services."},
    {"name": "GCP", "category": "Cloud", "description": "Google Cloud Platform — compute, data, and AI services."},
    {"name": "GitHub Actions", "category": "DevOps", "description": "CI/CD workflows integrated into GitHub repositories."},
    {"name": "TensorFlow", "category": "AI/ML", "description": "End-to-end open-source ML platform from Google."},
    {"name": "PyTorch", "category": "AI/ML", "description": "Deep learning framework with dynamic computation graphs."},
    {"name": "scikit-learn", "category": "AI/ML", "description": "Classical ML library for Python — regression, classification, clustering."},
    {"name": "Pandas", "category": "Data", "description": "Data analysis and manipulation library for Python."},
    {"name": "D3.js", "category": "Visualization", "description": "JavaScript library for data-driven documents and visualizations."},
    {"name": "React Native", "category": "Mobile", "description": "Cross-platform mobile framework using React."},
    {"name": "SwiftUI", "category": "Mobile", "description": "Declarative UI framework for iOS development."},
    {"name": "Kafka", "category": "Data", "description": "Distributed event streaming platform for real-time data pipelines."},
    {"name": "Spark", "category": "Data", "description": "Unified analytics engine for large-scale data processing."},
    {"name": "GraphQL", "category": "API", "description": "Query language and runtime for APIs."},
]

COURSES = [
    {"title": "Modern JavaScript From Scratch", "provider": "Udemy", "url": "https://www.udemy.com/course/modern-javascript", "level": "Beginner", "hours": 24.0},
    {"title": "React — The Complete Guide", "provider": "Udemy", "url": "https://www.udemy.com/course/react-complete-guide", "level": "Intermediate", "hours": 48.0},
    {"title": "TypeScript for Professionals", "provider": "Frontend Masters", "url": "https://frontendmasters.com/courses/typescript", "level": "Intermediate", "hours": 18.0},
    {"title": "CSS Grid & Flexbox Mastery", "provider": "CSS Tricks", "url": "https://css-tricks.com/course/grid-flexbox", "level": "Beginner", "hours": 12.0},
    {"title": "Python for Everybody", "provider": "Coursera", "url": "https://www.coursera.org/specializations/python", "level": "Beginner", "hours": 30.0},
    {"title": "Django for APIs", "provider": "TestDriven.io", "url": "https://testdriven.io/courses/django-api", "level": "Intermediate", "hours": 20.0},
    {"title": "FastAPI — The Complete Course", "provider": "Udemy", "url": "https://www.udemy.com/course/fastapi-course", "level": "Intermediate", "hours": 16.0},
    {"title": "SQL & Database Design", "provider": "Coursera", "url": "https://www.coursera.org/learn/sql-data-science", "level": "Beginner", "hours": 28.0},
    {"title": "Graph Databases with Neo4j", "provider": "Neo4j GraphAcademy", "url": "https://graphacademy.neo4j.com", "level": "Intermediate", "hours": 14.0},
    {"title": "Machine Learning Specialization", "provider": "Coursera", "url": "https://www.coursera.org/specializations/machine-learning", "level": "Intermediate", "hours": 60.0},
    {"title": "Deep Learning Specialization", "provider": "Coursera", "url": "https://www.coursera.org/specializations/deep-learning", "level": "Advanced", "hours": 80.0},
    {"title": "Practical Statistics for Data Scientists", "provider": "O'Reilly", "url": "https://www.oreilly.com/library/view/practical-statistics-for", "level": "Intermediate", "hours": 22.0},
    {"title": "Data Visualization with D3.js", "provider": "Udemy", "url": "https://www.udemy.com/course/d3-course", "level": "Intermediate", "hours": 26.0},
    {"title": "Docker & Kubernetes — The Practical Guide", "provider": "Udemy", "url": "https://www.udemy.com/course/docker-kubernetes", "level": "Intermediate", "hours": 34.0},
    {"title": "AWS Certified Solutions Architect", "provider": "A Cloud Guru", "url": "https://acloud.guru/learn/aws-solutions-architect", "level": "Intermediate", "hours": 40.0},
    {"title": "CI/CD with GitHub Actions", "provider": "GitHub Learning Lab", "url": "https://lab.github.com/courses", "level": "Beginner", "hours": 10.0},
    {"title": "System Design Primer", "provider": "ByteByteGo", "url": "https://bytebytego.com", "level": "Advanced", "hours": 35.0},
    {"title": "API Design Best Practices", "provider": "Google", "url": "https://cloud.google.com/apis/design", "level": "Intermediate", "hours": 8.0},
    {"title": "Mobile Development with React Native", "provider": "Meta", "url": "https://www.coursera.org/learn/react-native", "level": "Intermediate", "hours": 32.0},
    {"title": "iOS Development with SwiftUI", "provider": "Stanford", "url": "https://cs193p.sites.stanford.edu", "level": "Intermediate", "hours": 30.0},
    {"title": "Web Security Fundamentals", "provider": "OWASP", "url": "https://owasp.org/www-project-web-security-fundamentals", "level": "Intermediate", "hours": 18.0},
    {"title": "Data Engineering with Apache Spark", "provider": "Databricks Academy", "url": "https://www.databricks.com/learn", "level": "Advanced", "hours": 28.0},
    {"title": "Building ETL Pipelines", "provider": "DataCamp", "url": "https://www.datacamp.com/courses/etl-pipelines", "level": "Intermediate", "hours": 16.0},
    {"title": "Kotlin for Android Developers", "provider": "Google", "url": "https://developer.android.com/courses/kotlin-android", "level": "Intermediate", "hours": 24.0},
    {"title": "Graph Theory and Network Science", "provider": "MIT OCW", "url": "https://ocw.mit.edu/courses/graph-theory", "level": "Advanced", "hours": 40.0},
]

PROJECTS = [
    {"title": "Personal Portfolio Website", "description": "Build a responsive portfolio with React and Tailwind CSS, deployed to Vercel.", "difficulty": "Beginner"},
    {"title": "Real-Time Chat App", "description": "WebSocket-based chat application with rooms, typing indicators, and presence.", "difficulty": "Intermediate"},
    {"title": "E-Commerce Product Catalog", "description": "Server-rendered catalog with search, filtering, and cart — built with Next.js.", "difficulty": "Intermediate"},
    {"title": "REST API with Authentication", "description": "JWT-authenticated CRUD API with role-based access control using FastAPI.", "difficulty": "Intermediate"},
    {"title": "GraphQL Gateway", "description": "Federated GraphQL API aggregating multiple microservices.", "difficulty": "Advanced"},
    {"title": "Movie Recommendation Engine", "description": "Collaborative-filtering recommender using Pandas and scikit-learn.", "difficulty": "Intermediate"},
    {"title": "Image Classifier with CNNs", "description": "Train a convolutional neural network on CIFAR-10 using PyTorch.", "difficulty": "Advanced"},
    {"title": "Sentiment Analysis API", "description": "Fine-tune a transformer model for sentiment classification and serve via FastAPI.", "difficulty": "Advanced"},
    {"title": "Interactive Dashboard", "description": "Real-time analytics dashboard with D3.js charts and WebSocket updates.", "difficulty": "Intermediate"},
    {"title": "Dockerized Microservices", "description": "Multi-service app orchestrated with Docker Compose and Kubernetes.", "difficulty": "Advanced"},
    {"title": "CI/CD Pipeline from Scratch", "description": "Build, test, and deploy a full-stack app automatically with GitHub Actions.", "difficulty": "Intermediate"},
    {"title": "Cloud Migration Project", "description": "Migrate a monolithic app to AWS with autoscaling and managed database.", "difficulty": "Advanced"},
    {"title": "Data Warehouse Pipeline", "description": "ETL pipeline ingesting CSV/API data into a Spark-backed warehouse.", "difficulty": "Advanced"},
    {"title": "Streaming Analytics with Kafka", "description": "Real-time stream processing pipeline using Kafka and Spark Structured Streaming.", "difficulty": "Advanced"},
    {"title": "Cross-Platform Mobile App", "description": "Social-feed mobile app built with React Native and Expo.", "difficulty": "Intermediate"},
    {"title": "iOS Weather App", "description": "Native iOS weather app with SwiftUI and CoreLocation.", "difficulty": "Intermediate"},
    {"title": "Security Audit Tool", "description": "Automated scanner that checks dependencies for known CVEs and misconfigurations.", "difficulty": "Advanced"},
    {"title": "Knowledge Graph Builder", "description": "Ingest structured data into Neo4j and expose a query API for relationships.", "difficulty": "Advanced"},
]

# Job -> [skills]
JOB_SKILLS = {
    "Frontend Developer": ["JavaScript", "TypeScript", "React", "CSS", "HTML", "API Design"],
    "Backend Developer": ["Python", "SQL", "NoSQL", "API Design", "System Design", "Distributed Systems"],
    "Full-Stack Developer": ["JavaScript", "TypeScript", "React", "Python", "SQL", "API Design", "System Design"],
    "Data Scientist": ["Python", "SQL", "Statistics", "Machine Learning", "Data Visualization"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "System Design", "Distributed Systems"],
    "DevOps Engineer": ["Cloud Computing", "Containerization", "CI/CD", "System Design", "Distributed Systems"],
    "Cloud Solutions Architect": ["Cloud Computing", "System Design", "Distributed Systems", "API Design", "Containerization"],
    "Data Engineer": ["Python", "SQL", "ETL Pipelines", "Distributed Systems", "Data Modeling"],
    "Mobile Developer": ["Mobile Development", "JavaScript", "TypeScript", "API Design", "Kotlin"],
    "Security Engineer": ["Cybersecurity", "System Design", "API Design", "Distributed Systems", "Python"],
}

# Skill -> [technologies]
SKILL_TECHNOLOGIES = {
    "JavaScript": ["Node.js", "Next.js", "Vite"],
    "TypeScript": ["Node.js", "Next.js", "Vite"],
    "React": ["Next.js", "Tailwind CSS"],
    "CSS": ["Tailwind CSS"],
    "HTML": ["Tailwind CSS"],
    "Python": ["Django", "FastAPI", "Pandas", "scikit-learn", "PyTorch", "TensorFlow"],
    "SQL": ["PostgreSQL"],
    "NoSQL": ["MongoDB", "Neo4j"],
    "Machine Learning": ["scikit-learn", "TensorFlow", "PyTorch"],
    "Deep Learning": ["PyTorch", "TensorFlow"],
    "Statistics": ["Pandas", "scikit-learn"],
    "Data Visualization": ["D3.js", "Pandas"],
    "Cloud Computing": ["AWS", "GCP"],
    "Containerization": ["Docker", "Kubernetes"],
    "CI/CD": ["GitHub Actions"],
    "System Design": ["Kubernetes", "AWS"],
    "API Design": ["GraphQL", "FastAPI"],
    "Mobile Development": ["React Native", "SwiftUI"],
    "Cybersecurity": ["Docker"],
    "Data Modeling": ["Neo4j", "PostgreSQL"],
    "Graph Theory": ["Neo4j"],
    "ETL Pipelines": ["Spark", "Kafka"],
    "Distributed Systems": ["Kafka", "Spark", "Kubernetes"],
    "Kotlin": ["React Native"],
}

# Course -> [skills]
COURSE_SKILLS = {
    "Modern JavaScript From Scratch": ["JavaScript"],
    "React — The Complete Guide": ["React", "JavaScript"],
    "TypeScript for Professionals": ["TypeScript"],
    "CSS Grid & Flexbox Mastery": ["CSS"],
    "Python for Everybody": ["Python"],
    "Django for APIs": ["Python", "API Design"],
    "FastAPI — The Complete Course": ["Python", "API Design"],
    "SQL & Database Design": ["SQL", "Data Modeling"],
    "Graph Databases with Neo4j": ["NoSQL", "Graph Theory", "Data Modeling"],
    "Machine Learning Specialization": ["Machine Learning", "Statistics"],
    "Deep Learning Specialization": ["Deep Learning", "Machine Learning"],
    "Practical Statistics for Data Scientists": ["Statistics"],
    "Data Visualization with D3.js": ["Data Visualization"],
    "Docker & Kubernetes — The Practical Guide": ["Containerization", "CI/CD"],
    "AWS Certified Solutions Architect": ["Cloud Computing", "System Design"],
    "CI/CD with GitHub Actions": ["CI/CD"],
    "System Design Primer": ["System Design", "Distributed Systems"],
    "API Design Best Practices": ["API Design"],
    "Mobile Development with React Native": ["Mobile Development", "JavaScript"],
    "iOS Development with SwiftUI": ["Mobile Development"],
    "Web Security Fundamentals": ["Cybersecurity"],
    "Data Engineering with Apache Spark": ["ETL Pipelines", "Distributed Systems"],
    "Building ETL Pipelines": ["ETL Pipelines", "SQL"],
    "Kotlin for Android Developers": ["Kotlin", "Mobile Development"],
    "Graph Theory and Network Science": ["Graph Theory"],
}

# Project -> [skills]
PROJECT_SKILLS = {
    "Personal Portfolio Website": ["JavaScript", "React", "CSS", "HTML"],
    "Real-Time Chat App": ["JavaScript", "API Design", "System Design"],
    "E-Commerce Product Catalog": ["React", "TypeScript", "API Design"],
    "REST API with Authentication": ["Python", "API Design", "SQL"],
    "GraphQL Gateway": ["API Design", "System Design"],
    "Movie Recommendation Engine": ["Python", "Machine Learning", "Statistics"],
    "Image Classifier with CNNs": ["Deep Learning", "Machine Learning", "Python"],
    "Sentiment Analysis API": ["Machine Learning", "Deep Learning", "Python", "API Design"],
    "Interactive Dashboard": ["Data Visualization", "JavaScript"],
    "Dockerized Microservices": ["Containerization", "System Design", "Distributed Systems"],
    "CI/CD Pipeline from Scratch": ["CI/CD", "Cloud Computing"],
    "Cloud Migration Project": ["Cloud Computing", "System Design", "Containerization"],
    "Data Warehouse Pipeline": ["ETL Pipelines", "SQL", "Python"],
    "Streaming Analytics with Kafka": ["ETL Pipelines", "Distributed Systems"],
    "Cross-Platform Mobile App": ["Mobile Development", "JavaScript", "TypeScript"],
    "iOS Weather App": ["Mobile Development"],
    "Security Audit Tool": ["Cybersecurity", "Python"],
    "Knowledge Graph Builder": ["Data Modeling", "Graph Theory", "NoSQL", "Python"],
}

# Project -> [technologies]
PROJECT_TECHNOLOGIES = {
    "Personal Portfolio Website": ["Next.js", "Tailwind CSS", "Vite"],
    "Real-Time Chat App": ["Node.js", "Next.js"],
    "E-Commerce Product Catalog": ["Next.js", "Tailwind CSS"],
    "REST API with Authentication": ["FastAPI", "PostgreSQL"],
    "GraphQL Gateway": ["GraphQL", "Node.js"],
    "Movie Recommendation Engine": ["Pandas", "scikit-learn"],
    "Image Classifier with CNNs": ["PyTorch"],
    "Sentiment Analysis API": ["FastAPI", "PyTorch"],
    "Interactive Dashboard": ["D3.js"],
    "Dockerized Microservices": ["Docker", "Kubernetes"],
    "CI/CD Pipeline from Scratch": ["GitHub Actions", "Docker"],
    "Cloud Migration Project": ["AWS", "Docker"],
    "Data Warehouse Pipeline": ["Spark", "PostgreSQL"],
    "Streaming Analytics with Kafka": ["Kafka", "Spark"],
    "Cross-Platform Mobile App": ["React Native"],
    "iOS Weather App": ["SwiftUI"],
    "Security Audit Tool": ["Docker"],
    "Knowledge Graph Builder": ["Neo4j", "FastAPI"],
}

# Job -> related job (strength 1-10)
JOB_RELATED = {
    "Frontend Developer": [("Full-Stack Developer", 8), ("Mobile Developer", 5)],
    "Backend Developer": [("Full-Stack Developer", 8), ("DevOps Engineer", 6), ("Data Engineer", 5)],
    "Full-Stack Developer": [("Frontend Developer", 8), ("Backend Developer", 8), ("DevOps Engineer", 5)],
    "Data Scientist": [("Machine Learning Engineer", 8), ("Data Engineer", 6)],
    "Machine Learning Engineer": [("Data Scientist", 8), ("Data Engineer", 5)],
    "DevOps Engineer": [("Cloud Solutions Architect", 7), ("Backend Developer", 6), ("Security Engineer", 4)],
    "Cloud Solutions Architect": [("DevOps Engineer", 7), ("Backend Developer", 5)],
    "Data Engineer": [("Data Scientist", 6), ("Backend Developer", 5), ("Machine Learning Engineer", 4)],
    "Mobile Developer": [("Frontend Developer", 5), ("Full-Stack Developer", 4)],
    "Security Engineer": [("DevOps Engineer", 4), ("Backend Developer", 4)],
}

# Skill prerequisites
SKILL_PREREQUISITES = {
    "TypeScript": ["JavaScript"],
    "React": ["JavaScript"],
    "Deep Learning": ["Machine Learning"],
    "Machine Learning": ["Statistics"],
    "ETL Pipelines": ["SQL"],
    "Distributed Systems": ["System Design"],
    "Kotlin": ["Java"],
    "Swift": ["Mobile Development"],
}

# ---------------------------------------------------------------------------
# Cypher (all parameterized)
# ---------------------------------------------------------------------------

CONSTRAINTS = [
    "CREATE CONSTRAINT job_title IF NOT EXISTS FOR (j:Job) REQUIRE j.title IS UNIQUE",
    "CREATE CONSTRAINT skill_name IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE",
    "CREATE CONSTRAINT tech_name IF NOT EXISTS FOR (t:Technology) REQUIRE t.name IS UNIQUE",
    "CREATE CONSTRAINT course_title IF NOT EXISTS FOR (c:Course) REQUIRE c.title IS UNIQUE",
    "CREATE CONSTRAINT project_title IF NOT EXISTS FOR (p:Project) REQUIRE p.title IS UNIQUE",
]

CLEAR = "MATCH (n) DETACH DELETE n"


def _seed(tx, cypher: str, rows: list[dict]):
    for row in rows:
        tx.run(cypher, **row)


def seed(driver: Driver):
    with driver.session() as session:
        for c in CONSTRAINTS:
            session.run(c)
        logger.info("Constraints created.")

        session.run(CLEAR)
        logger.info("Cleared existing data.")

        session.execute_write(_seed, "CREATE (j:Job {title: $title, category: $category, description: $description, avg_salary: $avg_salary})", JOBS)
        logger.info("Loaded %d jobs.", len(JOBS))

        session.execute_write(_seed, "CREATE (s:Skill {name: $name, category: $category, description: $description})", SKILLS)
        logger.info("Loaded %d skills.", len(SKILLS))

        session.execute_write(_seed, "CREATE (t:Technology {name: $name, category: $category, description: $description})", TECHNOLOGIES)
        logger.info("Loaded %d technologies.", len(TECHNOLOGIES))

        session.execute_write(_seed, "CREATE (c:Course {title: $title, provider: $provider, url: $url, level: $level, hours: $hours})", COURSES)
        logger.info("Loaded %d courses.", len(COURSES))

        session.execute_write(_seed, "CREATE (p:Project {title: $title, description: $description, difficulty: $difficulty})", PROJECTS)
        logger.info("Loaded %d projects.", len(PROJECTS))

        # Job -[:REQUIRES]-> Skill
        req = [{"job": j, "skill": s} for j, skills in JOB_SKILLS.items() for s in skills]
        session.execute_write(_seed,
            "MATCH (j:Job {title: $job}), (s:Skill {name: $skill}) CREATE (j)-[:REQUIRES]->(s)", req)
        logger.info("Created %d REQUIRES relationships.", len(req))

        # Skill -[:IMPLEMENTED_WITH]-> Technology
        impl = [{"skill": s, "tech": t} for s, techs in SKILL_TECHNOLOGIES.items() for t in techs]
        session.execute_write(_seed,
            "MATCH (s:Skill {name: $skill}), (t:Technology {name: $tech}) CREATE (s)-[:IMPLEMENTED_WITH]->(t)", impl)
        logger.info("Created %d IMPLEMENTED_WITH relationships.", len(impl))

        # Course -[:TEACHES]-> Skill
        teaches = [{"course": c, "skill": s} for c, skills in COURSE_SKILLS.items() for s in skills]
        session.execute_write(_seed,
            "MATCH (c:Course {title: $course}), (s:Skill {name: $skill}) CREATE (c)-[:TEACHES]->(s)", teaches)
        logger.info("Created %d TEACHES relationships.", len(teaches))

        # Project -[:DEMONSTRATES]-> Skill
        dem = [{"project": p, "skill": s} for p, skills in PROJECT_SKILLS.items() for s in skills]
        session.execute_write(_seed,
            "MATCH (p:Project {title: $project}), (s:Skill {name: $skill}) CREATE (p)-[:DEMONSTRATES]->(s)", dem)
        logger.info("Created %d DEMONSTRATES relationships.", len(dem))

        # Project -[:USES]-> Technology
        uses = [{"project": p, "tech": t} for p, techs in PROJECT_TECHNOLOGIES.items() for t in techs]
        session.execute_write(_seed,
            "MATCH (p:Project {title: $project}), (t:Technology {name: $tech}) CREATE (p)-[:USES]->(t)", uses)
        logger.info("Created %d USES relationships.", len(uses))

        # Job -[:RELATED_TO]-> Job
        rel = [{"from": j, "to": r[0], "strength": r[1]} for j, related in JOB_RELATED.items() for r in related]
        session.execute_write(_seed,
            "MATCH (j1:Job {title: $from}), (j2:Job {title: $to}) CREATE (j1)-[:RELATED_TO {strength: $strength}]->(j2)", rel)
        logger.info("Created %d RELATED_TO relationships.", len(rel))

        # Skill -[:PREREQUISITE_OF]-> Skill
        prereq = [{"from": p, "to": s} for s, prereqs in SKILL_PREREQUISITES.items() for p in prereqs]
        session.execute_write(_seed,
            "MATCH (s1:Skill {name: $from}), (s2:Skill {name: $to}) CREATE (s1)-[:PREREQUISITE_OF]->(s2)", prereq)
        logger.info("Created %d PREREQUISITE_OF relationships.", len(prereq))

    logger.info("Seed complete. Nodes: %d jobs, %d skills, %d techs, %d courses, %d projects.",
                len(JOBS), len(SKILLS), len(TECHNOLOGIES), len(COURSES), len(PROJECTS))


def main():
    if not verify_connectivity():
        logger.error("Cannot connect to CognoDB. Check COGNODB_URI, COGNODB_USERNAME, COGNODB_PASSWORD.")
        return 1
    driver = get_driver()
    seed(driver)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
