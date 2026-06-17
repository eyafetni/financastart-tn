import React from 'react';
import MaturityIndicator from '../components/MaturityIndicator';
import ScoreBars from '../components/ScoreBars';
import FinancingReadiness from '../components/FinancingReadiness';
import PriorityBlockers from '../components/PriorityBlockers';
import RoadmapTimeline from '../components/RoadmapTimeline';
import { MapPin, Layers } from 'lucide-react';
import { translateValue } from '../data/dataAdapter';

export default function Dashboard({ data, lang }) {
  if (!data) return null;

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 flex flex-col gap-6">

      {/* ── Row 1: Maturity (2/3) + Financing Readiness (1/3) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <MaturityIndicator maturityData={data.maturity} lang={lang} />
        </div>
        <div className="lg:col-span-1">
          <FinancingReadiness readinessData={data.financingReadiness} lang={lang} />
        </div>
      </div>

      {/* ── Row 2: Context card (sector + location) ── */}
      <div className="glass-card p-5 flex flex-wrap items-center gap-6 border-s-4 border-s-slate-500">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-slate-800 flex items-center justify-center">
            <Layers className="h-4 w-4 text-cyan-400" />
          </div>
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">
              {lang === 'fr' ? 'Secteur' : 'القطاع'}
            </p>
            <p className="text-sm font-semibold text-white capitalize">
              {translateValue(data.secteur, lang)}
            </p>
          </div>
        </div>
        <div className="w-px h-8 bg-slate-800 hidden sm:block" />
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-slate-800 flex items-center justify-center">
            <MapPin className="h-4 w-4 text-indigo-400" />
          </div>
          <div>
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">
              {lang === 'fr' ? 'Localisation' : 'الموقع'}
            </p>
            <p className="text-sm font-semibold text-white">
              {translateValue(data.localisation, lang)}
            </p>
          </div>
        </div>
        <div className="ms-auto text-[10px] text-slate-600 font-mono">
          ID: {data.entrepreneur_id}
        </div>
      </div>

      {/* ── Row 3: Scores (left) + Blockers & Roadmap (right) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Score Bars */}
        <div>
          <ScoreBars scores={data.scores} lang={lang} />
        </div>

        {/* Blockers + Roadmap stacked */}
        <div className="flex flex-col gap-6">
          <PriorityBlockers blockers={data.blockers} lang={lang} />
          <RoadmapTimeline roadmapData={data.roadmap} lang={lang} />
        </div>
      </div>
    </main>
  );
}
