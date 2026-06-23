import React, { useState, useEffect } from 'react';
import MaturityIndicator from '../components/MaturityIndicator';
import ScoreBars from '../components/ScoreBars';
import FinancingReadiness from '../components/FinancingReadiness';
import AnomaliesList from '../components/AnomaliesList';
import RoadmapTimeline from '../components/RoadmapTimeline';
import ResourcesGrid from '../components/ResourcesGrid';
import AnswersInput from '../components/AnswersInput';
import { MapPin, Layers, Loader2 } from 'lucide-react';
import { getAdaptedData, translateValue } from '../data/dataAdapter';
import { saveF1, saveF2, saveF3 } from '../api';


export default function Dashboard({ lang }) {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/dashboard');
      if (response.ok) {
        const rawJson = await response.json();
        const adapted = getAdaptedData(rawJson);
        setDashboardData(adapted);

        // Sauvegarder F1 (après chargement des données)
        saveF1({
          stage: adapted.maturity?.realStage,
          perceived_stage: adapted.maturity?.perceivedStage,
          perception_gap: adapted.maturity?.realStage !== adapted.maturity?.perceivedStage,
          blockers: adapted.blockers?.map(b => b.title?.fr) ?? [],
          gaps: adapted.maturity?.gapsList ?? []
        });

        // Sauvegarder F2
        saveF2({
          scores: {
            market:      adapted.scores?.find(s => s.id === 'market')?.score,
            offer:       adapted.scores?.find(s => s.id === 'commercial')?.score,
            innovation:  adapted.scores?.find(s => s.id === 'innovation')?.score,
            scalability: adapted.scores?.find(s => s.id === 'scalability')?.score,
            green:       adapted.scores?.find(s => s.id === 'green')?.score,
          },
          global_score: adapted.financingReadiness?.score
        });

        // Sauvegarder F3
        saveF3({
          roadmap: adapted.roadmap
        });
      }
    } catch (e) {
      console.error('Error fetching dashboard data:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleSaveAnswers = async (updatedAnswers) => {
    try {
      const response = await fetch('/api/dashboard', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ answers: updatedAnswers })
      });
      if (response.ok) {
        const resData = await response.json();
        if (resData.success && resData.data) {
          const adapted = getAdaptedData(resData.data);
          setDashboardData(adapted);
          return true;
        }
      }
      return false;
    } catch (e) {
      console.error('Error saving answers:', e);
      return false;
    }
  };

  if (loading) {
    return (
      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-12 flex items-center justify-center">
        <div className="glass-card p-8 text-center flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 text-cyan-400 animate-spin" />
          <p className="text-slate-400 text-sm font-semibold">
            {lang === 'fr' ? 'Chargement du tableau de bord...' : 'جاري تحميل لوحة التحكم...'}
          </p>
        </div>
      </main>
    );
  }

  if (!dashboardData) return null;

  return (
    <main
      className="max-w-7xl mx-auto px-4 sm:px-6 py-8 flex flex-col gap-6"
      dir={lang === 'ar' ? 'rtl' : 'ltr'}
    >

      {/* ── Row 1: Maturity (2/3) + Financing Readiness (1/3) ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <MaturityIndicator maturityData={dashboardData.maturity} lang={lang} />
        </div>
        <div className="lg:col-span-1">
          <FinancingReadiness readinessData={dashboardData.financingReadiness} lang={lang} />
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
            <p className="text-sm font-semibold text-white">
              {translateValue(dashboardData.secteur, lang)}
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
              {translateValue(dashboardData.localisation, lang)}
            </p>
          </div>
        </div>
        <div className="ms-auto text-[10px] text-slate-655 font-mono">
          ID: {dashboardData.entrepreneur_id}
        </div>
      </div>

      {/* ── Row 3: Scores — pleine largeur ── */}
      <div>
        <ScoreBars scores={dashboardData.scores} lang={lang} />
      </div>

      {/* ── Row 4: Anomalies — full width compact cards ── */}
      <div>
        <AnomaliesList anomalies={dashboardData.anomalies} lang={lang} />
      </div>

      {/* ── Row 5: Roadmap — full width ── */}
      <div>
        <RoadmapTimeline roadmapData={dashboardData.roadmap} lang={lang} />
      </div>

      {/* ── Row 6: Resources — pleine largeur ── */}
      <div>
        <ResourcesGrid resources={dashboardData.resources} lang={lang} />
      </div>

      {/* ── Row 7: Answers Input — pleine largeur ── */}
      <div>
        <AnswersInput
          answers={dashboardData.answers}
          onSaveAnswers={handleSaveAnswers}
          lang={lang}
        />
      </div>
    </main>
  );
}
