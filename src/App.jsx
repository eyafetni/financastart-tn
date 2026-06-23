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
  return !!localStorage.getItem('auth_token');
};

export default function App() {
  const [lang, setLang] = useState('fr');
  const [isLoggedIn, setIsLoggedIn] = useState(isAuthenticated());
  
  // Get adapted data from dashboard.json
  const adaptedData = getAdaptedData();

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
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
          startupName={adaptedData.startupName}
          secteur={adaptedData.secteur}
          localisation={adaptedData.localisation}
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

