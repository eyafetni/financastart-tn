import React, { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './views/Dashboard';
import MyPath from './views/MyPath';
import Questionnaire from './views/Questionnaire';
import { getAdaptedData } from './data/dataAdapter';

export default function App() {
  const [lang, setLang] = useState('fr');
  
  // Get adapted data from dashboard.json
  const adaptedData = getAdaptedData();

  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col pb-12">
        <Navbar 
          lang={lang} 
          setLang={setLang} 
          startupName={adaptedData.startupName}
          secteur={adaptedData.secteur}
          localisation={adaptedData.localisation}
        />

        <Routes>
          <Route 
            path="/" 
            element={<Dashboard data={adaptedData} lang={lang} />} 
          />
          <Route 
            path="/parcours" 
            element={<MyPath lang={lang} />} 
          />
          <Route 
            path="/questionnaire" 
            element={<Questionnaire lang={lang} />} 
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
