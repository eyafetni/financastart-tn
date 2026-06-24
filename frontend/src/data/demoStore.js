import dashboardSeed from './dashboard.json';
import questionnaireSeed from './questionnaire.json';
 
const STORAGE_KEY = 'ains_demo_state';
const DEMO_TOKEN = 'demo-token';
const DEMO_USER_ID = 'demo-user';
const DEMO_PROJECT_ID = 'demo-project';
 
const clone = (value) => JSON.parse(JSON.stringify(value));
 
const defaultState = () => ({
  profile: {
    name: 'Amine Jrad',
    email: 'amine.jrad@gmail.com',
    projectName: 'Amine_Construction',
    sector: dashboardSeed.header?.secteur_label || 'Industrie/Construction'
  },
  dashboard: clone(dashboardSeed),
  questionnaire: clone(questionnaireSeed),
  savedSections: {}
});
 
function readState() {
  if (typeof window === 'undefined' || !window.localStorage) {
    return defaultState();
  }
 
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return defaultState();
    }
 
    const parsed = JSON.parse(raw);
    const state = defaultState();
 
    return {
      ...state,
      ...parsed,
      profile: {
        ...state.profile,
        ...(parsed.profile || {})
      },
      dashboard: {
        ...state.dashboard,
        ...(parsed.dashboard || {}),
        header: {
          ...state.dashboard.header,
          ...((parsed.dashboard || {}).header || {})
        }
      },
      questionnaire: {
        ...state.questionnaire,
        ...(parsed.questionnaire || {})
      },
      savedSections: {
        ...(parsed.savedSections || {})
      }
    };
  } catch {
    return defaultState();
  }
}
 
function writeState(state) {
  if (typeof window === 'undefined' || !window.localStorage) {
    return;
  }
 
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}
 
function persistSession() {
  if (typeof window === 'undefined' || !window.localStorage) {
    return;
  }
 
  window.localStorage.setItem('token', DEMO_TOKEN);
  window.localStorage.setItem('user_id', DEMO_USER_ID);
  window.localStorage.setItem('project_id', DEMO_PROJECT_ID);
  window.localStorage.setItem('demo_mode', 'true');
}
 
function applyProfileToDashboard(state) {
  const sector = state.profile.sector || dashboardSeed.header?.secteur_label || '';
  const projectName = state.profile.projectName || dashboardSeed.header?.nom_entreprise || 'Demo';
 
  state.dashboard.header = {
    ...(state.dashboard.header || {}),
    nom_entreprise: projectName,
    secteur_label: sector
  };
  state.dashboard.entrepreneur_id = DEMO_USER_ID;
  return state;
}
 
export function isDemoSession() {
  if (typeof window === 'undefined' || !window.localStorage) {
    return false;
  }
 
  return window.localStorage.getItem('demo_mode') === 'true'
    || window.localStorage.getItem('token') === DEMO_TOKEN
    || window.localStorage.getItem('project_id') === DEMO_PROJECT_ID;
}
 
export function ensureDemoSession({ name, email, projectName, sector } = {}) {
  const state = readState();
 
  state.profile = {
    ...state.profile,
    name: name || state.profile.name,
    email: email || state.profile.email,
    projectName: projectName || state.profile.projectName,
    sector: sector || state.profile.sector
  };
 
  applyProfileToDashboard(state);
  writeState(state);
  persistSession();
 
  return state;
}
 
export function clearDemoSession() {
  if (typeof window === 'undefined' || !window.localStorage) {
    return;
  }
 
  window.localStorage.removeItem('token');
  window.localStorage.removeItem('user_id');
  window.localStorage.removeItem('project_id');
  window.localStorage.removeItem('demo_mode');
}
 
export function getDemoDashboardData() {
  return clone(applyProfileToDashboard(readState()).dashboard);
}
 
export function getDemoQuestionnaireData() {
  return clone(readState().questionnaire);
}
 
export function saveDemoQuestionnaireData(data) {
  const state = readState();
  state.questionnaire = {
    ...clone(questionnaireSeed),
    ...clone(data)
  };
 
  if (Object.prototype.hasOwnProperty.call(data || {}, 'description')) {
    const now = new Date().toISOString();
    state.dashboard.answers = {
      last_updated: now.split('T')[0],
      free_text: {
        text: data.description || '',
        timestamp: now
      },
      responses: [
        {
          question_id: 'free_text_response',
          type: 'texte',
          answer: data.description || '',
          timestamp: now
        }
      ]
    };
  }
 
  if (Object.prototype.hasOwnProperty.call(data || {}, 'stade_reel')) {
    state.dashboard.stade_reel = data.stade_reel;
  }
 
  if (Object.prototype.hasOwnProperty.call(data || {}, 'stade_percu')) {
    state.dashboard.stade_percu = data.stade_percu;
  }
 
  if (Object.prototype.hasOwnProperty.call(data || {}, 'divergence_explication')) {
    state.dashboard.gap_explication = data.divergence_explication;
  }
 
  if (Object.prototype.hasOwnProperty.call(data || {}, 'answers')) {
    state.dashboard.answers = data.answers;
  }
 
  applyProfileToDashboard(state);
  writeState(state);
  return clone(state.questionnaire);
}
 
export function saveDemoDashboardSection(sectionName, payload) {
  const state = readState();
  state.savedSections = {
    ...(state.savedSections || {}),
    [sectionName]: clone(payload)
  };
  writeState(state);
  return clone(payload);
}
 
export function analyzeDemoProject(payload) {
  const questionnaire = saveDemoQuestionnaireData(payload);
  const dashboard = getDemoDashboardData();
 
  return {
    status: 'success',
    f1_diagnostic: {
      stade_reel: dashboard.stade_reel || questionnaire.stade_reel || 'Structuration',
      stade_percu: dashboard.stade_percu || questionnaire.stade_percu || 'Growth',
      gap_explication: dashboard.gap_explication || questionnaire.divergence_explication || ''
    }
  };
}
 