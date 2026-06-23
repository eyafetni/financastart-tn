import React from 'react';
import { CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';
import { translations } from '../data/interfaceTranslations';

import { translateValue } from '../data/dataAdapter';

export default function MaturityIndicator({ maturityData, lang }) {
  const t = translations[lang];
  const { perceivedStage, realStage, stages, alertMessage, gapsList } = maturityData;

  // Find indexes
  const realIndex = stages.findIndex(s => s.id === realStage);
  const perceivedIndex = stages.findIndex(s => s.id === perceivedStage);
  const hasMismatch = realStage !== perceivedStage;

  return (
    <div className="glass-card p-6 flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide">{t.maturityTitle}</h2>
          <p className="text-xs text-slate-400">
            {t.maturityReal}: <span className="text-cyan-400 font-semibold">{stages[realIndex]?.label[lang]}</span>
            {hasMismatch && (
              <span className="mx-2 text-amber-500">
                ({t.maturityPerceived}: {stages[perceivedIndex]?.label[lang]})
              </span>
            )}
          </p>
        </div>
        <div className="h-9 w-9 rounded-lg bg-slate-800 flex items-center justify-center text-slate-400">
          <CheckCircle2 className="h-5 w-5 text-cyan-400" />
        </div>
      </div>

      {/* Mismatch Alert Box */}
      {hasMismatch && (
        <div className="flex gap-4 p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-sm animate-pulse-slow">
          <div className="flex-shrink-0 mt-0.5">
            <AlertTriangle className="h-5 w-5 text-amber-400" />
          </div>
          <div className="w-full">
            <h4 className="font-bold text-amber-400 mb-1">{t.maturityAlertTitle}</h4>
            <p className="text-xs leading-relaxed text-amber-200/90">{alertMessage[lang]}</p>
            {gapsList && gapsList.length > 0 && (
              <ul className="list-disc list-inside mt-3 space-y-1 text-[11px] text-amber-300/80 border-t border-amber-500/15 pt-2">
                {gapsList.map((gap, gIdx) => (
                  <li key={gIdx} className="font-medium">
                    {translateValue(gap, lang)}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      {/* 6-Stage Timeline Visualizer */}
      <div className="relative py-8 px-2">
        {/* Connection Background Line */}
        <div className="absolute top-1/2 left-4 right-4 h-1 bg-slate-800 -translate-y-1/2 rounded-full z-0" />
        
        {/* Progress Fill Line */}
        <div 
          className="absolute top-1/2 left-4 h-1 bg-gradient-to-r from-cyan-500 to-cyan-400 -translate-y-1/2 rounded-full transition-all duration-500 z-0"
          style={{
            width: `${(realIndex / (stages.length - 1)) * 94}%`,
            right: lang === 'ar' ? 'auto' : undefined,
            left: lang === 'ar' ? undefined : '16px',
            transformOrigin: lang === 'ar' ? 'right' : 'left'
          }}
        />

        {/* Timeline Nodes */}
        <div className="relative flex justify-between items-center z-10">
          {stages.map((stage, idx) => {
            const isReal = stage.id === realStage;
            const isPerceived = stage.id === perceivedStage;
            const isCompleted = idx < realIndex;

            let nodeClass = "bg-slate-900 border-slate-700 text-slate-400";
            let iconElement = <span className="text-xs font-bold">{idx + 1}</span>;

            if (isCompleted) {
              nodeClass = "bg-cyan-500 border-cyan-400 text-slate-955 scale-110 shadow-lg shadow-cyan-500/20";
              iconElement = <CheckCircle2 className="h-4 w-4 stroke-[3]" />;
            } else if (isReal) {
              nodeClass = "bg-slate-900 border-cyan-400 text-cyan-400 scale-125 pulse-active border-2";
              iconElement = <span className="text-xs font-bold font-mono">{idx + 1}</span>;
            } else if (isPerceived && hasMismatch) {
              nodeClass = "bg-slate-900 border-amber-500 text-amber-500 scale-125 border-2 border-dashed";
              iconElement = <HelpCircle className="h-4 w-4" />;
            }

            return (
              <div key={stage.id} className="flex flex-col items-center group relative">
                {/* Node bubble */}
                <div className={`w-8 h-8 rounded-full flex items-center justify-center border transition-all duration-300 ${nodeClass}`}>
                  {iconElement}
                </div>

                {/* Node text label below */}
                <div className="absolute top-10 flex flex-col items-center w-28 text-center pointer-events-none">
                  <span className={`text-[11px] font-semibold tracking-tight transition-colors duration-200 ${
                    isReal ? 'text-cyan-400 font-bold' : isPerceived && hasMismatch ? 'text-amber-500 font-bold' : 'text-slate-400'
                  }`}>
                    {stage.label[lang]}
                  </span>
                  
                  {/* Small tag markers */}
                  {isReal && (
                    <span className="text-[8px] uppercase tracking-wider bg-cyan-950 text-cyan-400 px-1 rounded-sm mt-0.5 font-bold border border-cyan-500/20">
                      {t.maturityReal}
                    </span>
                  )}
                  {isPerceived && hasMismatch && (
                    <span className="text-[8px] uppercase tracking-wider bg-amber-955 text-amber-500 px-1 rounded-sm mt-0.5 font-bold border border-amber-500/20">
                      {t.maturityPerceived}
                    </span>
                  )}
                </div>

                {/* Hover Stage Detail Card */}
                <div className="absolute bottom-11 scale-90 opacity-0 group-hover:scale-100 group-hover:opacity-100 pointer-events-none transition-all duration-200 z-50 w-52 bg-slate-950 border border-slate-800 p-3 rounded-xl shadow-2xl text-left rtl:text-right">
                  <h5 className="text-xs font-bold text-cyan-400 border-b border-slate-800 pb-1 mb-1">
                    {stage.label[lang]}
                  </h5>
                  <p className="text-[10px] leading-relaxed text-slate-300">
                    {stage.desc[lang]}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
      <div className="h-6" /> {/* Spacer for labels */}
    </div>
  );
}
