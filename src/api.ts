import type { Course, ConnectionGraph, Job, Project, RelatedJob, Skill, SkillGapResult, Technology } from '@/types';

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { headers: { 'Content-Type': 'application/json' }, ...init });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: 'The API could not complete this request.' }));
    throw new Error(body.detail ?? 'The API could not complete this request.');
  }
  return response.json() as Promise<T>;
}

export const api = {
  jobs: () => request<Job[]>('/jobs'),
  job: (title: string) => request<Job>(`/jobs/${encodeURIComponent(title)}`),
  skills: (title: string) => request<Skill[]>(`/jobs/${encodeURIComponent(title)}/skills`),
  technologies: (title: string) => request<Technology[]>(`/jobs/${encodeURIComponent(title)}/technologies`),
  courses: (title: string) => request<Course[]>(`/jobs/${encodeURIComponent(title)}/courses`),
  projects: (title: string) => request<Project[]>(`/jobs/${encodeURIComponent(title)}/projects`),
  related: (title: string) => request<RelatedJob[]>(`/jobs/${encodeURIComponent(title)}/related`),
  allSkills: () => request<Skill[]>('/skills'),
  gap: (targetJob: string, haveSkills: string[]) => request<SkillGapResult>('/skill-gap', { method: 'POST', body: JSON.stringify({ target_job: targetJob, have_skills: haveSkills }) }),
  connections: (title: string) => request<ConnectionGraph>(`/connections/${encodeURIComponent(title)}`),
};
