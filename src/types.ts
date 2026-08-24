export interface Job { title: string; category: string; description: string; avg_salary: number }
export interface Skill { name: string; category: string; description: string }
export interface Technology { name: string; category: string; description: string }
export interface Course { title: string; provider: string; url: string; level: string; hours: number }
export interface Project { title: string; description: string; difficulty: string }
export interface RelatedJob { title: string; category: string; shared_skills: string[]; relation: string }
export interface SkillGapResult { target_job: string; have_skills: string[]; missing_skills: string[]; matching_skills: string[]; coverage_pct: number; recommended_courses: Course[]; recommended_projects: Project[] }
export interface ConnectionNode { id: string; label: string; type: string; properties: Record<string, unknown> }
export interface ConnectionEdge { source: string; target: string; type: string }
export interface ConnectionGraph { nodes: ConnectionNode[]; edges: ConnectionEdge[] }
