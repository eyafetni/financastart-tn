import React from 'react';
import { ShieldAlert, AlertTriangle, ArrowRight } from 'lucide-react';
import { translations } from '../data/interfaceTranslations';

export default function AnomaliesList({ anomalies, lang }) {
  const t = translations[lang];

  if (!anomalies || anomalies.length === 0) {
    return null;
  }

  return (
    <div className="flex flex-col gap-3">
      {/* Section Header — compact, not wrapped in a giant card */}
      <div className="flex items-center gap-3 px-1">
        <div className="h-8 w-8 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0">
          <ShieldAlert className="h-4 w-4 text-rose-500" />
        </div>
        <div>
          <h2 className="text-sm font-bold text-white tracking-wide">{t.anomaliesTitle}</h2>
          <p className="text-[11px] text-slate-400">{t.anomaliesSubtitle}</p>
        </div>
        <span className="ms-auto text-[10px] font-mono bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded-full">
          {anomalies.length} {lang === 'ar' ? 'شذوذات' : 'anomalies'}
        </span>
      </div>

      {/* Cards grid — 2 columns on large screens */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {anomalies.map((anomaly) => {
          const { id, dimension, penalty, justification, action, kbLink } = anomaly;

          return (
            <div
              key={id}
              className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800/60 border-s-4 border-s-rose-500 hover:bg-slate-900 hover:border-slate-700/80 transition-all duration-200 flex flex-col gap-2.5"
            >
              {/* Top Row: Dimension & Penalty badges */}
              <div className="flex items-center justify-between gap-2 flex-wrap">
                <span className="text-[9px] uppercase font-extrabold tracking-wider bg-slate-950 text-rose-400 border border-rose-500/20 px-2 py-0.5 rounded-full whitespace-nowrap">
                  {dimension.replace('_score', '')}
                </span>
                <span className="text-[9px] font-mono font-bold bg-rose-500/15 text-rose-300 border border-rose-500/25 px-1.5 py-0.5 rounded flex items-center gap-0.5 flex-shrink-0">
                  <AlertTriangle className="h-2.5 w-2.5" />
                  -{penalty} pts
                </span>
              </div>

              {/* Justification */}
              <p className="text-[11px] text-slate-300 leading-relaxed">
                {justification[lang] || justification.fr}
              </p>

              {/* Action */}
              <div className="bg-slate-950/50 border border-slate-800/50 p-2.5 rounded-lg">
                <p className="text-[9px] uppercase tracking-widest text-rose-500/70 font-bold flex items-center gap-1 mb-1">
                  <ArrowRight className="h-2.5 w-2.5 rtl:rotate-180" />
                  {t.recommendedAction}
                </p>
                <p className="text-[11px] text-slate-200">
                  {action[lang] || action.fr}
                </p>
              </div>

              {/* KB link — subtle */}
              {kbLink && (
                <p className="text-[9px] font-mono text-slate-600 hover:text-slate-400 cursor-help truncate" title={`${t.kbLink}: ${kbLink}`}>
                  {kbLink}
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
