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
    localisation
  } = rawData;

  // Detect conditions from raw data
  const hasLegalBlocker = blockers.some(b => b.domaine.toLowerCase() === 'légal');
  const hasMarketBlocker = blockers.some(b => b.domaine.toLowerCase() === 'marché');
  const hasNoRNE = gaps.includes("Pas de RNE enregistré");
  const hasNoBP = gaps.includes("Pas de business plan documenté");
  const hasNoClients = gaps.includes("Zéro client payant");

  // Calculate scores based on actual data from JSON
  const marketScore = hasMarketBlocker ? 45 : 80;
  const commercialScore = hasNoClients ? 20 : 75;
  const innovationScore = 80;
  const scalabilityScore = hasNoBP ? 35 : 70;
  const greenScore = 60;

  const baseAvg = Math.round((marketScore + commercialScore + innovationScore + scalabilityScore + greenScore) / 5);
  const financingScore = gap_detecte ? Math.min(baseAvg, 42) : Math.max(baseAvg, 78);

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
    scores: [
      {
        id: "market",
        title: { fr: "Market (Marché)", ar: "السوق" },
        score: marketScore,
        color: "cyan",
        description: { fr: "Analyse de la demande et adéquation marché.", ar: "تحليل الطلب وملاءمة المنتج للسوق." },
        subDimensions: [
          {
            name: { fr: "Validation Client", ar: "التحقق من العميل" },
            score: marketScore,
            justification: {
              fr: hasMarketBlocker ? "Validation client insuffisante - besoin d'études de terrain supplémentaires." : "Validation client satisfaisante.",
              ar: hasMarketBlocker ? "التحقق من صحة العملاء غير كافٍ - بحاجة لدراسات ميدانية إضافية." : "التحقق من صحة العملاء كافٍ ومكتمل."
            }
          },
          {
            name: { fr: "Opportunité Locale", ar: "الفرصة المحلية" },
            score: 85,
            justification: {
              fr: `Opportunité forte détectée dans la zone de ${localisation} pour le secteur ${secteur}.`,
              ar: `تم رصد فرصة قوية في منطقة ${translateValue(localisation, 'ar')} لقطاع ${translateValue(secteur, 'ar')}.`
            }
          }
        ]
      },
      {
        id: "commercial",
        title: { fr: "Commercial", ar: "التجاري" },
        score: commercialScore,
        color: "indigo",
        description: { fr: "Traction client et tunnel de conversion.", ar: "جذب العملاء ومسار تحويل المبيعات." },
        subDimensions: [
          {
            name: { fr: "Ventes et Traction", ar: "المبيعات والجاذبية" },
            score: commercialScore,
            justification: {
              fr: hasNoClients ? "Aucune vente enregistrée à ce jour (Zéro client payant)." : "Premières ventes encourageantes.",
              ar: hasNoClients ? "لم يتم تسجيل أي مبيعات حتى اليوم (عملاء دافعون: 0)." : "مبيعات أولية مشجعة."
            }
          }
        ]
      },
      {
        id: "innovation",
        title: { fr: "Innovation", ar: "الابتكار" },
        score: innovationScore,
        color: "violet",
        description: { fr: "Avantage produit et barrières concurrentielles.", ar: "ميزة المنتج والحواجز التنافسية." },
        subDimensions: [
          {
            name: { fr: "Différenciation Produit", ar: "تميز المنتج" },
            score: innovationScore,
            justification: {
              fr: "Concept innovant offrant une bonne valeur ajoutée.",
              ar: "مفهوم مبتكر يقدم قيمة مضافة جيدة."
            }
          }
        ]
      },
      {
        id: "scalability",
        title: { fr: "Scalabilité", ar: "القدرة على التوسع" },
        score: scalabilityScore,
        color: "amber",
        description: { fr: "Potentiel d'automatisation et modèle récurrent.", ar: "إمكانية الأتمتة والنموذج المتكرر للربح." },
        subDimensions: [
          {
            name: { fr: "Planification Opérationnelle", ar: "التخطيط التشغيلي" },
            score: scalabilityScore,
            justification: {
              fr: hasNoBP ? "Manque de business plan documenté pour structurer la mise à l'échelle." : "Plan d'affaires documenté et cohérent.",
              ar: hasNoBP ? "غياب مخطط عمل موثق يمنع هيكلة وتوسيع نطاق المشروع." : "خطة عمل موثقة ومتسقة."
            }
          }
        ]
      },
      {
        id: "green",
        title: { fr: "Impact Vert (Green)", ar: "الأثر البيئي" },
        score: greenScore,
        color: "emerald",
        description: { fr: "Bilan carbone et circularité des ressources.", ar: "بصمة الكربون ودائرية الموارد." },
        subDimensions: [
          {
            name: { fr: "Empreinte Écologique", ar: "الأثر البيئي" },
            score: greenScore,
            justification: {
              fr: `Valorisation des produits locaux de ${localisation} en circuit court.`,
              ar: `تثمين المنتجات المحلية ل${translateValue(localisation, 'ar')} في إطار توزيع قصير المدى.`
            }
          }
        ]
      }
    ],
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
