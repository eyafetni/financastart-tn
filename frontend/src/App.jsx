import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './views/Dashboard';
import MyPath from './views/MyPath';
import Questionnaire from './views/Questionnaire';
import LoginView from './views/LoginView';
import SignUpView from './views/SignUpView';
import { getAdaptedData } from './data/dataAdapter';

// Check if user has an active token in localStorage
export const isAuthenticated = () => {
  return !!localStorage.getItem('token');
};

export default function App() {
  const [lang, setLang] = useState('fr');
  const [isLoggedIn, setIsLoggedIn] = useState(isAuthenticated());

  const [projectData, setProjectData] = useState(null);

  React.useEffect(() => {
    if (isLoggedIn) {
      const projectId = localStorage.getItem('project_id') || 1;
      const token = localStorage.getItem('token');
      if (token) {
        fetch(`http://localhost:8000/projects/${projectId}/dashboard`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(res => {
          if (res.ok) return res.json();
          throw new Error('Failed to fetch');
        })
        .then(data => {
          const adapted = getAdaptedData(data);
          setProjectData(adapted);
        })
        .catch(console.error);
      }
    } else {
      setProjectData(null);
    }
  }, [isLoggedIn]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('project_id');
    setIsLoggedIn(false);
  };

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
  };

  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col pb-12">
        <Navbar
          lang={lang}
          setLang={setLang}
          startupName={projectData?.startupName || ''}
          secteur={projectData?.secteur || ''}
          localisation={projectData?.localisation || ''}
          isLoggedIn={isLoggedIn}
          onLogout={handleLogout}
        />

        <Routes>
          {/* Protected Routes: Accessible only if logged in */}
          <Route
            path="/"
            element={isLoggedIn ? <Dashboard lang={lang} /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/parcours"
            element={isLoggedIn ? <MyPath lang={lang} /> : <Navigate to="/login" replace />}
          />
          <Route
            path="/questionnaire"
            element={isLoggedIn ? <Questionnaire lang={lang} /> : <Navigate to="/login" replace />}
          />

          {/* Public / Guest Routes: Accessible only if NOT logged in */}
          <Route
            path="/login"
            element={!isLoggedIn ? <LoginView lang={lang} onLoginSuccess={handleLoginSuccess} /> : <Navigate to="/" replace />}
          />
          <Route
            path="/signup"
            element={!isLoggedIn ? <SignUpView lang={lang} /> : <Navigate to="/" replace />}
          />

          {/* Catch-all: redirect based on login status */}
          <Route
            path="*"
            element={<Navigate to={isLoggedIn ? "/" : "/login"} replace />}
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

