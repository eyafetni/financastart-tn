import React from 'react';
import { AlertCircle, AlertTriangle, Info, ShieldAlert } from 'lucide-react';
import { translations } from '../data/interfaceTranslations';

const priorityColors = {
  high: {
    border: 'border-s-4 border-s-rose-500 border-e-0',
    borderRtl: 'border-s-0 border-e-4 border-e-rose-500',
    bg: 'bg-rose-950/20 hover:bg-rose-950/30',
    text: 'text-rose-400',
    badge: 'bg-rose-950/60 text-rose-400 border border-rose-500/30',
    icon: AlertCircle
  },
  medium: {
    border: 'border-s-4 border-s-amber-500 border-e-0',
    borderRtl: 'border-s-0 border-e-4 border-e-amber-500',
    bg: 'bg-amber-950/20 hover:bg-amber-950/30',
    text: 'text-amber-400',
    badge: 'bg-amber-950/60 text-amber-400 border border-amber-500/30',
    icon: AlertTriangle
  },
  low: {
    border: 'border-s-4 border-s-yellow-400 border-e-0',
    borderRtl: 'border-s-0 border-e-4 border-e-yellow-400',
    bg: 'bg-yellow-950/10 hover:bg-yellow-950/20',
    text: 'text-yellow-400',
    badge: 'bg-yellow-950/40 text-yellow-400 border border-yellow-400/20',
    icon: Info
  }
};

export default function PriorityBlockers({ blockers, lang }) {
  const t = translations[lang];

  return (
    <div className="glass-card p-6 flex flex-col gap-5 h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide">{t.blockersTitle}</h2>
          <p className="text-xs text-slate-400">{t.blockersSubtitle}</p>
        </div>
        <div className="h-9 w-9 rounded-lg bg-slate-800 flex items-center justify-center">
          <ShieldAlert className="h-5 w-5 text-rose-500" />
        </div>
      </div>

      {/* Blockers list */}
      <div className="flex flex-col gap-3 max-h-[360px] overflow-y-auto pr-1">
        {blockers.map((blocker) => {
          const { id, domain, priority, title, desc } = blocker;
          const styles = priorityColors[priority] || priorityColors.medium;
          const Icon = styles.icon;

          // Determine border side depending on RTL direction
          const borderClass = lang === 'ar' ? styles.borderRtl : styles.border;

          return (
            <div
              key={id}
              className={`p-4 rounded-xl border border-slate-850/80 transition-all duration-300 ${styles.bg} ${borderClass}`}
            >
              {/* Top Row: Domain badge & Priority label */}
              <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] uppercase font-bold tracking-wider bg-slate-800 text-slate-300 px-2.5 py-0.5 rounded-full border border-slate-700/50">
                  {domain[lang]}
                </span>
                
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md flex items-center gap-1 ${styles.badge}`}>
                  <Icon className="h-3 w-3" />
                  {priority === 'high' ? t.priorityHigh : priority === 'medium' ? t.priorityMedium : t.priorityLow}
                </span>
              </div>

              {/* Title & Description */}
              <h4 className="text-sm font-bold text-white mb-1">
                {title[lang]}
              </h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                {desc[lang]}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
