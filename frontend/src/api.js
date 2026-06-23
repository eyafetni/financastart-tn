const BASE_URL = "http://localhost:8000";
const getToken = () => localStorage.getItem("token");

export async function register(email, password, name) {
  const res = await fetch(`${BASE_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, name })
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Erreur lors de l'inscription");
  }
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("user_id", data.user_id);
  return data;
}

export async function login(email, password) {
  const res = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Email ou mot de passe incorrect");
  }
  localStorage.setItem("token", data.access_token);
  localStorage.setItem("user_id", data.user_id);
  localStorage.setItem("project_id", data.project_id || "");
  return data;
}

export async function createProject(project_name, sector) {
  const res = await fetch(`${BASE_URL}/projects/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${getToken()}`
    },
    body: JSON.stringify({ project_name, sector })
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || "Erreur lors de la création du projet");
  }
  localStorage.setItem("project_id", data.id);
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
  const projectId = localStorage.getItem("project_id");
  if (!projectId) return;
  await fetch(`${BASE_URL}/projects/${projectId}/f1`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${getToken()}`
    },
    body: JSON.stringify({ f1_diagnostic })
  });
}

export async function saveF2(f2_scoring) {
  const projectId = localStorage.getItem("project_id");
  if (!projectId) return;
  await fetch(`${BASE_URL}/projects/${projectId}/f2`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${getToken()}`
    },
    body: JSON.stringify({ f2_scoring })
  });
}

export async function saveF3(f3_roadmap) {
  const projectId = localStorage.getItem("project_id");
  if (!projectId) return;
  await fetch(`${BASE_URL}/projects/${projectId}/f3`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${getToken()}`
    },
    body: JSON.stringify({ f3_roadmap })
  });
}