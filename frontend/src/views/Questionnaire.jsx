import { useState, useEffect, useRef } from 'react';
import { 
  CheckCircle2, 
  RotateCcw, 
  AlertTriangle,
  Loader2,
  FileText,
  ChevronLeft,
  ChevronRight,
  ClipboardList
} from 'lucide-react';
import { loadQuestionnaire, saveQuestionnaire } from '../data/questionnaireService';
import { getAdaptedData, translateValue } from '../data/dataAdapter';

// Textes bilingues locaux pour la structure du diagnostic
const pageTranslations = {
  fr: {
    title: "Diagnostic de votre projet",
    subtitle: "Remplissez les informations ci-dessous pour analyser la viabilité et l'éligibilité de votre startup.",
    divergenceAlert: "Divergence de stade détectée",
    saveSuccess: "Sauvegardé",
    saving: "Enregistrement...",
    loading: "Chargement du questionnaire...",
    resetBtn: "Réinitialiser",
    exportBtn: "Exporter JSON",
    resetConfirm: "Réinitialiser toutes les réponses ?",
    nextStep: "Suivant",
    prevStep: "Précédent",
    finish: "Diagnostic complété",
    stepLabel: "Étape {current} sur {total}",
    answeredPill: "{answered} sur {total} questions répondues",
    emptyAnswer: "Sélectionnez ou saisissez une réponse...",
    placeholderNumber: "Exemple: 5",
    placeholderText: "Saisissez votre texte...",
    charCount: "Caractères :",
    noQuestions: "Aucune question disponible pour cette étape."
  },
  ar: {
    title: "تشخيص مشروعك",
    subtitle: "يرجى ملء المعلومات أدناه لتحليل مدى نضج وأهلية شركتك الناشئة.",
    divergenceAlert: "تم الكشف عن اختلاف في مرحلة المشروع",
    saveSuccess: "تم الحفظ",
    saving: "جاري الحفظ...",
    loading: "جاري تحميل الاستبيان...",
    resetBtn: "إعادة تعيين",
    exportBtn: "تصدير JSON",
    resetConfirm: "هل تريد إعادة تعيين جميع الإجابات؟",
    nextStep: "التالي",
    prevStep: "السابق",
    finish: "تم إكمال التشخيص",
    stepLabel: "الخطوة {current} من {total}",
    answeredPill: "تمت الإجابة على {answered} من {total} أسئلة",
    emptyAnswer: "اختر أو اكتب إجابتك...",
    placeholderNumber: "مثال: 5",
    placeholderText: "اكتب هنا...",
    charCount: "الأحرف :",
    noQuestions: "لا توجد أسئلة متاحة لهذه الخطوة."
  }
};

// Détermine le secteur choisi pour le filtrage par branch
const getSelectedSector = (answers, detectedSector) => {
  if (answers.confirmation_secteur === 'non') {
    return answers.choix_secteur;
  }
  const detSector = detectedSector || 'agriculture';
  if (detSector === 'agri-food') return 'agriculture';
  return detSector;
};

// Algorithme de filtrage des questions dynamiques (branch, condition, next)
const getActiveQuestions = (questions, answers, detectedSector) => {
  const active = [];
  let i = 0;
  const sector = getSelectedSector(answers, detectedSector);
  
  while (i < questions.length) {
    const q = questions[i];
    
    // 1. Filtrer par branch (secteur)
    if (q.branch && !q.branch.includes(sector)) {
      i++;
      continue;
    }
    
    // 2. Filtrer par condition
    if (q.condition) {
      const [field, val] = q.condition.split('=');
      if (answers[field] !== val) {
        i++;
        continue;
      }
    }
    
    active.push(q);
    
    // 3. Routage next dynamique (saut de questions)
    if (q.next) {
      const answerVal = answers[q.id];
      const nextId = q.next[answerVal];
      if (nextId) {
        const nextIdx = questions.findIndex(quest => quest.id === nextId);
        if (nextIdx !== -1 && nextIdx > i) {
          i = nextIdx;
          continue;
        }
      }
    }
    
    i++;
  }
  return active;
};

export default function Questionnaire({ lang }) {
  const pt = pageTranslations[lang] || pageTranslations.fr;

  const [description, setDescription] = useState('');
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({}); // {id: valeur}
  const [stadeReel, setStadeReel] = useState('');
  const [stadePercu, setStadePercu] = useState('');
  const [divergenceExplication, setDivergenceExplication] = useState('');
  
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedIndicator, setSavedIndicator] = useState(false);

  const lastSavedAnswersRef = useRef(null);

  // Charger les données de la startup pour la substitution des variables
  const adaptedData = getAdaptedData();
  const detectedSector = adaptedData.secteur;
  const detectedRegion = adaptedData.localisation;
  const detectedStage = adaptedData.maturity.perceivedStage;

  // Charger les données depuis le fichier questionnaire.json
  useEffect(() => {
    async function fetchData() {
      try {
        const data = await loadQuestionnaire();
        setDescription(data.description || '');
        setQuestions(data.questions || []);
        
        // Formater les réponses en objet plat {id: valeur}
        let loadedAnswers = {};
        if (Array.isArray(data.answers)) {
          data.answers.forEach(item => {
            if (item && item.id) {
              loadedAnswers[item.id] = item.valeur;
            }
          });
        } else if (data.answers && typeof data.answers === 'object') {
          loadedAnswers = data.answers;
        }

        // Assurer que le champ de description libre est bien inclus dans les réponses
        if (!loadedAnswers.description_libre && data.description) {
          loadedAnswers.description_libre = data.description;
        }
        
        setAnswers(loadedAnswers);
        setStadeReel(data.stade_reel || '');
        setStadePercu(data.stade_percu || '');
        setDivergenceExplication(data.divergence_explication || '');
        
        // Initialiser la ref de sauvegarde
        lastSavedAnswersRef.current = JSON.stringify(loadedAnswers) + (data.description || '');
      } catch (err) {
        console.error("Erreur lors de l'initialisation du diagnostic:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  // Sauvegarder la totalité des données
  const saveAllData = async (newDesc = description, newAnswers = answers) => {
    setSaving(true);
    const payload = {
      description: newDesc,
      stade_reel: stadeReel,
      stade_percu: stadePercu,
      divergence_explication: divergenceExplication,
      questions,
      answers: newAnswers
    };
    await saveQuestionnaire(payload);
    lastSavedAnswersRef.current = JSON.stringify(newAnswers) + newDesc;
    setSaving(false);
    setSavedIndicator(true);
    setTimeout(() => setSavedIndicator(false), 2000);
  };

  // Sauvegarde auto temporisée (debounce) pour la saisie clavier libre
  useEffect(() => {
    if (loading) return;
    const currentPayloadKey = JSON.stringify(answers) + description;
    if (currentPayloadKey === lastSavedAnswersRef.current) return;

    const timer = setTimeout(() => {
      saveAllData(description, answers);
    }, 1000);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [answers, description]);

  // Gérer le changement d'une réponse simple (radio, text, number, textarea)
  const handleAnswerChange = (questionId, value) => {
    const updatedAnswers = {
      ...answers,
      [questionId]: value
    };
    setAnswers(updatedAnswers);

    let updatedDesc = description;
    if (questionId === 'description_libre') {
      updatedDesc = value;
      setDescription(value);
    }
    
    // Sauvegarder immédiatement uniquement pour les clics radios pour fluidité, debouncer le reste
    const questionDef = questions.find(q => q.id === questionId);
    const isClickType = questionDef?.type === 'radio';
    if (isClickType) {
      saveAllData(updatedDesc, updatedAnswers);
    }
  };

  // Gérer le basculement d'une case à cocher (checkbox)
  const handleCheckboxToggle = (questionId, optionValue) => {
    const currentAnswer = answers[questionId];
    const currentValues = Array.isArray(currentAnswer) 
      ? currentAnswer 
      : (currentAnswer ? [currentAnswer] : []);
    
    let newValues;
    if (currentValues.includes(optionValue)) {
      newValues = currentValues.filter(v => v !== optionValue);
    } else {
      newValues = [...currentValues, optionValue];
    }
    
    handleAnswerChange(questionId, newValues);
    // Sauvegarder immédiatement les checkboxes
    saveAllData(description, {
      ...answers,
      [questionId]: newValues
    });
  };

  // Réinitialiser les données
  const handleReset = async () => {
    if (window.confirm(pt.resetConfirm)) {
      setDescription('');
      setAnswers({});
      setCurrentStepIndex(0);
      await saveAllData('', {});
    }
  };



  if (loading) {
    return (
      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-12 flex items-center justify-center">
        <div className="glass-card p-8 text-center flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 text-cyan-400 animate-spin" />
          <p className="text-slate-400 text-sm font-semibold">{pt.loading}</p>
        </div>
      </main>
    );
  }

  // Détection de la divergence
  const hasDivergence = stadeReel && stadePercu && (stadeReel !== stadePercu);

  // Calculer la liste des questions et étapes actives
  const activeQuestions = getActiveQuestions(questions, answers, detectedSector);
  const activeEtapes = Array.from(new Set(activeQuestions.map(q => q.etape).filter(Boolean)));

  const steps = activeEtapes;
  const currentStep = steps[currentStepIndex] || steps[0];

  // Questions spécifiques à l'étape en cours
  const currentStepQuestions = activeQuestions.filter(q => q.etape === currentStep);

  // Nombre de questions complétées dans cette étape
  const answeredInStep = currentStepQuestions.filter(q => {
    const ans = answers[q.id];
    return ans !== undefined && ans !== '' && (Array.isArray(ans) ? ans.length > 0 : true);
  }).length;
  const totalInStep = currentStepQuestions.length;

  return (
    <main 
      className="max-w-4xl mx-auto px-4 sm:px-6 py-8 flex flex-col gap-6"
      dir={lang === 'ar' ? 'rtl' : 'ltr'}
    >
      {/* En-tête principal */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-wide flex items-center gap-2">
            <ClipboardList className="h-6 w-6 text-cyan-400" />
            {pt.title}
          </h2>
          <p className="text-xs text-slate-400 mt-1">{pt.subtitle}</p>
        </div>

        {/* Indicateurs de sauvegarde */}
        <div className="flex items-center gap-3">
          {saving && (
            <span className="flex items-center gap-1.5 text-xs text-cyan-400 bg-cyan-950/40 border border-cyan-800/40 px-3 py-1 rounded-full">
              <Loader2 className="h-3 w-3 animate-spin" />
              {pt.saving}
            </span>
          )}
          {savedIndicator && (
            <span className="flex items-center gap-1.5 text-xs text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-3 py-1 rounded-full animate-pulse">
              <CheckCircle2 className="h-3.5 w-3.5" />
              {pt.saveSuccess}
            </span>
          )}
        </div>
      </div>

      {/* Barre d'étape / Stepper responsive */}
      {steps.length > 0 && (
        <div className="flex flex-col gap-3">
          {/* Stepper sur écran large */}
          <div className="hidden md:flex items-center gap-2 bg-slate-900/60 p-2 rounded-2xl border border-slate-800/80 overflow-x-auto">
            {steps.map((step, idx) => {
              const isCurrent = idx === currentStepIndex;
              const isPast = idx < currentStepIndex;
              return (
                <button
                  key={step}
                  onClick={() => setCurrentStepIndex(idx)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-xl text-[10px] font-extrabold tracking-wide uppercase transition-all whitespace-nowrap cursor-pointer ${
                    isCurrent 
                      ? 'bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 shadow-sm shadow-cyan-950/20' 
                      : isPast
                        ? 'text-emerald-400 hover:text-emerald-300'
                        : 'text-slate-500 hover:text-slate-400'
                  }`}
                >
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] ${
                    isCurrent 
                      ? 'bg-cyan-400 text-slate-950 font-extrabold' 
                      : isPast
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : 'bg-slate-800 text-slate-500 border border-slate-700/50'
                  }`}>
                    {isPast ? '✓' : idx + 1}
                  </div>
                  {step}
                </button>
              );
            })}
          </div>

          {/* Stepper sur mobile */}
          <div className="flex md:hidden flex-col gap-1.5 p-4 bg-slate-900/60 rounded-2xl border border-slate-800/80">
            <div className="text-[10px] text-slate-500 font-extrabold uppercase tracking-wider">
              {pt.stepLabel.replace('{current}', currentStepIndex + 1).replace('{total}', steps.length)}
            </div>
            <div className="text-sm font-bold text-white truncate">{currentStep}</div>
            <div className="h-1 bg-slate-800 rounded-full overflow-hidden">
              <div 
                className="h-full bg-cyan-500 rounded-full transition-all duration-300"
                style={{ width: `${((currentStepIndex + 1) / steps.length) * 100}%` }}
              />
            </div>
          </div>
          
          {/* Progress Pill */}
          <div className="flex justify-between items-center text-xs text-slate-500 px-1">
            <span>{pt.answeredPill.replace('{answered}', answeredInStep).replace('{total}', totalInStep)}</span>
          </div>
        </div>
      )}

      {/* Bandeau d'alerte de divergence */}
      {hasDivergence && (
        <div className="bg-gradient-to-r from-rose-950/60 to-amber-950/40 border border-rose-500/40 text-rose-200 p-4 rounded-xl flex items-start gap-3 shadow-lg border-s-4 border-s-rose-500">
          <AlertTriangle className="h-5 w-5 text-rose-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h4 className="text-sm font-bold text-rose-300">
              {pt.divergenceAlert} ({stadePercu} → {stadeReel})
            </h4>
            <p className="text-xs text-rose-200 mt-1 leading-relaxed">
              {divergenceExplication}
            </p>
          </div>
        </div>
      )}

      {/* Conteneur principal des questions de l'étape courante */}
      <div className="flex flex-col gap-6 animate-fade-in">
        {currentStepQuestions.length > 0 ? (
          currentStepQuestions.map((question) => {
            const answerValue = answers[question.id] || '';
            const isCompleted = answerValue !== undefined && answerValue !== '' && (Array.isArray(answerValue) ? answerValue.length > 0 : true);

            // Remplacement dynamique des placeholders
            let labelText = question.texte[lang] || question.texte.fr || '';
            labelText = labelText
              .replace('{label}', translateValue(detectedSector, lang))
              .replace('{région}', translateValue(detectedRegion, lang))
              .replace('{stade}', translateValue(detectedStage, lang));

            return (
              <div 
                key={question.id} 
                className={`glass-card p-6 flex flex-col gap-4 border transition-all ${
                  isCompleted 
                    ? 'border-cyan-500/30 shadow-md shadow-cyan-950/5' 
                    : 'border-slate-800 hover:border-slate-700/60'
                }`}
              >
                {/* En-tête de la question */}
                <div className="flex justify-between items-start gap-3">
                  <h4 className="text-sm font-bold text-slate-200 leading-snug">
                    {labelText}
                  </h4>
                  {isCompleted && (
                    <span className="flex items-center gap-1 text-[10px] text-cyan-400 font-semibold bg-cyan-950/30 px-2 py-0.5 rounded border border-cyan-800/40 flex-shrink-0">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      <span>{lang === 'fr' ? 'Rempli' : 'مكتمل'}</span>
                    </span>
                  )}
                </div>

                {/* Formulaires de saisie / d'options */}
                <div className="mt-1">
                  {/* Option type: radio */}
                  {question.type === 'radio' && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {question.options?.map((opt) => {
                        const isSelected = answerValue === opt.value;
                        return (
                          <button
                            key={opt.value}
                            type="button"
                            onClick={() => handleAnswerChange(question.id, opt.value)}
                            className={`p-3.5 text-xs font-semibold rounded-xl text-left rtl:text-right border-2 transition-all flex items-center gap-3 cursor-pointer ${
                              isSelected 
                                ? 'border-cyan-500 bg-cyan-950/20 text-cyan-300' 
                                : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 text-slate-400 hover:text-slate-200'
                            }`}
                          >
                            <div className={`w-4 h-4 rounded-full border flex items-center justify-center flex-shrink-0 ${
                              isSelected ? 'border-cyan-400 bg-cyan-950' : 'border-slate-700'
                            }`}>
                              {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />}
                            </div>
                            <span className="truncate">{opt.label[lang] || opt.label.fr}</span>
                          </button>
                        );
                      })}
                    </div>
                  )}

                  {/* Option type: checkbox */}
                  {question.type === 'checkbox' && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      {question.options?.map((opt) => {
                        const isSelected = Array.isArray(answerValue) ? answerValue.includes(opt.value) : false;
                        return (
                          <button
                            key={opt.value}
                            type="button"
                            onClick={() => handleCheckboxToggle(question.id, opt.value)}
                            className={`p-3.5 text-xs font-semibold rounded-xl text-left rtl:text-right border-2 transition-all flex items-center gap-3 cursor-pointer ${
                              isSelected 
                                ? 'border-cyan-500 bg-cyan-950/20 text-cyan-300' 
                                : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 text-slate-400 hover:text-slate-200'
                            }`}
                          >
                            <div className={`w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 ${
                              isSelected ? 'border-cyan-400 bg-cyan-400' : 'border-slate-700'
                            }`}>
                              {isSelected && <CheckCircle2 className="w-3 h-3 text-slate-950 font-bold" />}
                            </div>
                            <span className="truncate">{opt.label[lang] || opt.label.fr}</span>
                          </button>
                        );
                      })}
                    </div>
                  )}

                  {/* Option type: textarea */}
                  {question.type === 'textarea' && (
                    <div className="flex flex-col gap-2">
                      <textarea
                        value={answerValue}
                        onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                        placeholder={question.placeholder?.[lang] || question.placeholder?.fr || pt.placeholderText}
                        className="w-full min-h-[110px] p-3.5 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-600 focus:border-cyan-500 focus:outline-none text-xs leading-relaxed transition-all resize-none"
                      />
                      <span className="text-[10px] text-slate-500 self-end">
                        {pt.charCount} <span className="font-mono text-slate-400">{answerValue.length}</span>
                      </span>
                    </div>
                  )}

                  {/* Option type: number */}
                  {question.type === 'number' && (
                    <input
                      type="number"
                      value={answerValue}
                      onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                      placeholder={question.placeholder?.[lang] || question.placeholder?.fr || pt.placeholderNumber}
                      className="w-full max-w-xs px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:border-cyan-500 focus:outline-none text-xs transition-all"
                    />
                  )}

                  {/* Fallback simple Text input */}
                  {question.type !== 'radio' && question.type !== 'checkbox' && question.type !== 'textarea' && question.type !== 'number' && (
                    <input
                      type="text"
                      value={answerValue}
                      onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                      placeholder={question.placeholder?.[lang] || question.placeholder?.fr || pt.placeholderText}
                      className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:border-cyan-500 focus:outline-none text-xs transition-all"
                    />
                  )}
                </div>
              </div>
            );
          })
        ) : (
          <div className="glass-card p-8 text-center text-slate-500 text-xs font-semibold">
            {pt.noQuestions}
          </div>
        )}
      </div>

      {/* Navigation et Actions en bas de page */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between mt-6 border-t border-slate-800 pt-6 gap-4">
        {/* Précédent */}
        <button
          type="button"
          onClick={() => setCurrentStepIndex(prev => Math.max(0, prev - 1))}
          disabled={currentStepIndex === 0}
          className={`px-5 py-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 border transition-all cursor-pointer ${
            currentStepIndex === 0 
              ? 'opacity-30 border-slate-800 text-slate-600 cursor-not-allowed' 
              : 'border-slate-800 bg-slate-900/40 text-slate-300 hover:border-slate-700 hover:text-white hover:bg-slate-900/80'
          }`}
        >
          <ChevronLeft className="h-4 w-4 rtl:rotate-180" />
          {pt.prevStep}
        </button>
        
        {/* Utilitaires (Reset) */}
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={handleReset}
            className="py-3 px-4 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-semibold rounded-xl border border-rose-500/30 transition-colors flex items-center justify-center gap-2 cursor-pointer"
          >
            <RotateCcw className="h-4 w-4" />
            {pt.resetBtn}
          </button>
        </div>

        {/* Suivant ou Terminer */}
        {currentStepIndex < steps.length - 1 ? (
          <button
            type="button"
            onClick={() => setCurrentStepIndex(prev => Math.min(steps.length - 1, prev + 1))}
            className="px-5 py-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-lg shadow-cyan-500/10 cursor-pointer"
          >
            {pt.nextStep}
            <ChevronRight className="h-4 w-4 rtl:rotate-180" />
          </button>
        ) : (
          <div className="px-5 py-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
            <CheckCircle2 className="h-4 w-4 animate-pulse" />
            {pt.finish}
          </div>
        )}
      </div>
    </main>
  );
}
