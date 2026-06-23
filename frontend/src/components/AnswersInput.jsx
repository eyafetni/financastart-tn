import React, { useState, useEffect, useRef } from 'react';
import { PenTool, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';
import { translations } from '../data/interfaceTranslations';

export default function AnswersInput({ answers, onSaveAnswers, lang }) {
  const t = translations[lang];

  // Set initial value based on answers structure in dashboard.json
  const initialText = answers?.free_text?.text || answers?.responses?.[0]?.answer || '';
  const [text, setText] = useState(initialText);
  const [saveStatus, setSaveStatus] = useState('idle'); // 'idle' | 'saving' | 'saved' | 'error'
  const isFirstMount = useRef(true);
  const debounceTimer = useRef(null);

  // Sync state if answers prop changes from parent
  useEffect(() => {
    if (answers) {
      const newText = answers?.free_text?.text || answers?.responses?.[0]?.answer || '';
      setText(newText);
    }
  }, [answers]);

  const saveText = async (currentText) => {
    setSaveStatus('saving');
    try {
      const updatedAnswers = {
        last_updated: new Date().toISOString().split('T')[0],
        free_text: {
          text: currentText,
          timestamp: new Date().toISOString()
        },
        responses: [
          {
            question_id: "free_text_response",
            type: "texte",
            answer: currentText,
            timestamp: new Date().toISOString()
          }
        ]
      };

      const success = await onSaveAnswers(updatedAnswers);
      if (success) {
        setSaveStatus('saved');
        // Clear saved indicator after 2.5s
        setTimeout(() => setSaveStatus('idle'), 2500);
      } else {
        setSaveStatus('error');
      }
    } catch (e) {
      console.error('Error saving free text:', e);
      setSaveStatus('error');
    }
  };

  // Debounced auto-save
  useEffect(() => {
    if (isFirstMount.current) {
      isFirstMount.current = false;
      return;
    }

    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }

    // Set auto-save timer (1.2 seconds)
    debounceTimer.current = setTimeout(() => {
      saveText(text);
    }, 1200);

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current);
      }
    };
  }, [text]);

  const handleBlur = () => {
    // Save immediately on blur if text has changed and is not already saving
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current);
    }
    const currentSavedText = answers?.free_text?.text || answers?.responses?.[0]?.answer || '';
    if (text !== currentSavedText && saveStatus !== 'saving') {
      saveText(text);
    }
  };

  return (
    <div className="glass-card p-6 flex flex-col gap-4">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide flex items-center gap-2">
            <PenTool className="h-5 w-5 text-indigo-400" />
            {t.answersTitle}
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">{t.answersSubtitle}</p>
        </div>

        {/* Status indicator */}
        <div className="flex items-center gap-2 text-xs h-7">
          {saveStatus === 'saving' && (
            <span className="flex items-center gap-1.5 text-cyan-400 bg-cyan-950/40 border border-cyan-800/40 px-3 py-1 rounded-full font-medium">
              <Loader2 className="h-3 w-3 animate-spin" />
              {t.saveStatusSaving}
            </span>
          )}
          {saveStatus === 'saved' && (
            <span className="flex items-center gap-1.5 text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-3 py-1 rounded-full font-medium animate-pulse">
              <CheckCircle2 className="h-3.5 w-3.5" />
              {t.saveStatusSaved}
            </span>
          )}
          {saveStatus === 'error' && (
            <span className="flex items-center gap-1.5 text-rose-400 bg-rose-950/40 border border-rose-800/40 px-3 py-1 rounded-full font-medium">
              <AlertCircle className="h-3.5 w-3.5" />
              {t.saveStatusError}
            </span>
          )}
        </div>
      </div>

      {/* Input container */}
      <div className="flex flex-col gap-2 relative">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onBlur={handleBlur}
          placeholder={t.placeholderAnswers}
          className="w-full min-h-[140px] p-4 bg-slate-950 border border-slate-850 hover:border-slate-800 focus:border-cyan-500/80 rounded-2xl text-white placeholder-slate-600 focus:outline-none text-xs leading-relaxed transition-all resize-none shadow-inner"
          dir={lang === 'ar' ? 'rtl' : 'ltr'}
        />
        <div className="flex justify-between items-center text-[10px] text-slate-650 px-1">
          <span>{lang === 'fr' ? 'Auto-enregistrement activé' : 'تفعيل الحفظ التلقائي'}</span>
          <span>
            {lang === 'fr' ? 'Caractères' : 'الحروف'}: <span className="font-mono text-slate-500">{text.length}</span>
          </span>
        </div>
      </div>
    </div>
  );
}
