import React from 'react';
import { Target, TrendingUp, Cpu, BarChart3, Leaf } from 'lucide-react';
import { translations } from '../data/interfaceTranslations';

// ── Color themes ──────────────────────────────────────────────────────────
const colorThemes = {
  cyan: {
    bar:      'bg-cyan-500',
    subBar:   'bg-cyan-400/70',
    text:     'text-cyan-400',
    badge:    'bg-cyan-500/15 text-cyan-300 border-cyan-500/25',
    icon:     'bg-cyan-500/10 border-cyan-500/20',
    divider:  'border-cyan-500/15',
    glow:     'shadow-cyan-500/10',
  },
  indigo: {
    bar:      'bg-indigo-500',
    subBar:   'bg-indigo-400/70',
    text:     'text-indigo-400',
    badge:    'bg-indigo-500/15 text-indigo-300 border-indigo-500/25',
    icon:     'bg-indigo-500/10 border-indigo-500/20',
    divider:  'border-indigo-500/15',
    glow:     'shadow-indigo-500/10',
  },
  violet: {
    bar:      'bg-violet-500',
    subBar:   'bg-violet-400/70',
    text:     'text-violet-400',
    badge:    'bg-violet-500/15 text-violet-300 border-violet-500/25',
    icon:     'bg-violet-500/10 border-violet-500/20',
    divider:  'border-violet-500/15',
    glow:     'shadow-violet-500/10',
  },
  amber: {
    bar:      'bg-amber-500',
    subBar:   'bg-amber-400/70',
    text:     'text-amber-400',
    badge:    'bg-amber-500/15 text-amber-300 border-amber-500/25',
    icon:     'bg-amber-500/10 border-amber-500/20',
    divider:  'border-amber-500/15',
    glow:     'shadow-amber-500/10',
  },
  emerald: {
    bar:      'bg-emerald-500',
    subBar:   'bg-emerald-400/70',
    text:     'text-emerald-400',
    badge:    'bg-emerald-500/15 text-emerald-300 border-emerald-500/25',
    icon:     'bg-emerald-500/10 border-emerald-500/20',
    divider:  'border-emerald-500/15',
    glow:     'shadow-emerald-500/10',
  },
};

const iconMap = {
  market:      Target,
  commercial:  TrendingUp,
  innovation:  Cpu,
  scalability: BarChart3,
  green:       Leaf,
};

// ── Score colour helper ───────────────────────────────────────────────────
function scoreColor(val) {
  if (val >= 70) return 'text-emerald-400';
  if (val >= 45) return 'text-amber-400';
  return 'text-red-400';
}

// ── Single dimension card ─────────────────────────────────────────────────
function DimensionCard({ scoreObj, lang }) {
  const { id, title, score, color, description, justification, subDimensions } = scoreObj;
  const theme = colorThemes[color] || colorThemes.cyan;
  const Icon = iconMap[id] || Target;
  const hasJustif = justification && (justification[lang] || justification.fr);

  return (
    <div
      className={`
        relative rounded-2xl border border-slate-800/60 bg-slate-900/40
        hover:border-slate-700/80 hover:bg-slate-900/60
        transition-all duration-300 overflow-hidden
        shadow-lg ${theme.glow}
      `}
    >
      {/* Subtle left accent bar */}
      <div className={`absolute inset-y-0 start-0 w-0.5 ${theme.bar} rounded-full opacity-60`} />

      <div className="flex flex-col lg:flex-row gap-0">

        {/* ── LEFT: Global score ─────────────────────────────────────── */}
        <div className="flex flex-col gap-4 p-5 lg:w-[42%] border-b lg:border-b-0 lg:border-e border-slate-800/50">

          {/* Icon + title + score badge */}
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className={`h-10 w-10 rounded-xl border flex items-center justify-center shrink-0 ${theme.icon}`}>
                <Icon className={`h-5 w-5 ${theme.text}`} />
              </div>
              <div>
                <h4 className="text-sm font-bold text-white leading-tight">{title[lang]}</h4>
                <p className="text-[10px] text-slate-400 mt-0.5 leading-snug">{description[lang]}</p>
              </div>
            </div>
            {/* Score badge */}
            <span className={`shrink-0 text-xs font-mono font-bold px-2.5 py-1 rounded-lg border ${theme.badge}`}>
              {score}<span className="opacity-60 text-[10px]">/100</span>
            </span>
          </div>

          {/* Main progress bar */}
          <div>
            <div className="flex justify-between text-[10px] text-slate-500 mb-1.5">
              <span>Score global</span>
              <span className={`font-mono font-bold ${scoreColor(score)}`}>{score}%</span>
            </div>
            <div className="h-3 bg-slate-950/60 rounded-full overflow-hidden border border-slate-800/40">
              <div
                className={`h-full ${theme.bar} rounded-full transition-all duration-700 ease-out`}
                style={{ width: `${Math.min(score, 100)}%` }}
              />
            </div>
          </div>

          {/* Justification */}
          {hasJustif && (
            <div className="rounded-xl bg-slate-950/50 border border-slate-800/50 p-3">
              <p className="text-[9px] uppercase tracking-widest text-slate-650 font-bold mb-1">Analyse</p>
              <p className="text-[10px] text-slate-450 leading-relaxed italic">
                {justification[lang] || justification.fr}
              </p>
            </div>
          )}
        </div>

        {/* ── RIGHT: Sub-scores (always visible) ─────────────────────── */}
        <div className="flex flex-col gap-3 p-5 lg:flex-1">

          <p className={`text-[9px] uppercase tracking-widest font-bold ${theme.text} opacity-70`}>
            Sous-dimensions
          </p>

          {subDimensions && subDimensions.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {subDimensions.map((sub, idx) => {
                const subNameFr = sub.name?.fr ?? sub.key;
                const subNameAr = sub.name?.ar ?? sub.key;
                const val = sub.score ?? 0;

                return (
                  <div
                    key={idx}
                    className="flex flex-col gap-1.5 p-3 rounded-xl bg-slate-950/40 border border-slate-800/40 hover:border-slate-700/60 transition-colors"
                  >
                    {/* Label bilingue */}
                    <div className="flex flex-col gap-0.5">
                      <span className="text-[11px] font-semibold text-slate-200 leading-tight">
                        {subNameFr}
                      </span>
                      <span className="text-[10px] text-slate-500 leading-tight font-light" dir="rtl">
                        {subNameAr}
                      </span>
                    </div>

                    {/* Mini-bar + valeur */}
                    <div className="flex items-center gap-2 mt-1">
                      <div className="flex-1 h-1.5 bg-slate-900 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${theme.subBar} rounded-full transition-all duration-500`}
                          style={{ width: `${Math.min(val, 100)}%` }}
                        />
                      </div>
                      <span className={`text-[11px] font-mono font-bold shrink-0 ${scoreColor(val)}`}>
                        {val}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-[11px] text-slate-650 italic">Aucun sous-score disponible.</p>
          )}
        </div>
      </div>
    </div>
  );
}

// ── Main ScoreBars component ──────────────────────────────────────────────
export default function ScoreBars({ scores, lang }) {
  const t = translations[lang];

  return (
    <div className="flex flex-col gap-4">
      {/* Section header */}
      <div>
        <h2 className="text-base font-bold text-white tracking-wide">{t.scoreBarsTitle}</h2>
        <p className="text-xs text-slate-400 mt-0.5">{t.scoreBarsSubtitle}</p>
      </div>

      {/* Dimension cards */}
      <div className="flex flex-col gap-4">
        {scores.map((scoreObj) => (
          <DimensionCard key={scoreObj.id} scoreObj={scoreObj} lang={lang} />
        ))}
      </div>
    </div>
  );
}
