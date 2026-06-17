import React, { useState } from 'react';
import { Target, TrendingUp, Cpu, BarChart3, Leaf, ChevronRight } from 'lucide-react';
import { translations } from '../data/interfaceTranslations';

// Color map for Tailwind classes based on JSON color key
const colorThemes = {
  cyan: {
    bg: 'bg-cyan-500',
    text: 'text-cyan-400',
    border: 'border-cyan-500/20',
    lightBg: 'bg-cyan-500/10',
    shadow: 'shadow-cyan-500/20',
    hoverBorder: 'group-hover:border-cyan-400/50'
  },
  indigo: {
    bg: 'bg-indigo-500',
    text: 'text-indigo-400',
    border: 'border-indigo-500/20',
    lightBg: 'bg-indigo-500/10',
    shadow: 'shadow-indigo-500/20',
    hoverBorder: 'group-hover:border-indigo-400/50'
  },
  violet: {
    bg: 'bg-violet-500',
    text: 'text-violet-400',
    border: 'border-violet-500/20',
    lightBg: 'bg-violet-500/10',
    shadow: 'shadow-violet-500/20',
    hoverBorder: 'group-hover:border-violet-400/50'
  },
  amber: {
    bg: 'bg-amber-500',
    text: 'text-amber-400',
    border: 'border-amber-500/20',
    lightBg: 'bg-amber-500/10',
    shadow: 'shadow-amber-500/20',
    hoverBorder: 'group-hover:border-amber-400/50'
  },
  emerald: {
    bg: 'bg-emerald-500',
    text: 'text-emerald-400',
    border: 'border-emerald-500/20',
    lightBg: 'bg-emerald-500/10',
    shadow: 'shadow-emerald-500/20',
    hoverBorder: 'group-hover:border-emerald-400/50'
  }
};

const iconMap = {
  market: Target,
  commercial: TrendingUp,
  innovation: Cpu,
  scalability: BarChart3,
  green: Leaf
};

export default function ScoreBars({ scores, lang }) {
  const t = translations[lang];
  const [activeMobileId, setActiveMobileId] = useState(null);

  const toggleMobileDetails = (id) => {
    setActiveMobileId(activeMobileId === id ? null : id);
  };

  return (
    <div className="glass-card p-6 flex flex-col gap-6 h-full">
      {/* Header */}
      <div>
        <h2 className="text-lg font-bold text-white tracking-wide">{t.scoreBarsTitle}</h2>
        <p className="text-xs text-slate-400 mt-1">{t.scoreBarsSubtitle}</p>
      </div>

      {/* Scores List */}
      <div className="flex flex-col gap-5">
        {scores.map((scoreObj) => {
          const { id, title, score, color, description, subDimensions } = scoreObj;
          const theme = colorThemes[color] || colorThemes.cyan;
          const Icon = iconMap[id] || Target;

          return (
            <div key={id} className="relative group">
              {/* Desktop Tooltip Hover Container */}
              <div 
                onClick={() => toggleMobileDetails(id)}
                className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl bg-slate-950/35 border border-slate-800 hover:bg-slate-900/40 transition-all duration-300 cursor-pointer select-none tooltip-trigger"
              >
                {/* Left block: Icon and Label */}
                <div className="flex items-center gap-3 w-full md:w-1/4">
                  <div className={`h-10 w-10 rounded-xl ${theme.lightBg} border ${theme.border} flex items-center justify-center`}>
                    <Icon className={`h-5 w-5 ${theme.text}`} />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white group-hover:text-cyan-300 transition-colors">
                      {title[lang]}
                    </h4>
                    <span className="text-[10px] text-slate-400 font-medium block leading-tight">
                      {description[lang]}
                    </span>
                  </div>
                </div>

                {/* Middle block: Progress Bar */}
                <div className="flex-1 w-full md:px-4">
                  <div className="h-3 bg-slate-800 rounded-full overflow-hidden border border-slate-700/30">
                    <div 
                      className={`h-full ${theme.bg} rounded-full transition-all duration-700 ease-out`}
                      style={{ width: `${score}%` }}
                    />
                  </div>
                </div>

                {/* Right block: Percentage and chevron */}
                <div className="flex items-center justify-between md:justify-end gap-3 md:w-20">
                  <span className={`text-lg font-bold font-mono ${theme.text}`}>
                    {score}%
                  </span>
                  <ChevronRight className={`h-4 w-4 text-slate-500 group-hover:text-slate-300 transition-transform md:rotate-0 rotate-90 ${activeMobileId === id ? 'rotate-180 md:rotate-180' : ''}`} />
                </div>
              </div>

              {/* Tooltip Content Overlay - Standard Hover on Desktop & Click on Mobile */}
              <div className={`
                md:absolute md:top-0 md:end-full md:me-4 md:w-96 w-full z-50
                glass-card bg-slate-950/95 border border-slate-700/80 p-5 shadow-2xl rounded-2xl
                transition-all duration-300 pointer-events-none md:opacity-0 md:translate-y-2 md:group-hover:opacity-100 md:group-hover:translate-y-0 md:group-hover:pointer-events-auto
                ${activeMobileId === id ? 'block mt-2 pointer-events-auto opacity-100 translate-y-0' : 'hidden md:block'}
              `}>
                <div className="flex items-center gap-2 border-b border-slate-800 pb-2 mb-3">
                  <div className={`h-6 w-6 rounded-md ${theme.lightBg} flex items-center justify-center`}>
                    <Icon className={`h-3.5 w-3.5 ${theme.text}`} />
                  </div>
                  <h5 className="text-xs font-bold text-white uppercase tracking-wider">
                    {title[lang]} - {t.subDimensionsTitle}
                  </h5>
                </div>

                <div className="flex flex-col gap-4">
                  {subDimensions.map((sub, sIdx) => (
                    <div key={sIdx} className="flex flex-col gap-1 border-b border-slate-900/60 pb-2 last:border-0 last:pb-0">
                      <div className="flex items-center justify-between text-[11px] font-semibold">
                        <span className="text-slate-200">{sub.name[lang]}</span>
                        <span className={`${theme.text} font-mono font-bold`}>{sub.score}/100</span>
                      </div>
                      
                      {/* Sub-bar */}
                      <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${theme.bg} rounded-full`}
                          style={{ width: `${sub.score}%` }}
                        />
                      </div>

                      {/* Justification text */}
                      <div className="text-[10px] text-slate-400 bg-slate-900/40 p-2 rounded-lg border border-slate-800/60 mt-1 italic leading-relaxed">
                        <strong className="text-[9px] uppercase tracking-wide not-italic text-slate-500 block mb-0.5">
                          {t.justificationTitle}
                        </strong>
                        "{sub.justification[lang]}"
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
