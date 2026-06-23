import { useState, useEffect } from 'react';
import {
  Calendar, TrendingUp, TrendingDown, Minus,
  ChevronDown, ChevronUp, X, CheckCircle,
  ShieldAlert, AlertTriangle, ArrowUpRight, History, Star, MessageCircle
} from 'lucide-react';
import { translations } from '../data/interfaceTranslations';
import { loadQuestionnaire, allQuestions } from '../data/questionnaireService';
import { sessionHistory, scoreKeys, scoreLabels, scoreColors } from '../data/sessionHistory';
import ScoreHistoryChart from '../components/ScoreHistoryChart';

// ── helpers ──────────────────────────────────────────────────────────────────
const stageLabels = {
  fr: {
    Ideation: 'Idéation', Validation: 'Validation', Structuration: 'Structuration',
    Fundraising: 'Levée de fonds', Launch: 'Lancement', Growth: 'Croissance',
  },
  ar: {
    Ideation: 'فكرة', Validation: 'تحقق', Structuration: 'هيكلة',
    Fundraising: 'جمع التمويل', Launch: 'إطلاق', Growth: 'نمو',
  },
};

function ScoreTrend({ current, previous }) {
  if (previous === undefined) return <Minus className="h-3 w-3 text-slate-500" />;
  const diff = current - previous;
  if (diff > 0) return (
    <span className="flex items-center gap-0.5 text-emerald-400 text-[10px] font-bold">
      <TrendingUp className="h-3 w-3" />+{diff}
    </span>
  );
  if (diff < 0) return (
    <span className="flex items-center gap-0.5 text-rose-400 text-[10px] font-bold">
      <TrendingDown className="h-3 w-3" />{diff}
    </span>
  );
  return <Minus className="h-3 w-3 text-slate-500" />;
}

// ── Session Detail Modal ─────────────────────────────────────────────────────
function SessionModal({ session, lang, onClose, prevSession }) {
  const t = translations[lang];
  const isBankable = session.status === 'bankable';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="glass-card w-full max-w-lg p-6 flex flex-col gap-5 shadow-2xl border-slate-700/60 relative">
        {/* Close */}
        <button
          onClick={onClose}
          className="absolute top-4 end-4 h-8 w-8 rounded-lg bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-400 hover:text-white transition-all"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Title */}
        <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
          <div className="h-10 w-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center">
            <Calendar className="h-5 w-5 text-indigo-400" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">
              {lang === 'fr' ? `Session du ${session.date}` : `جلسة ${session.date}`}
            </h3>
            <p className="text-xs text-slate-400">
              {lang === 'fr'
                ? `Stade réel : ${stageLabels.fr[session.stade_reel]}`
                : `المرحلة الفعلية: ${stageLabels.ar[session.stade_reel]}`}
            </p>
          </div>
          {session.isCurrent && (
            <span className="ms-auto text-[10px] bg-cyan-950/60 border border-cyan-500/30 text-cyan-400 px-2 py-0.5 rounded-full font-bold">
              {lang === 'fr' ? 'Session actuelle' : 'الجلسة الحالية'}
            </span>
          )}
        </div>

        {/* Financing score */}
        <div className={`flex items-center justify-between p-3 rounded-xl border ${
          isBankable ? 'bg-emerald-950/20 border-emerald-500/25 text-emerald-400' : 'bg-rose-950/20 border-rose-500/25 text-rose-400'
        }`}>
          <div className="flex items-center gap-2 text-sm font-bold">
            {isBankable ? <CheckCircle className="h-4 w-4" /> : <ShieldAlert className="h-4 w-4" />}
            <span>{isBankable ? t.bankable : t.notBankable}</span>
          </div>
          <span className="text-2xl font-extrabold font-mono">{session.financingScore}<span className="text-xs opacity-60">/100</span></span>
        </div>

        {/* Gap alert */}
        {session.gap_detecte && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-amber-950/20 border border-amber-500/20 text-amber-300 text-xs">
            <AlertTriangle className="h-4 w-4 flex-shrink-0 text-amber-400" />
            <span>
              {lang === 'fr'
                ? `Écart détecté : stade perçu "${stageLabels.fr[session.stade_percu]}" ≠ stade réel.`
                : `فجوة محددة: المرحلة المتصورة "${stageLabels.ar[session.stade_percu]}" ≠ الفعلية.`}
            </span>
          </div>
        )}

        {/* Score grid */}
        <div className="grid grid-cols-2 gap-2">
          {scoreKeys.map((key) => {
            const curr = session.scores[key];
            const prev = prevSession?.scores[key];
            return (
              <div key={key} className="flex items-center justify-between bg-slate-950/40 border border-slate-800 rounded-xl p-3">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ background: scoreColors[key] }} />
                  <span className="text-[11px] text-slate-300">{scoreLabels[lang][key]}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold font-mono" style={{ color: scoreColors[key] }}>{curr}</span>
                  <ScoreTrend current={curr} previous={prev} />
                </div>
              </div>
            );
          })}
        </div>

        <button
          onClick={onClose}
          className="mt-1 w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold transition-all"
        >
          {t.close}
        </button>
      </div>
    </div>
  );
}

// ── Overall Progress Bar ──────────────────────────────────────────────────────
function ProgressBar({ current, previous, label, color }) {
  const diff = previous !== undefined ? current - previous : null;
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between text-[11px]">
        <span className="text-slate-300 font-medium">{label}</span>
        <div className="flex items-center gap-2">
          <span className="font-mono font-bold" style={{ color }}>{current}%</span>
          {diff !== null && diff !== 0 && (
            <span className={`font-bold ${diff > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {diff > 0 ? '+' : ''}{diff}
            </span>
          )}
        </div>
      </div>
      <div className="h-2 bg-slate-800 rounded-full overflow-hidden border border-slate-700/40">
        <div
          className="h-full rounded-full transition-all duration-700 ease-out"
          style={{ width: `${current}%`, background: color }}
        />
      </div>
    </div>
  );
}

// ── Main MyPath View ──────────────────────────────────────────────────────────
export default function MyPath({ lang }) {
  const t = translations[lang];
  const [selectedSession, setSelectedSession] = useState(null);
  const [expandChart, setExpandChart] = useState(true);

  const [questionnaireData, setQuestionnaireData] = useState(null);
  const [loadingQuestionnaire, setLoadingQuestionnaire] = useState(true);

  useEffect(() => {
    async function fetchQ() {
      try {
        const data = await loadQuestionnaire();
        setQuestionnaireData(data);
      } catch (e) {
        console.error("Error loading questionnaire in MyPath:", e);
      } finally {
        setLoadingQuestionnaire(false);
      }
    }
    fetchQ();
  }, []);

  const current = sessionHistory[sessionHistory.length - 1];
  const prev = sessionHistory[sessionHistory.length - 2];

  // Overall score = avg of all 5 dimensions
  const avgScore = (sess) =>
    Math.round(scoreKeys.reduce((s, k) => s + sess.scores[k], 0) / scoreKeys.length);

  const currentAvg = avgScore(current);
  const prevAvg = avgScore(prev);
  const globalDiff = currentAvg - prevAvg;

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8 flex flex-col gap-6">

      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-wide flex items-center gap-2">
            <History className="h-6 w-6 text-indigo-400" />
            {t.myPathTitle}
          </h2>
          <p className="text-xs text-slate-400 mt-1">{t.myPathSubtitle}</p>
        </div>
        <div className="flex items-center gap-2 text-xs bg-slate-900 border border-slate-800 text-slate-400 px-3 py-1.5 rounded-lg">
          <Calendar className="h-3.5 w-3.5" />
          <span>{t.sessionLabel} {current.date}</span>
        </div>
      </div>

      {/* Questionnaire Responses Section */}
      {(() => {
        if (loadingQuestionnaire || !questionnaireData) return null;
        
        const description = questionnaireData.description || '';
        const answersArray = questionnaireData.answers || [];
        const hasAnswers = answersArray.length > 0;
        
        if (!hasAnswers && !description) return null;

        return (
          <div className="glass-card p-6 flex flex-col gap-4 border-l-4 border-l-cyan-400">
            {/* Header */}
            <div className="flex items-center gap-2 pb-4 border-b border-slate-800">
              <MessageCircle className="h-5 w-5 text-cyan-400" />
              <div>
                <h3 className="text-sm font-bold text-white">
                  {lang === 'fr' ? 'Réponses du questionnaire' : 'إجابات الاستبيان'}
                </h3>
                <p className="text-xs text-slate-400">
                  {lang === 'fr'
                    ? `${answersArray.length} réponse(s) enregistrée(s)`
                    : `${answersArray.length} إجابة (إجابات) مسجلة`}
                </p>
              </div>
            </div>

            <div className="space-y-3">
              {/* Questions structurées */}
              {hasAnswers && (
                <div className="space-y-2">
                  <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold">
                    {lang === 'fr' ? 'Questions structurées' : 'الأسئلة المنظمة'}
                  </p>
                  <div className="grid gap-2">
                    {answersArray.slice(0, 4).map((ans) => {
                      const qDef = questionnaireData.questions?.find(q => q.id === ans.id) || allQuestions[ans.id];
                      const qLabel = qDef?.texte?.[lang] || qDef?.label?.[lang] || ans.id.replace(/_/g, ' ');
                      
                      let displayAnswer;
                      if (Array.isArray(ans.valeur)) {
                        displayAnswer = ans.valeur
                          .map(v => qDef?.options?.find(o => o.value === v)?.label?.[lang] || v)
                          .join(', ');
                      } else {
                        const opt = qDef?.options?.find(o => o.value === ans.valeur);
                        displayAnswer = opt?.label?.[lang] || opt?.label || String(ans.valeur).substring(0, 120);
                      }
                      
                      return (
                        <div key={ans.id} className="text-sm p-3 rounded-lg bg-slate-950/40 border border-slate-800/60">
                          <p className="text-[10px] text-cyan-400/80 font-semibold uppercase tracking-wide mb-1">
                            {qLabel}
                          </p>
                          <p className="text-slate-200 text-sm">
                            {displayAnswer}
                          </p>
                        </div>
                      );
                    })}
                    {answersArray.length > 4 && (
                      <p className="text-xs text-slate-500 text-center py-1">
                        {lang === 'fr'
                          ? `+${answersArray.length - 4} autres réponses`
                          : `+${answersArray.length - 4} إجابات أخرى`}
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Réponse libre (description) */}
              {description && (
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-slate-500 font-bold mb-2">
                    {lang === 'fr' ? '✏️ Description du projet' : '✏️ وصف المشروع'}
                  </p>
                  <div className="p-4 rounded-xl bg-cyan-950/20 border border-cyan-500/30">
                    <p className="text-sm text-slate-100 whitespace-pre-wrap break-words leading-relaxed">
                      {description}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        );
      })()}

      {/* KPI Summary Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Sessions count */}
        <div className="glass-card p-4 flex flex-col gap-1">
          <p className="text-[10px] text-slate-400 uppercase tracking-wider">
            {lang === 'fr' ? 'Sessions totales' : 'إجمالي الجلسات'}
          </p>
          <p className="text-3xl font-extrabold text-white font-mono">{sessionHistory.length}</p>
          <p className="text-[10px] text-slate-500">{lang === 'fr' ? 'évaluations réalisées' : 'تقييمات منجزة'}</p>
        </div>

        {/* Score financement actuel */}
        <div className="glass-card p-4 flex flex-col gap-1">
          <p className="text-[10px] text-slate-400 uppercase tracking-wider">{t.financingScore}</p>
          <p className="text-3xl font-extrabold text-cyan-400 font-mono">{current.financingScore}</p>
          <ScoreTrend current={current.financingScore} previous={prev?.financingScore} />
        </div>

        {/* Overall average score */}
        <div className="glass-card p-4 flex flex-col gap-1">
          <p className="text-[10px] text-slate-400 uppercase tracking-wider">{t.overallProgress}</p>
          <p className="text-3xl font-extrabold text-indigo-400 font-mono">{currentAvg}%</p>
          <ScoreTrend current={currentAvg} previous={prevAvg} />
        </div>

        {/* Progression */}
        <div className="glass-card p-4 flex flex-col gap-1">
          <p className="text-[10px] text-slate-400 uppercase tracking-wider">
            {lang === 'fr' ? 'Progression totale' : 'التقدم الإجمالي'}
          </p>
          <p className={`text-3xl font-extrabold font-mono ${globalDiff >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {globalDiff >= 0 ? '+' : ''}{globalDiff}%
          </p>
          <p className="text-[10px] text-slate-500">{lang === 'fr' ? 'depuis la session précédente' : 'منذ الجلسة السابقة'}</p>
        </div>
      </div>

      {/* Growth Tip */}
      <div className="glass-card p-4 border-l-4 border-l-amber-400 flex items-start gap-3">
        <div className="h-8 w-8 rounded-lg bg-amber-400/10 border border-amber-400/20 flex items-center justify-center flex-shrink-0">
          <Star className="h-4 w-4 text-amber-400" />
        </div>
        <div>
          <h4 className="text-sm font-bold text-amber-300 mb-0.5">{t.growthTipTitle}</h4>
          <p className="text-xs text-slate-400 leading-relaxed">{t.growthTipDesc}</p>
        </div>
      </div>

      {/* Score Evolution Chart */}
      <div className="glass-card p-6 flex flex-col gap-4">
        <div
          className="flex items-center justify-between cursor-pointer"
          onClick={() => setExpandChart(!expandChart)}
        >
          <div>
            <h3 className="text-base font-bold text-white">{t.progressionChartTitle}</h3>
            <p className="text-xs text-slate-400">{t.progressionChartSubtitle}</p>
          </div>
          <button className="h-8 w-8 rounded-lg bg-slate-800 hover:bg-slate-700 flex items-center justify-center text-slate-400 transition-all">
            {expandChart ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
        </div>

        {expandChart && (
          <ScoreHistoryChart sessions={sessionHistory} lang={lang} />
        )}
      </div>

      {/* Current vs Previous Score Bars */}
      <div className="glass-card p-6 flex flex-col gap-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div>
            <h3 className="text-base font-bold text-white">
              {lang === 'fr' ? 'Comparaison des scores' : 'مقارنة الدرجات'}
            </h3>
            <p className="text-xs text-slate-400">
              {lang === 'fr' ? 'Session actuelle vs précédente' : 'الجلسة الحالية مقابل السابقة'}
            </p>
          </div>
          <div className="flex items-center gap-3 text-[10px] text-slate-400">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-cyan-500 inline-block" />{lang === 'fr' ? 'Actuel' : 'حالي'}</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-slate-600 inline-block" />{lang === 'fr' ? 'Précédent' : 'سابق'}</span>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
          {scoreKeys.map((key) => (
            <ProgressBar
              key={key}
              label={scoreLabels[lang][key]}
              current={current.scores[key]}
              previous={prev?.scores[key]}
              color={scoreColors[key]}
            />
          ))}
        </div>
      </div>

      {/* Session History Table */}
      <div className="glass-card p-6 flex flex-col gap-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <h3 className="text-base font-bold text-white">{t.historyTableTitle}</h3>
          <span className="text-[10px] bg-slate-800 border border-slate-700 text-slate-400 px-2 py-0.5 rounded-full">
            {sessionHistory.length} {lang === 'fr' ? 'sessions' : 'جلسات'}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="border-b border-slate-800">
                {[t.colDate, t.colFinancingScore, t.colStatus, lang === 'fr' ? 'Stade réel' : 'المرحلة الفعلية', t.colActions].map((h) => (
                  <th key={h} className="text-left rtl:text-right text-[10px] uppercase tracking-wider text-slate-500 font-semibold py-2 px-3 first:ps-0 last:pe-0">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {[...sessionHistory].reverse().map((sess, i) => {
                const sessIdx = sessionHistory.indexOf(sess);
                const prevSess = sessIdx > 0 ? sessionHistory[sessIdx - 1] : null;
                const isBankable = sess.status === 'bankable';
                const isFirst = i === 0;

                return (
                  <tr
                    key={sess.id}
                    className={`group transition-colors ${isFirst ? 'bg-cyan-950/10' : 'hover:bg-slate-800/20'}`}
                  >
                    {/* Date */}
                    <td className="py-3 px-3 ps-0">
                      <div className="flex items-center gap-2">
                        {sess.isCurrent && (
                          <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 inline-block animate-pulse" />
                        )}
                        <span className={`text-xs font-mono ${sess.isCurrent ? 'text-cyan-400 font-bold' : 'text-slate-300'}`}>
                          {sess.date}
                        </span>
                      </div>
                    </td>

                    {/* Financing score */}
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-2">
                        <span className={`text-sm font-bold font-mono ${isBankable ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {sess.financingScore}
                        </span>
                        <ScoreTrend current={sess.financingScore} previous={prevSess?.financingScore} />
                      </div>
                    </td>

                    {/* Status badge */}
                    <td className="py-3 px-3">
                      <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full border ${
                        isBankable
                          ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-400'
                          : 'bg-rose-950/40 border-rose-500/30 text-rose-400'
                      }`}>
                        {isBankable ? <CheckCircle className="h-3 w-3" /> : <ShieldAlert className="h-3 w-3" />}
                        {isBankable ? t.bankable : t.notBankable}
                      </span>
                    </td>

                    {/* Stage */}
                    <td className="py-3 px-3">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs text-slate-300">
                          {lang === 'fr' ? stageLabels.fr[sess.stade_reel] : stageLabels.ar[sess.stade_reel]}
                        </span>
                        {sess.gap_detecte && (
                          <AlertTriangle className="h-3 w-3 text-amber-500" title="Gap detected" />
                        )}
                      </div>
                    </td>

                    {/* Action */}
                    <td className="py-3 px-3 pe-0">
                      <button
                        onClick={() => setSelectedSession({ sess, prevSess })}
                        className="flex items-center gap-1 text-[10px] font-semibold text-slate-400 hover:text-cyan-400 transition-colors"
                        title={t.viewDetails}
                      >
                        <ArrowUpRight className="h-3.5 w-3.5" />
                        {lang === 'fr' ? 'Détails' : 'تفاصيل'}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Session detail modal */}
      {selectedSession && (
        <SessionModal
          session={selectedSession.sess}
          prevSession={selectedSession.prevSess}
          lang={lang}
          onClose={() => setSelectedSession(null)}
        />
      )}
    </main>
  );
}
