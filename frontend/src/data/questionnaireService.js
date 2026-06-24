import defaultQuestionnaire from './questionnaire.json';
import {
  analyzeDemoProject,
  getDemoQuestionnaireData,
  isDemoSession,
  saveDemoQuestionnaireData
} from './demoStore';

// Définir toutes les questions possibles comme fallback et pour la traduction dans les vues existantes
export const allQuestions = {
  legal_status: {
    id: 'legal_status',
    category: 'legal',
    type: 'radio',
    label: { fr: 'Statut légal de l\'entreprise', ar: 'الحالة القانونية للشركة' },
    options: [
      { value: 'auto-entrepreneur', label: { fr: 'Auto-entrepreneur', ar: 'عامل حر' } },
      { value: 'sarl', label: { fr: 'SARL', ar: 'شركة ذات مسؤولية محدودة' } },
      { value: 'sas', label: { fr: 'SAS', ar: 'شركة مساهمة mbssat' } },
      { value: 'none', label: { fr: 'Aucune structure enregistrée', ar: 'لا توجد هيكلة قانونية' } }
    ]
  },
  market_validation: {
    id: 'market_validation',
    category: 'market',
    type: 'checkbox',
    label: { fr: 'Quelles validations client avez-vous effectuées?', ar: 'ما هي التحققات من العملاء التي أجريتها؟' },
    options: [
      { value: 'interviews', label: { fr: 'Entretiens utilisateurs', ar: 'مقابلات المستخدمين' } },
      { value: 'prototype_test', label: { fr: 'Test de prototype', ar: 'اختبار النموذج' } },
      { value: 'beta_users', label: { fr: 'Utilisateurs bêta', ar: 'المستخدمون التجريبيون' } },
      { value: 'none', label: { fr: 'Aucune validation', ar: 'بدون تحقق' } }
    ]
  },
  agri_specifics: {
    id: 'agri_specifics',
    category: 'sector',
    type: 'radio',
    label: { fr: 'Produits agricoles: Type de chaîne de valeur', ar: 'المنتجات agricoles: نوع سلسلة القيمة' },
    options: [
      { value: 'production', label: { fr: 'Production/Transformation', ar: 'الإنتاج/التحويل' } },
      { value: 'distribution', label: { fr: 'Distribution/Logistique', ar: 'التوزيع/الخدمات اللوجستية' } },
      { value: 'retail', label: { fr: 'Vente au détail', ar: 'البيع بالتجزئة' } },
      { value: 'tech', label: { fr: 'Solution technologique agri', ar: 'حل تكنولوجي زراعي' } }
    ]
  },
  funding_readiness: {
    id: 'funding_readiness',
    category: 'financing',
    type: 'radio',
    label: { fr: 'Êtes-vous réellement prêt pour le financement?', ar: 'هل أنت حقاً مستعداً للتمويل؟' },
    options: [
      { value: 'very_ready', label: { fr: 'Très prêt - tout est en place', ar: 'مستعد جداً - كل شيء جاهز' } },
      { value: 'partially_ready', label: { fr: 'Partiellement - besoin de clarifications', ar: 'جزئياً - بحاجة لتوضيحات' } },
      { value: 'not_ready', label: { fr: 'Pas prêt - besoin de travail', ar: 'غير مستعد - بحاجة للعمل' } }
    ]
  },
  legal_structure_details: {
    id: 'legal_structure_details',
    category: 'legal',
    type: 'text',
    label: { fr: 'Prochaines étapes pour structurer légalement (détails)', ar: 'الخطوات التالية للهيكلة القانونية (التفاصيل)' }
  },
  revenue_model: {
    id: 'revenue_model',
    category: 'commercial',
    type: 'radio',
    label: { fr: 'Modèle de revenu principal', ar: 'نموذج الإيرادات الرئيسي' },
    options: [
      { value: 'b2b', label: { fr: 'B2B (Entreprise à Entreprise)', ar: 'B2B' } },
      { value: 'b2c', label: { fr: 'B2C (Entreprise à Consommateur)', ar: 'B2C' } },
      { value: 'hybrid', label: { fr: 'Hybride', ar: 'مختلط' } },
      { value: 'subscription', label: { fr: 'Abonnement', ar: 'الاشتراك' } }
    ]
  },
  time_to_market: {
    id: 'time_to_market',
    category: 'timeline',
    type: 'radio',
    label: { fr: 'Délai estimé avant lancement commercial', ar: 'الوقت المتوقع قبل الإطلاق التجاري' },
    options: [
      { value: '0-3months', label: { fr: '0-3 mois', ar: '0-3 أشهر' } },
      { value: '3-6months', label: { fr: '3-6 mois', ar: '3-6 أشهر' } },
      { value: '6-12months', label: { fr: '6-12 mois', ar: '6-12 شهراً' } },
      { value: 'after_1year', label: { fr: 'Plus d\'1 an', ar: 'أكثر من سنة' } }
    ]
  }
};

/**
 * Charge les données complètes du questionnaire depuis la base de données
 */
export async function loadQuestionnaire() {
  if (!isDemoSession()) {
    return defaultQuestionnaire;
  }

  const savedQuestionnaire = getDemoQuestionnaireData();
  return savedQuestionnaire || defaultQuestionnaire;
}

/**
 * Sauvegarde les données complètes du questionnaire dans la base de données
 */
export async function saveQuestionnaire(data) {
  if (!isDemoSession()) {
    return { success: false, error: 'Non authentifié ou projet introuvable' };
  }

  saveDemoQuestionnaireData(data);
  return { success: true, demo: true };
}

/**
 * Sauvegarde uniquement la description
 */
export async function saveDescription(description) {
  const data = await loadQuestionnaire();
  data.description = description;
  return await saveQuestionnaire(data);
}

/**
 * Sauvegarde uniquement les réponses (au format [{ id, valeur }])
 */
export async function saveAnswers(answersArray) {
  const data = await loadQuestionnaire();
  data.answers = answersArray;
  return await saveQuestionnaire(data);
}

/**
 * Lance l'analyse complète (F1 + F2) sur le backend
 */
export async function analyzeProject(payload) {
  if (!isDemoSession()) {
    return { success: false, error: 'Non authentifié ou projet introuvable' };
  }

  return analyzeDemoProject(payload);
}

