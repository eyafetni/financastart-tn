import { useState, useEffect } from 'react';
import { 
  CheckCircle2, 
  RotateCcw, 
  Download, 
  AlertTriangle,
  Loader2,
  FileText
} from 'lucide-react';
import { loadQuestionnaire, saveQuestionnaire } from '../data/questionnaireService';

// Textes bilingues locaux pour la structure du diagnostic
const pageTranslations = {
  fr: {
    title: "Diagnostic de votre projet",
    subtitle: "Remplissez les informations ci-dessous pour analyser la viabilité et l'éligibilité de votre startup.",
    descTitle: "1. Description générale de votre projet",
    descPlaceholder: "Décrivez votre projet, vos objectifs, votre cible et votre valeur ajoutée...",
    divergenceAlert: "Divergence de stade détectée",
    questionsTitle: "2. Questions complémentaires",
    saveSuccess: "Sauvegardé",
    saving: "Enregistrement...",
    loading: "Chargement du questionnaire...",
    emptyAnswer: "Sélectionnez ou saisissez une réponse...",
    placeholderNumber: "Exemple: 5",
    placeholderText: "Saisissez votre texte...",
    resetBtn: "Réinitialiser",
    exportBtn: "Exporter JSON",
    resetConfirm: "Réinitialiser toutes les réponses ?",
    charCount: "Caractères :"
  },
  ar: {
    title: "تشخيص مشروعك",
    subtitle: "يرجى ملء المعلومات أدناه لتحليل مدى نضج وأهلية شركتك الناشئة.",
    descTitle: "1. الوصف العام لمشروعك",
    descPlaceholder: "صف مشروعك، أهدافك، الفئة المستهدفة والقيمة المضافة...",
    divergenceAlert: "تم الكشف عن اختلاف في مرحلة المشروع",
    questionsTitle: "2. أسئلة إضافية",
    saveSuccess: "تم الحفظ",
    saving: "جاري الحفظ...",
    loading: "جاري تحميل الاستبيان...",
    emptyAnswer: "اختر أو اكتب إجابتك...",
    placeholderNumber: "مثال: 5",
    placeholderText: "اكتب هنا...",
    resetBtn: "إعادة تعيين",
    exportBtn: "تصدير JSON",
    resetConfirm: "هل تريد إعادة تعيين جميع الإجابات؟",
    charCount: "الأحرف :"
  }
};

export default function Questionnaire({ lang }) {
  const pt = pageTranslations[lang] || pageTranslations.fr;

  const [description, setDescription] = useState('');
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState([]); // [{id, valeur}]
  const [stadeReel, setStadeReel] = useState('');
  const [stadePercu, setStadePercu] = useState('');
  const [divergenceExplication, setDivergenceExplication] = useState('');
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedIndicator, setSavedIndicator] = useState(false);

  // Charger les données depuis le fichier questionnaire.json
  useEffect(() => {
    async function fetchData() {
      try {
        const data = await loadQuestionnaire();
        setDescription(data.description || '');
        setQuestions(data.questions || []);
        setAnswers(data.answers || []);
        setStadeReel(data.stade_reel || '');
        setStadePercu(data.stade_percu || '');
        setDivergenceExplication(data.divergence_explication || '');
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
    setSaving(false);
    setSavedIndicator(true);
    setTimeout(() => setSavedIndicator(false), 2000);
  };

  // Sauvegarde auto temporisée pour la description (debounce)
  useEffect(() => {
    if (loading) return;
    const timer = setTimeout(() => {
      saveAllData(description, answers);
    }, 1000);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [description]);

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

  // Gérer le changement d'une réponse simple (radio, text, number, textarea)
  const handleAnswerChange = (questionId, value) => {
    const updatedAnswers = [...answers];
    const index = updatedAnswers.findIndex(a => a.id === questionId);
    
    if (index !== -1) {
      updatedAnswers[index] = { id: questionId, valeur: value };
    } else {
      updatedAnswers.push({ id: questionId, valeur: value });
    }
    
    setAnswers(updatedAnswers);
    saveAllData(description, updatedAnswers);
  };

  // Gérer le basculement d'une case à cocher (checkbox)
  const handleCheckboxToggle = (questionId, optionValue) => {
    const currentAnswer = answers.find(a => a.id === questionId);
    const currentValues = currentAnswer ? (Array.isArray(currentAnswer.valeur) ? currentAnswer.valeur : [currentAnswer.valeur]) : [];
    
    let newValues;
    if (currentValues.includes(optionValue)) {
      newValues = currentValues.filter(v => v !== optionValue);
    } else {
      newValues = [...currentValues, optionValue];
    }
    
    handleAnswerChange(questionId, newValues);
  };

  // Réinitialiser les données
  const handleReset = async () => {
    if (window.confirm(pt.resetConfirm)) {
      setDescription('');
      setAnswers([]);
      await saveAllData('', []);
    }
  };

  // Exporter au format JSON
  const handleExport = () => {
    const dataStr = JSON.stringify({
      description,
      stade_reel: stadeReel,
      stade_percu: stadePercu,
      divergence_explication: divergenceExplication,
      questions,
      answers
    }, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'questionnaire.json';
    link.click();
  };

  // Détection de la divergence
  const hasDivergence = stadeReel && stadePercu && (stadeReel !== stadePercu);

  return (
    <main 
      className="max-w-4xl mx-auto px-4 sm:px-6 py-8 flex flex-col gap-6"
      dir={lang === 'ar' ? 'rtl' : 'ltr'}
    >
      {/* En-tête principal */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-wide flex items-center gap-2">
            <FileText className="h-6 w-6 text-cyan-400" />
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

      {/* 1. Zone de texte libre (Description) */}
      <div className="glass-card p-6 flex flex-col gap-4 border-l-4 border-l-cyan-500">
        <div>
          <label className="block text-sm font-bold text-white mb-1">
            {pt.descTitle}
          </label>
        </div>
        <div className="relative">
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder={pt.descPlaceholder}
            className="w-full min-h-[120px] p-4 bg-slate-950 border-2 border-slate-800 rounded-xl text-white placeholder-slate-600 focus:border-cyan-500 focus:outline-none text-sm leading-relaxed transition-all resize-none"
          />
        </div>
        <div className="flex justify-between items-center text-xs text-slate-500">
          <span>
            {pt.charCount} <span className="text-slate-300 font-mono">{description.length}</span>
          </span>
        </div>
      </div>

      {/* 2. Bandeau d'alerte de divergence */}
      {hasDivergence && (
        <div className="bg-gradient-to-r from-rose-950/60 to-amber-950/40 border border-rose-500/40 text-rose-200 p-4 rounded-xl flex items-start gap-3 shadow-lg shadow-rose-950/10 animate-fade-in border-s-4 border-s-rose-500">
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

      {/* 3. Questions dynamiques */}
      {questions.length > 0 && (
        <div className="flex flex-col gap-6">
          <div className="border-b border-slate-800 pb-2">
            <h3 className="text-lg font-bold text-white">
              {pt.questionsTitle}
            </h3>
          </div>

          <div className="grid gap-6">
            {questions.map((question) => {
              const answerObj = answers.find(a => a.id === question.id);
              const answerValue = answerObj ? answerObj.valeur : '';

              return (
                <div 
                  key={question.id} 
                  className="glass-card p-6 flex flex-col gap-4 border border-slate-800 hover:border-slate-700/60 transition-all"
                >
                  {/* Libellé de la question */}
                  <div>
                    <h4 className="text-sm font-bold text-slate-200 leading-snug">
                      {question.texte[lang] || question.texte.fr}
                    </h4>
                  </div>

                  {/* Options & Inputs */}
                  <div className="mt-1">
                    {/* Radio input */}
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
                                isSelected ? 'border-cyan-400 bg-cyan-950' : 'border-slate-650'
                              }`}>
                                {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-cyan-400" />}
                              </div>
                              <span className="truncate">{opt.label[lang] || opt.label.fr}</span>
                            </button>
                          );
                        })}
                      </div>
                    )}

                    {/* Checkbox input */}
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
                                isSelected ? 'border-cyan-400 bg-cyan-400' : 'border-slate-650'
                              }`}>
                                {isSelected && <CheckCircle2 className="w-3 h-3 text-slate-950 font-bold" />}
                              </div>
                              <span className="truncate">{opt.label[lang] || opt.label.fr}</span>
                            </button>
                          );
                        })}
                      </div>
                    )}

                    {/* Textarea input */}
                    {question.type === 'textarea' && (
                      <textarea
                        value={answerValue || ''}
                        onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                        placeholder={question.placeholder?.[lang] || question.placeholder?.fr || pt.placeholderText}
                        className="w-full min-h-[90px] p-3 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-600 focus:border-cyan-500 focus:outline-none text-xs leading-relaxed transition-all resize-none"
                      />
                    )}

                    {/* Number input */}
                    {question.type === 'number' && (
                      <input
                        type="number"
                        value={answerValue || ''}
                        onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                        placeholder={question.placeholder?.[lang] || question.placeholder?.fr || pt.placeholderNumber}
                        className="w-full max-w-xs px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:border-cyan-500 focus:outline-none text-xs transition-all"
                      />
                    )}

                    {/* Fallback to simple Text input */}
                    {question.type !== 'radio' && question.type !== 'checkbox' && question.type !== 'textarea' && question.type !== 'number' && (
                      <input
                        type="text"
                        value={answerValue || ''}
                        onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                        placeholder={question.placeholder?.[lang] || question.placeholder?.fr || pt.placeholderText}
                        className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:border-cyan-500 focus:outline-none text-xs transition-all"
                      />
                    )}
                  </div>

                  {/* Indicateur de saisie complétée */}
                  {answerValue !== undefined && answerValue !== '' && (Array.isArray(answerValue) ? answerValue.length > 0 : true) && (
                    <div className="flex items-center gap-1.5 text-[10px] text-cyan-400 font-semibold self-start mt-1 bg-cyan-950/20 px-2 py-0.5 rounded border border-cyan-800/30">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                      <span>{lang === 'fr' ? 'Complété' : 'مكتمل'}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Actions de bas de page */}
      <div className="flex flex-col sm:flex-row gap-3 mt-4 border-t border-slate-800 pt-6">
        <button
          onClick={handleExport}
          className="flex-1 py-3 px-4 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 text-xs font-semibold rounded-xl border border-cyan-500/30 transition-colors flex items-center justify-center gap-2 cursor-pointer"
        >
          <Download className="h-4 w-4" />
          {pt.exportBtn}
        </button>
        <button
          onClick={handleReset}
          className="py-3 px-4 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-semibold rounded-xl border border-rose-500/30 transition-colors flex items-center justify-center gap-2 cursor-pointer"
        >
          <RotateCcw className="h-4 w-4" />
          {pt.resetBtn}
        </button>
      </div>
    </main>
  );
}
