import {
  ensureDemoSession,
  isDemoSession,
  saveDemoDashboardSection,
  clearDemoSession
} from './data/demoStore';

const API_BASE = "http://localhost:8000";
const getToken = () => localStorage.getItem("token");

export async function register(email, password, name) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name })
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Erreur d'inscription");
  }
  const data = await res.json();
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("user_id", data.user_id);
  
  // Create a default project automatically upon registration
  const projRes = await createProject("Mon Projet Startup", "agriculture");
  localStorage.setItem("project_id", projRes.id);

  return data;
}

export async function login(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || "Email ou mot de passe incorrect");
  }
  const data = await res.json();
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("user_id", data.user_id);

  try {
    const projsRes = await fetch(`${API_BASE}/projects/`, {
      headers: { 'Authorization': `Bearer ${data.access_token}` }
    });
    if (projsRes.ok) {
      const projects = await projsRes.json();
      if (projects.length > 0) {
        localStorage.setItem("project_id", projects[0].id);
      } else {
        const projRes = await createProject("Mon Projet Startup", "agriculture");
        localStorage.setItem("project_id", projRes.id);
      }
    }
  } catch (err) {
    console.error("Error fetching projects on login", err);
  }

  return data;
}

export async function createProject(project_name, sector) {
  const res = await fetch(`${API_BASE}/projects/`, {
    method: 'POST',
    headers: { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`
    },
    body: JSON.stringify({ project_name, sector })
  });
  if (!res.ok) throw new Error("Failed to create project");
  const data = await res.json();
  return data;
}

export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user_id");
  localStorage.removeItem("project_id");
}

export function isAuthenticated() {
  return !!getToken();
}


export async function saveF1(f1_diagnostic) {
  if (!localStorage.getItem("project_id")) return;
  saveDemoDashboardSection('f1_diagnostic', f1_diagnostic);
}

export async function saveF2(f2_scoring) {
  if (!localStorage.getItem("project_id")) return;
  saveDemoDashboardSection('f2_scoring', f2_scoring);
}

export async function saveF3(f3_roadmap) {
  if (!localStorage.getItem("project_id")) return;
  saveDemoDashboardSection('f3_roadmap', f3_roadmap);
}