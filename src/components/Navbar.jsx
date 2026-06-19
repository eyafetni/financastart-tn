import React, { useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, TrendingUp, ClipboardList, User, LogOut, Languages } from 'lucide-react';
import { translations } from '../data/interfaceTranslations';

import { translateValue } from '../data/dataAdapter';

export default function Navbar({ lang, setLang, startupName, secteur, localisation, isLoggedIn, onLogout }) {
  const t = translations[lang];

  useEffect(() => {
    // Set HTML direction and lang attribute
    document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    document.documentElement.lang = lang;
  }, [lang]);

  return (
    <header className="sticky top-0 z-50 w-full glass-card border-x-0 border-t-0 rounded-none bg-slate-900/80 backdrop-blur-md px-6 py-4">
      <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Title / Logo */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <span className="font-bold text-white text-xl">ب</span>
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
              {isLoggedIn ? startupName : 'بوصلتي'}
              <span className="text-xs bg-slate-800 text-cyan-400 px-2 py-0.5 rounded-full border border-slate-700/50">
                {isLoggedIn ? t.dashboardTitle : (lang === 'fr' ? 'Bawsalati' : 'منصة ريادة الأعمال')}
              </span>
            </h1>
            {isLoggedIn && (
              <p className="text-xs text-slate-400 flex items-center flex-wrap gap-1.5 mt-0.5">
                <span>{t.dashboardSubtitle}</span>
                {secteur && localisation && (
                  <>
                    <span className="text-slate-650">•</span>
                    <span className="text-cyan-400 font-bold bg-cyan-950/60 border border-cyan-500/20 px-2 py-0.5 rounded text-[10px] uppercase tracking-wide">
                      {translateValue(secteur, lang)} ({translateValue(localisation, lang)})
                    </span>
                  </>
                )}
              </p>
            )}
          </div>
        </div>

        {/* Navigation Links (Only visible if logged in) */}
        {isLoggedIn && (
          <nav className="flex items-center gap-2 bg-slate-950/40 p-1 rounded-xl border border-slate-800">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <LayoutDashboard className="h-4 w-4" />
              <span>{t.tabDashboard}</span>
            </NavLink>
            <NavLink
              to="/parcours"
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <TrendingUp className="h-4 w-4" />
              <span>{t.tabMyPath}</span>
            </NavLink>
            <NavLink
              to="/questionnaire"
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <ClipboardList className="h-4 w-4" />
              <span>{lang === 'fr' ? 'Questionnaire' : 'استبيان'}</span>
            </NavLink>
          </nav>
        )}

        {/* Right Section: Auth State & Language Toggler */}
        <div className="flex items-center gap-3">
          {/* Auth Button */}
          {isLoggedIn ? (
            <button
              onClick={onLogout}
              className="flex items-center gap-1.5 px-3 py-1.5 border border-red-500/30 bg-red-950/20 hover:bg-red-950/40 text-red-400 rounded-xl text-xs font-semibold tracking-wide transition-all shadow-md shadow-red-500/5 hover:border-red-500/50 cursor-pointer"
            >
              <LogOut className="h-3.5 w-3.5" />
              <span>{lang === 'fr' ? 'Déconnexion' : 'خروج'}</span>
            </button>
          ) : (
            <NavLink
              to="/login"
              className={({ isActive }) =>
                `flex items-center gap-1.5 px-3 py-1.5 border rounded-xl text-xs font-semibold tracking-wide transition-all ${
                  isActive
                    ? 'bg-cyan-500 text-slate-950 border-cyan-500 shadow-md shadow-cyan-500/10'
                    : 'border-slate-800 text-slate-450 hover:text-slate-250 hover:bg-slate-805/50'
                }`
              }
            >
              <User className="h-3.5 w-3.5" />
              <span>{lang === 'fr' ? 'Connexion' : 'دخول'}</span>
            </NavLink>
          )}

          {/* Language Selector */}
          <div className="flex items-center gap-1 bg-slate-950/50 border border-slate-800 rounded-xl p-0.5">
            <button
              onClick={() => setLang('fr')}
              className={`px-2 py-1 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                lang === 'fr'
                  ? 'bg-slate-800 text-cyan-400 shadow-inner'
                  : 'text-slate-400 hover:text-slate-200 font-normal'
              }`}
            >
              FR
            </button>
            <button
              onClick={() => setLang('ar')}
              className={`px-2 py-1 rounded-lg text-xs font-semibold tracking-wide transition-all ${
                lang === 'ar'
                  ? 'bg-slate-800 text-cyan-400 shadow-inner'
                  : 'text-slate-400 hover:text-slate-200 font-normal'
              }`}
            >
              العربية
            </button>
          </div>
          <div className="text-slate-500 hover:text-slate-400 transition-colors p-1.5 cursor-help" title="Langue / اللغة">
            <Languages className="h-4 w-4" />
          </div>
        </div>
      </div>
    </header>
  );
}
