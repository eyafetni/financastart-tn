import React from 'react';
import { Calendar, CheckCircle2, Circle, Clock } from 'lucide-react';
import { translations } from '../data/interfaceTranslations';

export default function RoadmapTimeline({ roadmapData, lang }) {
  const t = translations[lang];

  return (
    <div className="glass-card p-6 flex flex-col gap-6 h-full">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide">{t.roadmapTitle}</h2>
          <p className="text-xs text-slate-400">{t.roadmapSubtitle}</p>
        </div>
        <div className="h-9 w-9 rounded-lg bg-slate-800 flex items-center justify-center">
          <Calendar className="h-5 w-5 text-indigo-400" />
        </div>
      </div>

      {/* Timeline List */}
      <div className="relative border-s border-slate-850 ms-3 rtl:border-s-0 rtl:border-e rtl:border-slate-850 rtl:ms-0 rtl:me-3 pl-6 rtl:pl-0 rtl:pr-6 flex flex-col gap-6">
        {roadmapData.map((horizonObj, idx) => {
          const { horizon, title, actions } = horizonObj;

          return (
            <div key={horizon} className="relative group">
              {/* Timeline Bullet node */}
              <span className="absolute -start-[31px] rtl:-start-auto rtl:-end-[31px] top-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-slate-900 border border-indigo-500 shadow-md group-hover:scale-110 transition-transform">
                <span className="h-1.5 w-1.5 rounded-full bg-indigo-400" />
              </span>

              {/* Horizon Header */}
              <div className="flex items-center gap-2 mb-3">
                <Clock className="h-3.5 w-3.5 text-indigo-400" />
                <h4 className="text-xs uppercase font-extrabold tracking-wider text-indigo-300">
                  {title[lang]}
                </h4>
              </div>

              {/* Actions Box */}
              <div className="grid grid-cols-1 gap-2.5">
                {actions.map((action, aIdx) => (
                  <div
                    key={aIdx}
                    className={`flex items-start gap-3 p-3 rounded-xl border transition-all duration-300 ${
                      action.completed
                        ? 'bg-emerald-950/10 border-emerald-500/20 text-slate-300 hover:border-emerald-500/40'
                        : 'bg-slate-950/20 border-slate-800/80 text-slate-300 hover:border-slate-700/60'
                    }`}
                  >
                    {/* Status Circle Check */}
                    <div className="flex-shrink-0 mt-0.5">
                      {action.completed ? (
                        <CheckCircle2 className="h-4.5 w-4.5 text-emerald-400 stroke-[2.5]" />
                      ) : (
                        <Circle className="h-4.5 w-4.5 text-slate-500 stroke-[2]" />
                      )}
                    </div>

                    {/* Action Text */}
                    <span className={`text-xs leading-normal ${action.completed ? 'line-through text-slate-500' : ''}`}>
                      {action.text[lang]}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
