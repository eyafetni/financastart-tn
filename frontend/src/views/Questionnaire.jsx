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
import { loadQuestionnaire, saveQuestionnaire, analyzeProject } from '../data/questionnaireService';
import { getAdaptedData, translateValue } from '../data/dataAdapter';
import { useNavigate } from 'react-router-dom';

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
    exportBtn: "Analyser le projet",
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
  const navigate = useNavigate();

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

  const [detectedSector, setDetectedSector] = useState('');
  const [detectedRegion, setDetectedRegion] = useState('');
  const [detectedStage, setDetectedStage] = useState('');
  const [detectedNom, setDetectedNom] = useState('');

  // Charger les données depuis le fichier questionnaire.json et l'API
  useEffect(() => {
    async function fetchData() {
      try {
        const projectId = localStorage.getItem('project_id') || 1;
        const token = localStorage.getItem('token');
        if (token) {
          const res = await fetch(`http://localhost:8000/projects/${projectId}/dashboard`, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          if (res.ok) {
            const rawData = await res.json();
            const adapted = getAdaptedData(rawData);
            setDetectedSector(adapted.secteur);
            setDetectedRegion(adapted.localisation);
            setDetectedStage(adapted.maturity.perceivedStage);
            setDetectedNom(adapted.startupName || '');
          }
        }
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

  // Envoyer les réponses pour analyse et enregistrement en BD
  const handleAnalyzeProject = async () => {
    // 1. Résoudre le Secteur
    let rawSecteur = answers.choix_secteur;
    if (!rawSecteur && answers.confirmation_secteur === 'oui') {
      rawSecteur = detectedSector;
    }
    if (!rawSecteur) rawSecteur = detectedSector || 'agriculture';
    if (rawSecteur === 'agri-food') rawSecteur = 'agriculture';

    const sectorMapping = {
      'agriculture': 'agriculture_sylviculture_peche',
      'industrie': 'industrie_construction',
      'commerce': 'commerce_transport_logistique',
      'service': 'service_tourisme',
      'technologie': 'tech_services_entreprise'
    };
    const resolvedSector = sectorMapping[rawSecteur] || rawSecteur;

    // 2. Résoudre la Localisation
    let resolvedLocalisation = detectedRegion;
    if (answers.confirmation_region === 'non') {
      resolvedLocalisation = answers.choix_region;
    }
    if (!resolvedLocalisation) resolvedLocalisation = detectedRegion || '';

    // 3. Résoudre le Stade perçu
    let rawStadePercu = detectedStage;
    if (answers.confirmation_stade === 'non') {
      rawStadePercu = answers.choix_stade;
    }
    if (!rawStadePercu) rawStadePercu = detectedStage || '';

    const stageMapping = {
      'ideation': 'Ideation',
      'market_validation': 'Market Validation',
      'structuration': 'Structuration',
      'fundraising': 'Fundraising',
      'launch_planning': 'Launch Planning',
      'growth': 'Growth'
    };
    const resolvedStadePercu = stageMapping[rawStadePercu] || rawStadePercu;

    // 4. Données de base
    const payload = {
      nom_entreprise: answers.nom_entreprise || detectedNom || '',
      description_libre: description || answers.description_libre || '',
      secteur: resolvedSector,
      localisation: resolvedLocalisation,
      stade_percu: resolvedStadePercu,
      equipe: answers.equipe || null
    };

    // 5. Ajout des champs spécifiques aux secteurs
    if (rawSecteur === 'industrie') {
      payload.indus_equipements = answers.indus_equipements || null;
      payload.indus_iso = answers.indus_iso || null;
      payload.indus_foprodi = answers.indus_foprodi ? (answers.indus_foprodi === 'oui') : null;
      payload.indus_sous_traitance = answers.indus_donneurs_ordre === 'contrats_formels' ? 'formels' :
        answers.indus_donneurs_ordre === 'informellement' ? 'informels' :
          answers.indus_donneurs_ordre === 'non' ? 'aucun' : null;
    } else if (rawSecteur === 'agriculture') {
      payload.agri_certifications_sanitaires = answers.agri_certifications ? (answers.agri_certifications === 'oui') : null;
      payload.agri_chaine_froid = answers.agri_chaine_froid ? (answers.agri_chaine_froid === 'oui') : null;
      payload.agri_saisonnalite = answers.agri_saisonnalite || null;
      payload.agri_acces_foncier = answers.agri_foncier || null;
    } else if (rawSecteur === 'commerce') {
      payload.com_reseau_distribution = answers.com_distribution || null;
      payload.com_parc_vehicules = answers.com_transport || null;
      payload.com_digital = answers.com_digital || null;
      payload.com_stock = answers.com_stock || null;
    } else if (rawSecteur === 'service') {
      payload.service_classement = answers.serv_classement || null;
      payload.service_fidelisation = answers.serv_fidelisation || null;
      payload.service_numerisation = answers.serv_numerique || null;
      payload.service_saisonnalite = answers.serv_saisonnalite || null;
    } else if (rawSecteur === 'technologie') {
      payload.tech_mvp = answers.tech_mvp || null;
      payload.tech_mrr = answers.tech_mrr || null;
      payload.tech_ip = answers.tech_propriete_intellectuelle ? (answers.tech_propriete_intellectuelle === 'oui') : null;
      payload.tech_scalabilite = answers.tech_scalabilite || null;
    }

    // 6. Ajout des champs généraux
    payload.rne = answers.rne ? (answers.rne === 'oui') : null;
    payload.forme_juridique = payload.rne ? (answers.forme_juridique || null) : null;
    payload.a_revenus = answers.revenus ? (answers.revenus === 'oui') : null;
    payload.chiffre_affaires = payload.a_revenus ? (Number(answers.chiffre_affaires) || null) : null;
    payload.anciennete_revenus = payload.a_revenus ? (answers.duree_revenus || null) : null;
    payload.a_clients_payants = !payload.a_revenus && answers.clients_payants ? (answers.clients_payants === 'oui') : null;
    payload.lettres_intention = !payload.a_revenus && payload.a_clients_payants && answers.lettres_intention ? (answers.lettres_intention === 'oui') : null;
    payload.validation_type = !payload.a_revenus && !payload.a_clients_payants && answers.validation_idee ? answers.validation_idee : null;
    payload.business_plan = answers.business_plan || null;
    payload.innovation = answers.innovation || null;
    payload.accompagnement = answers.accompagnement || null;
    payload.financement = answers.financement_externe || null;

    // 7. Mapping des réponses F2
    const f2QuestionsMapping = {
      mkt_cible: {
        key: 'type_cible',
        options: {
          b2c: { index: 0, valeur: 'B2C' },
          b2b_pme: { index: 1, valeur: 'B2B_SME' },
          b2b_grands_comptes: { index: 2, valeur: 'B2B_Enterprise' },
          b2b2c: { index: 3, valeur: 'B2B2C' },
          b2g: { index: 4, valeur: 'B2G' }
        }
      },
      mkt_som: {
        key: 'potentiel_financier_marche',
        options: {
          moins_1m: { index: 0, valeur: 'niche_locale' },
          '1m_5m': { index: 1, valeur: 'marche_regional_limite' },
          '5m_20m': { index: 2, valeur: 'marche_national_intermediaire' },
          '20m_50m': { index: 3, valeur: 'marche_national_majeur' },
          plus_50m: { index: 4, valeur: 'marche_international' }
        }
      },
      mkt_concurrence: {
        key: 'intensite_concurrence',
        options: {
          sature: { index: 0, valeur: 'monopole_oligopole' },
          acteurs_finances: { index: 1, valeur: 'concurrence_severe' },
          moderee: { index: 2, valeur: 'marche_partage' },
          emergent: { index: 3, valeur: 'concurrence_faible' },
          pionnier: { index: 4, valeur: 'absence_concurrence' }
        }
      },
      mkt_traction: {
        key: 'niveau_traction',
        options: {
          zero_utilisateur: { index: 0, valeur: 'ideation_zero_traction' },
          beta_testeurs: { index: 1, valeur: 'interet_sans_revenu' },
          premieres_transactions: { index: 2, valeur: 'traction_initiale' },
          portefeuille_croissance: { index: 3, valeur: 'traction_forte' },
          mrr_stable: { index: 4, valeur: 'croissance_exponentielle' }
        }
      },
      mkt_monetisation: {
        key: 'modele_revenu',
        options: {
          flou: { index: 0, valeur: 'non_defini' },
          one_shot: { index: 1, valeur: 'one_shot_vente_directe' },
          transaction: { index: 2, valeur: 'commission_marketplace' },
          recurrent: { index: 3, valeur: 'abonnement_saas' },
          hybride: { index: 4, valeur: 'usage_freemium' }
        }
      },
      com_modelisation: {
        key: 'business_plan_f2',
        options: {
          aucun: { index: 0, valeur: 'non_existant' },
          basique: { index: 1, valeur: 'brouillon_incomplet' },
          bmc_complet: { index: 2, valeur: 'en_cours_de_validation' },
          valide_mentors: { index: 3, valeur: 'valide_equipe' },
          audite_investisseurs: { index: 4, valeur: 'valide_externe' }
        }
      },
      com_maturite_tech: {
        key: 'maturite_produit',
        options: {
          maquettes: { index: 0, valeur: 'maquette_papier_wireframe' },
          prototype: { index: 1, valeur: 'prototype_dysfonctionnel' },
          mvp: { index: 2, valeur: 'mvp_valide' },
          produit_fini: { index: 3, valeur: 'produit_commercialisable' },
          disponible_international: { index: 4, valeur: 'produit_internationalise' }
        }
      },
      com_pricing: {
        key: 'strategie_prix',
        options: {
          intuitif: { index: 0, valeur: 'prix_intuitif_arbitraire' },
          cout_marge: { index: 1, valeur: 'cout_plus_marge' },
          calque_concurrents: { index: 2, valeur: 'alignement_concurrence' },
          roi_client: { index: 3, valeur: 'valeur_percue' },
          optimise: { index: 4, valeur: 'tarification_dynamique' }
        }
      },
      com_pain_point: {
        key: 'alignement_besoins',
        options: {
          inexistant: { index: 0, valeur: 'nice_to_have_faible' },
          confort: { index: 1, valeur: 'important_non_urgent' },
          reel_differe: { index: 2, valeur: 'critique_non_bloquant' },
          critique: { index: 3, valeur: 'must_have_urgent' },
          pmf: { index: 4, valeur: 'douleur_extreme' }
        }
      },
      ino_originalite: {
        key: 'nouveaute_locale',
        options: {
          replication: { index: 0, valeur: 'copie_conforme' },
          option_plus: { index: 1, valeur: 'amelioration_incrementale' },
          importation: { index: 2, valeur: 'adaptation_locale' },
          inedit_pays: { index: 3, valeur: 'nouveaute_nationale' },
          rupture_internationale: { index: 4, valeur: 'nouveaute_internationale' }
        }
      },
      ino_technologie: {
        key: 'intensite_tech',
        options: {
          assemblage: { index: 0, valeur: 'technologie_standard' },
          app_standard: { index: 1, valeur: 'developpement_specifique' },
          cloud_api: { index: 2, valeur: 'integration_avancee' },
          ia_data: { index: 3, valeur: 'ia_proprietaire' },
          deeptech: { index: 4, valeur: 'deeptech_recherche' }
        }
      },
      ino_barriere: {
        key: 'barrieres_entree',
        options: {
          copiable: { index: 0, valeur: 'sans_barriere' },
          execution: { index: 1, valeur: 'vitesse_execution' },
          exclusivites: { index: 2, valeur: 'moat_commercial' },
          reseau: { index: 3, valeur: 'effet_de_reseau' },
          brevet: { index: 4, valeur: 'barriere_technologique' }
        }
      },
      ino_disruption: {
        key: 'degre_rupture',
        options: {
          aucun_changement: { index: 0, valeur: 'digitalisation_basique' },
          gain_marginal: { index: 1, valeur: 'optimisation_standard' },
          modification_visible: { index: 2, valeur: 'transformation_process' },
          obsolescence: { index: 3, valeur: 'disruption_marche' },
          nouvel_usage: { index: 4, valeur: 'creation_de_marche' }
        }
      },
      sca_deploiement: {
        key: 'replicabilite',
        options: {
          infrastructure_lourde: { index: 0, valeur: 'physique_non_replicable' },
          autorisations: { index: 1, valeur: 'physique_difficile' },
          bureau_reduit: { index: 2, valeur: 'deploiement_operationnel_modere' },
          standardise: { index: 3, valeur: 'facilement_replicable' },
          full_digital: { index: 4, valeur: 'deploiement_100_percent_digital' }
        }
      },
      sca_masse_salariale: {
        key: 'independance_manuelle',
        options: {
          lineaire: { index: 0, valeur: 'dependance_totale' },
          humain_central: { index: 1, valeur: 'rendements_degressifs' },
          vagues: { index: 2, valeur: 'paliers_de_croissance' },
          infrastructure: { index: 3, valeur: 'haute_automatisation' },
          automatise: { index: 4, valeur: 'croissance_pure_tech' }
        }
      },
      sca_capex: {
        key: 'couts_deploiement',
        options: {
          millions: { index: 0, valeur: 'intensif_capex' },
          lever_fonds: { index: 1, valeur: 'investissements_lourds' },
          absorbable: { index: 2, valeur: 'besoin_modere' },
          faible: { index: 3, valeur: 'besoin_faible' },
          marginal_nul: { index: 4, valeur: 'cout_marginal_quasi_nul' }
        }
      },
      sca_geographie: {
        key: 'potentiel_geo',
        options: {
          ville: { index: 0, valeur: 'local_uniquement' },
          gouvernorats: { index: 1, valeur: 'regional' },
          national: { index: 2, valeur: 'national' },
          mena: { index: 3, valeur: 'continental_mena' },
          born_global: { index: 4, valeur: 'mondial_born_global' }
        }
      },
      esg_carbone: {
        key: 'climat_air',
        options: {
          fortement_carbone: { index: 0, valeur: 'fort_impact_carbone' },
          efforts_optimisation: { index: 1, valeur: 'effort_d_attenuation' },
          neutre: { index: 2, valeur: 'neutralite_passive' },
          reduction_active: { index: 3, valeur: 'impact_positif_mesurable' },
          captation: { index: 4, valeur: 'impact_negatif_carbone' }
        }
      },
      esg_eau: {
        key: 'donnees_eau_fournies',
        options: {
          non_mesure: { index: 0, valeur: 'consommation_non_suivie' },
          moyennes_floues: { index: 1, valeur: 'estimation_annuelle' },
          releves_manuels: { index: 2, valeur: 'suivi_manuel_partiel' },
          iot_monitoring: { index: 3, valeur: 'suivi_digital_temps_reel' },
          ia_eau: { index: 4, valeur: 'ia_prediction_besoins' }
        }
      },
      esg_sols: {
        key: 'sols_biodiversite',
        options: {
          intrants_chimiques: { index: 0, valeur: 'impact_negatif' },
          aucun_impact: { index: 1, valeur: 'neutralite_sols' },
          pratiques_limitant: { index: 2, valeur: 'preservation_passive' },
          amelioration_mesurable: { index: 3, valeur: 'preservation_active' },
          restauration: { index: 4, valeur: 'impact_regeneratif' }
        }
      },
      esg_dechets: {
        key: 'ressources_dechets',
        options: {
          extraire_jeter: { index: 0, valeur: 'decharges_non_triees' },
          tri_basique: { index: 1, valeur: 'reduction_a_la_source' },
          reduction_amont: { index: 2, valeur: 'tri_et_recyclage' },
          valorisation: { index: 3, valeur: 'revalorisation_upcycling' },
          zero_dechet: { index: 4, valeur: 'economie_circulaire' }
        }
      }
    };

    payload.reponses_f2 = {};
    Object.keys(f2QuestionsMapping).forEach(qId => {
      const mapping = f2QuestionsMapping[qId];
      const answerVal = answers[qId];
      if (answerVal && mapping.options[answerVal]) {
        payload.reponses_f2[mapping.key] = mapping.options[answerVal];
      }
    });

    setSaving(true);
    try {
      const token = localStorage.getItem('token');
      const projectId = localStorage.getItem('project_id') || 1;

      const response = await fetch(`http://localhost:8000/projects/${projectId}/analyse`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const data = await response.json();

        // 🟢 C'EST ICI QU'IL FAUT AJOUTER LA LIGNE SUIVANTE :
        if (data.project_id) {
          localStorage.setItem('project_id', data.project_id);
        }

        const resObj = data.f1_diagnostic;
        if (resObj) {
          setStadeReel(resObj.stade_reel || '');
          setStadePercu(resObj.stade_percu || '');
          setDivergenceExplication(resObj.gap_explication || '');
        }
        setSavedIndicator(true);
        setTimeout(() => setSavedIndicator(false), 2000);

        // Rediriger vers le dashboard après succès
        navigate('/');
      } else {
        const errData = await response.json().catch(() => ({}));
        alert("Erreur lors de l'analyse : " + (errData.detail || response.statusText));
      }
    } catch (err) {
      console.error("Erreur lors de la validation du diagnostic:", err);
      alert("Erreur serveur lors de l'analyse.");
    } finally {
      setSaving(false);
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
                  className={`flex items-center gap-2 px-3 py-2 rounded-xl text-[10px] font-extrabold tracking-wide uppercase transition-all whitespace-nowrap cursor-pointer ${isCurrent
                    ? 'bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 shadow-sm shadow-cyan-950/20'
                    : isPast
                      ? 'text-emerald-400 hover:text-emerald-300'
                      : 'text-slate-500 hover:text-slate-400'
                    }`}
                >
                  <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] ${isCurrent
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
                className={`glass-card p-6 flex flex-col gap-4 border transition-all ${isCompleted
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
                            className={`p-3.5 text-xs font-semibold rounded-xl text-left rtl:text-right border-2 transition-all flex items-center gap-3 cursor-pointer ${isSelected
                              ? 'border-cyan-500 bg-cyan-950/20 text-cyan-300'
                              : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 text-slate-400 hover:text-slate-200'
                              }`}
                          >
                            <div className={`w-4 h-4 rounded-full border flex items-center justify-center flex-shrink-0 ${isSelected ? 'border-cyan-400 bg-cyan-950' : 'border-slate-700'
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
                            className={`p-3.5 text-xs font-semibold rounded-xl text-left rtl:text-right border-2 transition-all flex items-center gap-3 cursor-pointer ${isSelected
                              ? 'border-cyan-500 bg-cyan-950/20 text-cyan-300'
                              : 'border-slate-800 hover:border-slate-700 bg-slate-900/40 text-slate-400 hover:text-slate-200'
                              }`}
                          >
                            <div className={`w-4 h-4 rounded border flex items-center justify-center flex-shrink-0 ${isSelected ? 'border-cyan-400 bg-cyan-400' : 'border-slate-700'
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
          className={`px-5 py-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 border transition-all cursor-pointer ${currentStepIndex === 0
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
          <div className="flex flex-col sm:flex-row items-center justify-end w-full gap-3">
            <button
              type="button"
              onClick={handleAnalyzeProject}
              disabled={saving}
              className="w-full sm:w-auto px-5 py-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-lg shadow-cyan-500/10 cursor-pointer disabled:opacity-50"
            >
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileText className="h-4 w-4" />}
              {saving ? pt.saving : pt.exportBtn}
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
