import rawData from './dashboard.json';

// Translation dictionaries for raw JSON string values
export const valueTranslations = {
  fr: {
    "agri-food": "Agroalimentaire",
    "Sfax": "Sfax",
    "Ideation": "Idéation",
    "Validation": "Validation",
    "Structuration": "Structuration",
    "Fundraising": "Levée de fonds",
    "Launch": "Lancement",
    "Growth": "Croissance",
    "légal": "Légal",
    "marché": "Marché",
    "financier": "Financier",
    "technique": "Technique",
    "Pas de RNE enregistré": "Pas de RNE enregistré",
    "Pas de business plan documenté": "Pas de business plan documenté",
    "Zéro client payant": "Zéro client payant",
    "L'entrepreneur se croit prêt pour financement mais n'a pas de structure juridique enregistrée": "L'entrepreneur se croit prêt pour le financement mais n'a pas de structure juridique enregistrée.",
    "Entreprise non enregistrée": "Entreprise non enregistrée",
    "Validation client insuffisante": "Validation client insuffisante"
  },
  ar: {
    "agri-food": "الصناعات الغذائية",
    "Sfax": "صفاقس",
    "Ideation": "فكرة",
    "Validation": "تحقق",
    "Structuration": "هيكلة",
    "Fundraising": "جمع تمويل",
    "Launch": "إطلاق",
    "Growth": "نمو",
    "légal": "قانوني",
    "marché": "السوق",
    "financier": "مالي",
    "technique": "تقني",
    "Pas de RNE enregistré": "السجل الوطني للمؤسسات (RNE) غير مسجل",
    "Pas de business plan documenté": "مخطط العمل غير موثق",
    "Zéro client payant": "لا يوجد عملاء دافعين",
    "L'entrepreneur se croit prêt pour financement mais n'a pas de structure juridique enregistrée": "يعتقد رائد الأعمال أنه جاهز للتمويل ولكنه لا يملك هيكلاً قانونياً مسجلاً.",
    "Entreprise non enregistrée": "الشركة غير مسجلة قانونياً",
    "Validation client insuffisante": "التحقق من صحة العملاء غير كافٍ"
  }
};

export function translateValue(value, lang) {
  if (!value) return "";
  return valueTranslations[lang]?.[value] || value;
}

// ─── Scores du Membre 2 (simulés) ──────────────────────────────────────────
const member2Scores = {
  market_score:           { valeur: 42.0, sous_scores: { taille_marche: 30.0, concurrence: 40.0, validation_client: 50.0, modele_revenus: 48.0 } },
  commercial_offer_score: { valeur: 58.0, sous_scores: { proposition_valeur: 60.0, maturite_produit: 50.0, strategie_prix: 60.0, alignement_besoins: 62.0 } },
  innovation_score:       { valeur: 78.0, sous_scores: { nouveaute_locale: 80.0, intensite_tech: 75.0, barrieres_entree: 80.0, degre_rupture: 77.0 } },
  scalability_score:      { valeur: 82.0, sous_scores: { replicabilite: 85.0, independance_manuelle: 80.0, couts_deploiement: 82.0, potentiel_geo: 81.0 } },
  green_score:            { valeur: 75.0, sous_scores: { climat_air: 80.0, eau: 70.0, sols_biodiversite: 75.0, ressources_dechets: 75.0 } }
};

// ─── Métadonnées bilingues des dimensions ───────────────────────────────────
const DIMENSION_CONFIG = [
  {
    id: 'market',
    jsonKey: 'market_score',
    color: 'cyan',
    title:       { fr: 'Marché',              ar: 'السوق' },
    description: { fr: 'Analyse de la demande et adéquation marché.', ar: 'تحليل الطلب وملاءمة المنتج للسوق.' },
    subLabels: {
      taille_marche:     { fr: 'Taille du marché',   ar: 'حجم السوق' },
      concurrence:       { fr: 'Concurrence',         ar: 'المنافسة' },
      validation_client: { fr: 'Validation client',   ar: 'التحقق من العملاء' },
      modele_revenus:    { fr: 'Modèle de revenus',   ar: 'نموذج الإيرادات' }
    }
  },
  {
    id: 'commercial',
    jsonKey: 'commercial_offer_score',
    color: 'indigo',
    title:       { fr: 'Commercial',          ar: 'العرض التجاري' },
    description: { fr: 'Traction client et tunnel de conversion.', ar: 'جذب العملاء ومسار تحويل المبيعات.' },
    subLabels: {
      proposition_valeur:  { fr: 'Proposition de valeur',        ar: 'مقترح القيمة' },
      maturite_produit:    { fr: 'Maturité du produit',          ar: 'نضج المنتج' },
      strategie_prix:      { fr: 'Stratégie de prix',            ar: 'استراتيجية التسعير' },
      alignement_besoins:  { fr: 'Alignement avec les besoins',  ar: 'الملاءمة مع الاحتياجات' }
    }
  },
  {
    id: 'innovation',
    jsonKey: 'innovation_score',
    color: 'violet',
    title:       { fr: 'Innovation',          ar: 'الابتكار' },
    description: { fr: 'Avantage produit et barrières concurrentielles.', ar: 'ميزة المنتج والحواجز التنافسية.' },
    subLabels: {
      nouveaute_locale:  { fr: 'Nouveauté locale',          ar: 'الابتكار المحلي' },
      intensite_tech:    { fr: 'Intensité technologique',   ar: 'الكثافة التكنولوجية' },
      barrieres_entree:  { fr: "Barrières à l'entrée",      ar: 'حواجز الدخول' },
      degre_rupture:     { fr: 'Degré de rupture',          ar: 'درجة القطيعة' }
    }
  },
  {
    id: 'scalability',
    jsonKey: 'scalability_score',
    color: 'amber',
    title:       { fr: 'Scalabilité',         ar: 'القابلية للتوسع' },
    description: { fr: "Potentiel d'automatisation et modèle récurrent.", ar: 'إمكانية الأتمتة والنموذج المتكرر.' },
    subLabels: {
      replicabilite:          { fr: 'Réplicabilité',               ar: 'قابلية التكرار' },
      independance_manuelle:  { fr: 'Indépendance manuelle',       ar: 'الاستقلالية عن العمل اليدوي' },
      couts_deploiement:      { fr: 'Coûts de déploiement',        ar: 'تكاليف النشر' },
      potentiel_geo:          { fr: 'Potentiel géographique',      ar: 'الإمكانية الجغرافية' }
    }
  },
  {
    id: 'green',
    jsonKey: 'green_score',
    color: 'emerald',
    title:       { fr: 'Green',               ar: 'الاستدامة البيئية' },
    description: { fr: 'Bilan carbone et circularité des ressources.', ar: 'بصمة الكربون ودائرية الموارد.' },
    subLabels: {
      climat_air:         { fr: 'Climat & Air',        ar: 'المناخ والهواء' },
      eau:                { fr: "Gestion de l'eau",    ar: 'إدارة المياه' },
      sols_biodiversite:  { fr: 'Sols & Biodiversité', ar: 'التربة والتنوع البيولوجي' },
      ressources_dechets: { fr: 'Ressources & Déchets', ar: 'الموارد والنفايات' }
    }
  }
];

// ─── Fusion Membre1 + Membre2 (moyenne simple) ──────────────────────────────
function buildMergedScores(rawScores) {
  return DIMENSION_CONFIG.map((dim) => {
    const m1 = rawScores?.[dim.jsonKey] || { valeur: 0, sous_scores: {}, justification_template: '' };
    const m2 = member2Scores[dim.jsonKey] || { valeur: 0, sous_scores: {} };

    const mergedValeur = Math.round(((m1.valeur + m2.valeur) / 2) * 10) / 10;

    const subDimensions = Object.keys(dim.subLabels).map((subKey) => {
      const v1 = m1.sous_scores?.[subKey] ?? 0;
      const v2 = m2.sous_scores?.[subKey] ?? 0;
      const mergedSub = Math.round(((v1 + v2) / 2) * 10) / 10;
      return {
        key: subKey,
        name: dim.subLabels[subKey],
        score: mergedSub,
        m1Score: v1,
        m2Score: v2
      };
    });

    // Justification dynamique bilingue basée sur les scores fusionnés
    const justification = buildJustification(dim.id, mergedValeur, subDimensions, m1.justification_template);

    return {
      id: dim.id,
      title: dim.title,
      score: mergedValeur,
      color: dim.color,
      description: dim.description,
      justification,
      subDimensions
    };
  });
}

function buildJustification(dimId, mergedValeur, subDimensions, originalTemplate) {
  const worstSub = subDimensions.reduce((a, b) => (a.score < b.score ? a : b), subDimensions[0]);

  const templates = {
    market: {
      fr: `Score Marché fusionné : ${mergedValeur}/100. Le sous-score '${worstSub?.name?.fr}' (${worstSub?.score}/100) est le point le plus faible — bloqueur potentiel pour le financement.`,
      ar: `درجة السوق المدمجة: ${mergedValeur}/100. المعيار الأضعف هو '${worstSub?.name?.ar}' (${worstSub?.score}/100) — قد يكون عائقاً أمام التمويل.`
    },
    commercial: {
      fr: `Score Commercial fusionné : ${mergedValeur}/100. Le sous-score '${worstSub?.name?.fr}' (${worstSub?.score}/100) nécessite une attention prioritaire avant toute approche investisseur.`,
      ar: `درجة العرض التجاري المدمجة: ${mergedValeur}/100. المعيار '${worstSub?.name?.ar}' (${worstSub?.score}/100) يستوجب الأولوية قبل التواصل مع أي مستثمر.`
    },
    innovation: {
      fr: `Score Innovation fusionné : ${mergedValeur}/100. Le profil innovant est reconnu. '${worstSub?.name?.fr}' (${worstSub?.score}/100) peut encore être consolidé.`,
      ar: `درجة الابتكار المدمجة: ${mergedValeur}/100. الملف الابتكاري معترف به. '${worstSub?.name?.ar}' (${worstSub?.score}/100) يمكن تعزيزه أكثر.`
    },
    scalability: {
      fr: `Score Scalabilité fusionné : ${mergedValeur}/100. Le modèle est scalable. '${worstSub?.name?.fr}' (${worstSub?.score}/100) est le levier à optimiser en priorité.`,
      ar: `درجة القابلية للتوسع المدمجة: ${mergedValeur}/100. النموذج قابل للتوسع. '${worstSub?.name?.ar}' (${worstSub?.score}/100) هو الرافعة الأولى للتحسين.`
    },
    green: {
      fr: `Score Green fusionné : ${mergedValeur}/100. L'impact environnemental est maîtrisé. '${worstSub?.name?.fr}' (${worstSub?.score}/100) est le pilier à renforcer.`,
      ar: `درجة الاستدامة المدمجة: ${mergedValeur}/100. الأثر البيئي تحت السيطرة. '${worstSub?.name?.ar}' (${worstSub?.score}/100) هو الركيزة التي تحتاج تعزيزاً.`
    }
  };

  return templates[dimId] || { fr: originalTemplate || '', ar: originalTemplate || '' };
}

export function getAdaptedData() {
  const {
    entrepreneur_id,
    stade_reel,
    stade_percu,
    gap_detecte,
    gap_explication,
    gaps,
    blockers,
    secteur,
    localisation,
    scores: rawScores
  } = rawData;

  // Detect conditions from raw data
  const hasLegalBlocker = blockers.some(b => b.domaine.toLowerCase() === 'légal');
  const hasMarketBlocker = blockers.some(b => b.domaine.toLowerCase() === 'marché');
  const hasNoRNE = gaps.includes("Pas de RNE enregistré");
  const hasNoBP = gaps.includes("Pas de business plan documenté");
  const hasNoClients = gaps.includes("Zéro client payant");

  // Build merged scores from dashboard.json + member 2
  const mergedScores = buildMergedScores(rawScores);

  // Financing score based on merged scores average
  const avgMerged = Math.round(mergedScores.reduce((sum, s) => sum + s.score, 0) / mergedScores.length);
  const financingScore = gap_detecte ? Math.min(avgMerged, 42) : Math.max(avgMerged, 78);

  // Build adapted data from raw JSON
  const adapted = {
    startupName: `${entrepreneur_id}`,
    entrepreneur_id,
    secteur,
    localisation,
    maturity: {
      perceivedStage: stade_percu,
      realStage: stade_reel,
      stages: [
        {
          id: "Ideation",
          label: { fr: "Idéation", ar: "فكرة" },
          desc: { fr: "Définition du concept et étude de marché initiale.", ar: "تحديد المفهوم ودراسة السوق الأولية." }
        },
        {
          id: "Validation",
          label: { fr: "Validation", ar: "التحقق" },
          desc: { fr: "Création d'un MVP et premiers tests utilisateurs.", ar: "إنشاء نموذج أولى واختبار المستخدمين." }
        },
        {
          id: "Structuration",
          label: { fr: "Structuration", ar: "الهيكلة" },
          desc: { fr: "Enregistrement légal, constitution de l'équipe et modélisation.", ar: "التسجيل القانوني، تكوين الفريق وصياغة النموذج." }
        },
        {
          id: "Fundraising",
          label: { fr: "Levée de fonds", ar: "جمع التمويل" },
          desc: { fr: "Pitching, due diligence, recherche de capital.", ar: "تقديم العروض، فحص الجدوى والبحث عن رأس المال." }
        },
        {
          id: "Launch",
          label: { fr: "Lancement", ar: "الإطلاق" },
          desc: { fr: "Début de la commercialisation et acquisition active.", ar: "بدء التسويق التجاري والاستقطاب النشط." }
        },
        {
          id: "Growth",
          label: { fr: "Croissance", ar: "النمو" },
          desc: { fr: "Passage à l'échelle, expansion géographique.", ar: "التوسع والنمو والتمدد الجغرافي." }
        }
      ],
      alertMessage: {
        fr: gap_explication,
        ar: translateValue(gap_explication, 'ar')
      },
      gapsList: gaps
    },
    scores: mergedScores,
    financingReadiness: {
      score: financingScore,
      status: financingScore >= 75 ? 'bankable' : 'non_bankable',
      statusLabel: {
        fr: financingScore >= 75 ? "Bancable (Éligible)" : "Non bancable (À consolider)",
        ar: financingScore >= 75 ? "جاهز للتمويل (مؤهل)" : "غير جاهز للتمويل (بحاجة لتعزيز)"
      },
      description: {
        fr: gap_explication,
        ar: translateValue(gap_explication, 'ar')
      }
    },
    blockers: blockers.map((b, idx) => ({
      id: `bl-${idx}`,
      domain: {
        fr: b.domaine.charAt(0).toUpperCase() + b.domaine.slice(1),
        ar: translateValue(b.domaine, 'ar')
      },
      priority: b.priorite === 1 ? 'high' : b.priorite === 2 ? 'medium' : 'low',
      title: {
        fr: b.description,
        ar: translateValue(b.description, 'ar')
      },
      desc: {
        fr: `Bloqueur identifié dans le domaine : ${b.domaine}. Niveau de priorité : ${b.priorite}.`,
        ar: `عقبة محددة في مجال: ${translateValue(b.domaine, 'ar')}. مستوى الأولوية: ${b.priorite}.`
      }
    })),
    roadmap: [
      {
        horizon: "immediate",
        title: { fr: "Immédiat (0 - 3 mois)", ar: "فوري (0 - 3 أشهر)" },
        actions: [
          ...(hasNoRNE ? [{
            text: { fr: "Enregistrer la structure au RNE (Registre National des Entreprises)", ar: "تسجيل الشركة في السجل الوطني للمؤسسات (RNE)" },
            completed: false
          }] : []),
          ...(hasMarketBlocker ? [{
            text: { fr: "Mener des actions de validation client sur le terrain", ar: "إجراء مقابلات التحقق من صحة العملاء في الميدان" },
            completed: false
          }] : []),
          {
            text: { fr: "Corriger l'écart identifié par la divergence perçu/réel", ar: "تصحيح الفجوة المحددة بالاختلاف المدرك/الحقيقي" },
            completed: false
          }
        ]
      },
      {
        horizon: "shortTerm",
        title: { fr: "Court terme (3 - 6 mois)", ar: "المدى القريب (3 - 6 أشهر)" },
        actions: [
          ...(hasNoBP ? [{
            text: { fr: "Rédiger et finaliser le Business Plan financier", ar: "إعداد وصياغة مخطط العمل المالي النهائي" },
            completed: false
          }] : []),
          ...(hasNoClients ? [{
            text: { fr: "Lancer les premières offres de test et acquérir les premiers clients payants", ar: "إطلاق العروض التجريبية الأولى وكسب أول عملاء دافعين" },
            completed: false
          }] : [])
        ]
      },
      {
        horizon: "mediumTerm",
        title: { fr: "Moyen terme (6 - 12 mois)", ar: "المدى المتوسط (6 - 12 شهراً)" },
        actions: [
          {
            text: { fr: `Développer le réseau commercial régional à ${localisation}`, ar: `توسيع الشبكة التجارية الإقليمية في ${translateValue(localisation, 'ar')}` },
            completed: false
          },
          {
            text: { fr: "Préparer la documentation complète pour solliciter un financement bancaire", ar: "تجهيز الملف الكامل لطلب التمويل البنكي" },
            completed: false
          }
        ]
      }
    ]
  };

  return adapted;
}
