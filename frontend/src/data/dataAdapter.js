
 
// Translation dictionaries for raw JSON string values
export const valueTranslations = {
  fr: {
    // Sectors & Locations
    "Industrie/Construction": "Industrie/Construction",
    "Industrie / Construction": "Industrie / Construction",
    "Sfax": "Sfax",
    "Sfax, Tunisie": "Sfax, Tunisie",
 
    // Stages
    "Ideation": "Idéation",
    "Market Validation": "Validation",
    "Structuration": "Structuration",
    "Fundraising": "Levée de fonds",
    "Launch Planning": "Lancement",
    "Growth": "Croissance",
 
    // Resource Types
    "financement_bancaire": "Financement bancaire",
    "concours_financement": "Concours & Financement",
    "subvention": "Subvention",
    "programme_accompagnement": "Programme d'accompagnement",
    "cadre_legal_avantages": "Cadre légal & Avantages",
    "accompagnement_incubation": "Accompagnement & Incubation",
    "accompagnement_conseil": "Accompagnement & Conseil",
    "garantie_credit": "Garantie de crédit",
    "subvention_investissement": "Subvention d'investissement",
    "capital_investissement": "Capital investissement",
    "business_angels": "Business Angels",
    "garantie": "Garantie",
    "acceleration_investissement": "Accélération & Investissement",
    "subvention_recherche": "Subvention de recherche (R&D)",
    "subvention_formation": "Subvention de formation",
    "pret_participatif": "Prêt participatif",
    "label_accreditation": "Label & Accréditation",
    "subvention_incitation": "Subvention & Incitation",
  },
  ar: {
    // Sectors & Locations
    "Industrie/Construction": "الصناعة / البناء",
    "Industrie / Construction": "الصناعة / البناء",
    "Sfax": "صفاقس",
    "Sfax, Tunisie": "صفاقس، تونس",
 
    // Stages
    "Ideation": "فكرة",
    "Market Validation": "تحقق",
    "Structuration": "هيكلة",
    "Fundraising": "جمع تمويل",
    "Launch Planning": "إطلاق",
    "Growth": "نمو",
 
    // Mismatch Gap Message
    "⚠️ DIVERGENCE DÉTECTÉE — Vous pensez être en 'Growth' → stade réel: 'Structuration'.\n  L'entrepreneur a surestimé son stade de 3 niveau(x). Il se perçoit en 'Growth' mais le diagnostic objectif indique 'Structuration'. Causes principales : Fondateur seul — équipe à constituer, Absence de certification ISO sur les chantiers, Absence de RNE (entité juridique non créée).": "⚠️ تم الكشف عن تباين — تعتقد أنك في مرحلة 'النمو' ← المرحلة الفعلية: 'الهيكلة'.\n  لقد بالغ رائد الأعمال في تقدير مرحلته بمقدار 3 مستويات. يرى نفسه في مرحلة 'النمو' ولكن التشخيص الموضوعي يشير إلى 'الهيكلة'. الأسباب الرئيسية: مؤسس بمفرده — يجب تكوين فريق، غياب شهادة ISO في الورشات، غياب السجل الوطني للمؤسسات (الكيان القانوني غير مُنشأ).",
 
    // Divergence signals
    "Vous vous croyez en 'Growth' mais n'avez pas de RNE — impossible de constituer un dossier bancable sans entité juridique.": "تعتقد أنك في مرحلة 'النمو' ولكن ليس لديك سجل وطني للمؤسسات (RNE) — من المستحيل تكوين ملف تمويل بنكي بدون كيان قانوني.",
    "Votre solution existe déjà sur le marché tunisien depuis plusieurs années. L'innovation perçue ne se traduit pas en différenciation réelle.": "حلك موجود بالفعل في السوق التونسية منذ عدة سنوات. الابتكار المتصور لا يترجم إلى تميز حقيقي.",
 
    // Roadmap items
    "[Industrie / Construction] Contacter APII Sfax (FOPRODI) + BFPME (CMLT) pour le dossier de structuration": "[الصناعة / البناء] الاتصال بوكالة النهوض بالصناعة والتجديد بصفاقس (FOPRODI) + البنك التونسي لتمويل المؤسسات الصغرى والمتوسطة (CMLT) لملف الهيكلة",
    "🚨 Sollicitez le bureau régional de l'APII de Sfax pour déposer un dossier de prime d'investissement industriel.": "🚨 اتصل بالمكتب الإقليمي لوكالة النهوض بالصناعة والتجديد (APII) بصفاقس لتقديم ملف منحة الاستثمار الصناعي.",
    "🚨 Recrutez un bras droit opérationnel (chef de chantier/COO) ou ouvrez votre capital pour intégrer un co-fondateur.": "🚨 وظف مساعد عمليات (رئيس ورشة/COO) أو افتح رأس المال لإدماج شريك مؤسس.",
    "Créer société au RNE si pas encore fait": "تأسيس الشركة في السجل الوطني للمؤسسات (RNE) إن لم يتم ذلك بعد",
    "Constituer dossier BFPME (business plan modèle GIZ)": "إعداد ملف البنك التونسي لتمويل المؤسسات الصغرى والمتوسطة BFPME (نموذج مخطط العمل GIZ)",
    "Évaluer apport personnel + éligibilité SOTUGAR": "تقييم المساهمة الشخصية + الأهلية لضمان SOTUGAR",
    "⚠️ FRI=32/100 — Projet non encore bancable. Structuration prioritaire avant dépôt dossier financement.": "⚠️ مؤشر الجاهزية للتمويل FRI = 32/100 — المشروع غير جاهز للتمويل بعد. الهيكلة لها الأولوية قبل إيداع ملف التمويل.",
    "🎯 [Market Score critique] Obtenir 3 lettres d'intention clients payants avant tout dépôt de dossier": "🎯 [درجة سوق حرجة] الحصول على 3 رسائل نية من عملاء دافعين قبل إيداع أي ملف",
    "🎯 [Offre commerciale] Rédiger fiche proposition de valeur (1 page) et tester avec 5 clients réels": "🎯 [العرض التجاري] كتابة ورقة مقترح القيمة (صفحة واحدة) واختبارها مع 5 عملاء حقيقيين",
    "Déposer dossier FOPRODI APII (prime 10% équipements)": "تقديم ملف FOPRODI APII (منحة 10% على المعدات)",
    "Vérifier garantie SOTUGAR": "التحقق من ضمان الشركة التونسية للضمان (SOTUGAR)",
    "Finaliser cofinancement avec banque partenaire": "استكمال التمويل المشترك مع البنك الشريك",
    "Obtenir accord BFPME": "الحصول على موافقة BFPME",
    "Recruter équipe clé (COO / associé)": "توظيف الفريق الرئيسي (COO / شريك)",
    "Mettre en place comptabilité formelle": "إرساء محاسبة قانونية منتظمة",
 
    // Anomalies
    "Risque de Burnout : Gérer seul une entreprise de construction en pleine structuration est un goulot d'étranglement majeur (Key-Man Risk) rédhibitoire pour les investisseurs.": "خطر الاحتراق النفسي: إدارة شركة بناء بمفردك في مرحلة الهيكلة هي عقبة رئيسية (خطر الشخص المفتاح) وغير مقبولة للمستثمرين.",
    "Recrutez un bras droit opérationnel (chef de chantier/COO) ou ouvrez votre capital pour intégrer un co-fondateur.": "وظف مساعد عمليات (رئيس ورشة/COO) أو افتح رأس المال لإدماج شريك مؤسس.",
    "Leviers régionaux inexploités : Vous êtes basé à Sfax mais ne bénéficiez d'aucun financement régional. Vous passez à côté de primes de développement spécifiques au gouvernorat (FOPRODI / APII Sfax).": "الرافعات الإقليمية غير المستغلة: أنت متمركز في صفاقس ولكنك لا تستفيد من أي تمويل إقليمي. تفوتك منح التنمية المخصصة للولاية (FOPRODI / APII صفاقس).",
    "Sollicitez le bureau régional de l'APII de Sfax pour déposer un dossier de prime d'investissement industriel.": "اتصل بالمكتب الإقليمي لوكالة النهوض بالصناعة والتجديد (APII) بصفاقس لتقديم ملف منحة الاستثمار الصناعي.",
 
    // Score justifications & actions
    "Le Market Score est insuffisant (16.3/100). Le critere 'Taille marche' (10/100) constitue un bloqueur majeur pour toute demarche de financement.": "درجة السوق غير كافية (16.3/100). يشكل معيار 'حجم السوق' (10/100) عقبة رئيسية أمام أي عملية تمويل.",
    "ACTION URGENTE : 'Taille marche' doit passer au-dessus de 30/100. Sans cela, aucun financement n'est envisageable.": "إجراء عاجل: يجب أن يتجاوز معيار 'حجم السوق' 30/100. بدون ذلك، لا يمكن النظر في أي تمويل.",
    "L'offre commerciale est trop fragile (40.0/100). La 'Proposition valeur' (40/100) doit etre refondee avant toute approche d'investisseur.": "العرض التجاري هش للغاية (40.0/100). يجب إعادة صياغة 'مقترح القيمة' (40/100) قبل التواصل مع أي مستثمر.",
    "ACTION URGENTE : redefinir 'Proposition valeur' (score 40/100). Engager un atelier job-to-be-done avec de vrais utilisateurs.": "إجراء عاجل: إعادة تحديد 'مقترح القيمة' (درجة 40/100). البدء بورشة عمل 'الوظائف المطلوب إنجازها' (job-to-be-done) مع مستخدمين حقيقيين.",
    "Le profil innovant est reconnu : 'Nouveaute locale' (90/100) positionne favorablement le projet sur son marche.": "الملف الابتكاري معترف به: 'الابتكار المحلي' (90/100) يضع المشروع في مكانة إيجابية في سوقه.",
    "Initier une procedure de depot de brevet (Art. 12 Startup Act) pour securiser les barrieres a l'entree.": "بدء إجراءات تسجيل براءة الاختراع (الفصل 12 من قانون الشركات الناشئة) لتأمين حواجز الدخول.",
    "Le modele est fortement scalable. La 'Replicabilite' (90/100) confirme la capacite de croissance sans augmentation lineaire des couts.": "النموذج قابل للتوسع بشكل كبير. تؤكد 'قابلية التكرار' (90/100) القدرة على النمو دون زيادة خطية في التكاليف.",
    "Modeliser les economies d'echelle a 3 ans pour le dossier de levee de fonds.": "نمذجة وفورات الحجم على مدى 3 سنوات لملف جمع التمويل.",
    "L'impact environnemental est bien maitrise. Le pilier 'Climat air' (90/100) est un atout dans le contexte PNUD/ODD.": "الأثر البيئي تحت السيطرة الجيدة. ركيزة 'المناخ والهواء' (90/100) تعد ميزة في سياق برنامج الأمم المتحدة الإنمائي وأهداف التنمية المستدامة.",
    "Formaliser le bilan carbone et l'aligner sur les ODD pour les dossiers de financement PNUD/AFD.": "إعداد تقرير البصمة الكربونية ومواءمته مع أهداف التنمية المستدامة لملفات تمويل برنامج الأمم المتحدة الإنمائي والوكالة الفرنسية للتنمية.",
 
    // Organisms
    "BFPME": "البنك التونسي لتمويل المؤسسات الصغرى والمتوسطة (BFPME)",
    "AINS 4.0 / PNUD / GEWEET / ODC / IEEE / APII": "AINS 4.0 / برنامج الأمم المتحدة الإنمائي / GEWEET / ODC / IEEE / APII",
    "APII / Fonds de Promotion et Décentralisation Industrielle": "وكالة النهوض بالصناعة والتجديد / صندوق النهوض بالصناعة وتوسيع اللامركزية",
    "APII / Reseau des Centres d'Affaires Nationaux": "وكالة النهوض بالصناعة والتجديد / شبكة مراكز الأعمال الوطنية",
    "SOTUGAR / Ministere des Finances": "الشركة التونسية للضمان / وزارة المالية",
    "Agence Nationale Maîtrise Énergie (ANME)": "الوكالة الوطنية للتحكم في الطاقة (ANME)",
    "APII (Agence de Promotion de l'Industrie et de l'Innovation)": "وكالة النهوض بالصناعة والتجديد (APII)",
    "Société Tunisienne de Garantie (SOTUGAR)": "الشركة التونسية للضمان (SOTUGAR)",
    "Smart Capital Tunisie": "سمارت كابيتال تونس",
    "Reseau Carthage Business Angels": "شبكة قرطاج للمستثمرين الملائكيين",
    "Flat6Labs Tunisia": "فلات 6 لابس تونس",
    "BTS (Banque Tunisienne de Solidarite)": "البنك التونسي للتضامن (BTS)",
    "Centre de Formation et de Promotion (CTFP / ATFP)": "المركز الوطني للتكوين المستمر والترقية المهنية (CTFP / ATFP)",
    "Smart Capital / College des Startups": "سمارت كابيتال / لجنة الشركات الناشئة",
    "Smart Capital / Ministere des Technologies de la Communication": "سمارت كابيتال / وزارة تكنولوجيات الاتصال",
 
    // Resource Types
    "financement_bancaire": "تمويل بنكي",
    "concours_financement": "مسابقة وتمويل",
    "subvention": "منحة",
    "programme_accompagnement": "برنامج مرافقة",
    "cadre_legal_avantages": "إطار قانوني وامتيازات",
    "accompagnement_incubation": "مرافقة وحضن مشاريع",
    "accompagnement_conseil": "مرافقة وإرشاد",
    "garantie_credit": "ضمان القرض",
    "subvention_investissement": "منحة استثمار",
    "capital_investissement": "رأس مال استثماري",
    "business_angels": "مستثمرون ملائكيون",
    "garantie": "ضمان",
    "acceleration_investissement": "تسريع واستثمار",
    "subvention_recherche": "منحة بحث وتطوير",
    "subvention_formation": "منحة تكوين",
    "pret_participatif": "قرض تشاركي",
    "label_accreditation": "علامة واعتماد",
    "subvention_incitation": "منحة وتشجيع",
 
    // Resources Names
    "Credit à Moyen et Long Terme (CMLT)": "قرض متوسط وطويل المدى (CMLT)",
    "AINS Hackathon – Concours et financement projets IA entrepreneurship": "هاكاثون AINS – مسابقة وتمويل مشاريع الذكاء الاصطناعي وريادة الأعمال",
    "FOPRODI – Prime investissement matériel industriel (10%)": "صندوق النهوض بالصناعة وتوسيع اللامركزية – منحة استثمار المعدات الصناعية (10%)",
    "APII – Centres d'Affaires (Espaces Entreprendre)": "وكالة النهوض بالصناعة والتجديد – مراكز الأعمال (فضاءات المبادرة)",
    "Fonds National de Garantie (FNG)": "الصندوق الوطني للضمان",
    "Startup Act Tunisie – Cadre Avantages & Labellisation": "قانون الشركات الناشئة تونس – إطار الامتيازات وعلامة المؤسسة الناشئة",
    "Programme Efficacité Énergétique ANME – Subvention équipements": "برنامج النجاعة الطاقية للوكالة الوطنية للتحكم في الطاقة – منحة التجهيزات",
    "APII – Fonds de Promotion Industrielle (FOPRODI)": "وكالة النهوض بالصناعة والتجديد – صندوق النهوض بالصناعة (FOPRODI)",
    "SOTUGAR – Garantie crédits PME (fonds national garantie)": "الشركة التونسية للضمان – ضمان قروض المؤسسات الصغرى والمتوسطة",
    "Smart Capital – Fonds direct PME innovantes (hors ANAVA)": "سمارت كابيتال – الصندوق المباشر للمؤسسات الصغرى والمتوسطة المبتكرة",
    "Carthage Business Angels": "شبكة قرطاج للمستثمرين الملائكيين",
    "Flat6Labs Tunisia – Programme d'Acceleration et d'Investissement": "فلات 6 لابس تونس – برنامج تسريع واستثمار",
    "Credit Professionnel BTS Bank": "القرض المهني من البنك التونسي للتضامن",
    "CTFP – Financement formation professionnelle continue PME": "المركز الوطني للتكوين المستمر والترقية المهنية – تمويل التكوين المهني المستمر",
    "BFPME – Intilak 2": "البنك التونسي لتمويل المؤسسات الصغرى والمتوسطة – انطلاق 2",
    "Startup Label (Le Label de Startup)": "علامة مؤسسة ناشئة",
    "Bourse de la Startup (Startup Grant)": "منحة مؤسسة ناشئة"
  }
};
 
export function translateValue(value, lang) {
  if (!value) return "";
  return valueTranslations[lang]?.[value] || value;
}
 
// Metadata configuration for dimensions
const DIMENSION_CONFIG = [
  {
    id: 'market',
    jsonKey: 'market_score',
    f2Key: 'market',
    color: 'cyan',
    title: { fr: 'Marché', ar: 'السوق' },
    description: { fr: 'Analyse de la demande et adéquation marché.', ar: 'تحليل الطلب وملاءمة المنتج للسوق.' },
    subLabels: {
      taille_marche: { fr: 'Taille du marché', ar: 'حجم السوق' },
      concurrence: { fr: 'Concurrence', ar: 'المنافسة' },
      validation_client: { fr: 'Validation client', ar: 'التحقق من العملاء' },
      modele_revenus: { fr: 'Modèle de revenus', ar: 'نموذج الإيرادات' }
    }
  },
  {
    id: 'commercial',
    jsonKey: 'commercial_offer_score',
    f2Key: 'commercial_offer',
    color: 'indigo',
    title: { fr: 'Commercial', ar: 'العرض التجاري' },
    description: { fr: 'Traction client et tunnel de conversion.', ar: 'جذب العملاء ومسار تحويل المبيعات.' },
    subLabels: {
      proposition_valeur: { fr: 'Proposition de valeur', ar: 'مقترح القيمة' },
      maturite_produit: { fr: 'Maturité du produit', ar: 'نضج المنتج' },
      strategie_prix: { fr: 'Stratégie de prix', ar: 'استراتيجية التسعير' },
      alignement_besoins: { fr: 'Alignement avec les besoins', ar: 'الملاءمة مع الاحتياجات' }
    }
  },
  {
    id: 'innovation',
    jsonKey: 'innovation_score',
    f2Key: 'innovation',
    color: 'violet',
    title: { fr: 'Innovation', ar: 'الابتكار' },
    description: { fr: 'Avantage produit et barrières concurrentielles.', ar: 'ميزة المنتج والحواجز التنافسية.' },
    subLabels: {
      nouveaute_locale: { fr: 'Nouveauté locale', ar: 'الابتكار المحلي' },
      intensite_tech: { fr: 'Intensité technologique', ar: 'الكثافة التكنولوجية' },
      barrieres_entree: { fr: "Barrières à l'entrée", ar: 'حواجز الدخول' },
      degre_rupture: { fr: 'Degré de rupture', ar: 'درجة القطيعة' }
    }
  },
  {
    id: 'scalability',
    jsonKey: 'scalability_score',
    f2Key: 'scalability',
    color: 'amber',
    title: { fr: 'Scalabilité', ar: 'القابلية للتوسع' },
    description: { fr: "Potentiel d'automatisation et modèle récurrent.", ar: 'إمكانية الأتمتة والنموذج المتكرر.' },
    subLabels: {
      replicabilite: { fr: 'Réplicabilité', ar: 'قابلية التكرار' },
      independance_manuelle: { fr: 'Indépendance manuelle', ar: 'الاستقلالية عن العمل اليدوي' },
      couts_deploiement: { fr: 'Coûts de déploiement', ar: 'تكاليف النشر' },
      potentiel_geo: { fr: 'Potentiel géographique', ar: 'الإمكانية الجغرافية' }
    }
  },
  {
    id: 'green',
    jsonKey: 'green_score',
    f2Key: 'green',
    color: 'emerald',
    title: { fr: 'Green', ar: 'الاستدامة البيئية' },
    description: { fr: 'Bilan carbone et circularité des ressources.', ar: 'بصمة الكربون ودائرية الموارد.' },
    subLabels: {
      climat_air: { fr: 'Climat & Air', ar: 'المناخ والهواء' },
      eau: { fr: "Gestion de l'eau", ar: 'إدارة المياه' },
      sols_biodiversite: { fr: 'Sols & Biodiversité', ar: 'التربة والتنوع البيولوجي' },
      ressources_dechets: { fr: 'Ressources & Déchets', ar: 'الموارد والنفايات' }
    }
  }
];
 
export function getAdaptedData(data) {
  if (!data || Object.keys(data).length === 0) return null;

  const {
    project_id,
    startup_name,
    sector: data_sector,
    location: data_location,
    real_stage,
    perceived_stage,
    gap_detected,
    gap_explanation,
    divergence_signals,
    scores_data,
    detected_anomalies,
    recommended_resources,
    roadmap_data,
    financing_readiness_index,
    is_financeable,
    fri_interpretation,
    raw_answers
  } = data;

  const nom_entreprise = startup_name || `Projet #${project_id || ''}`;
  const localisation = data_location || "";
  const secteur = data_sector || "";
 
  // 6-Stage Timeline
  const stages = [
    {
      id: "Ideation",
      label: { fr: "Idéation", ar: "فكرة" },
      desc: { fr: "Définition du concept et étude de marché initiale.", ar: "تحديد المفهوم ودراسة السوق الأولية." }
    },
    {
      id: "Market Validation",
      label: { fr: "Validation", ar: "التحقق" },
      desc: { fr: "Création d'un MVP et premiers tests utilisateurs.", ar: "إنشاء نموذج أولي واختبار المستخدمين." }
    },
    {
      id: "Structuration",
      label: { fr: "Structuration", ar: "الهيكلة" },
      desc: { fr: "Enregistrement légal, constitution de l'équipe et modélisation.", ar: "التسجيل القانوني، تكوين الفريق وصياغة النموذج." }
    },
    {
      id: "Fundraising",
      label: { fr: "Levée de fonds", ar: "جمع التمويل" },
      desc: { fr: "Pitching, due diligence, recherche de capital.", ar: "تقديم العروض, فحص الجدوى والبحث عن رأس المال." }
    },
    {
      id: "Launch Planning",
      label: { fr: "Lancement", ar: "الإطلاق" },
      desc: { fr: "Début de la commercialisation et acquisition active.", ar: "بدء التسويق التجاري والاستقطاب النشط." }
    },
    {
      id: "Growth",
      label: { fr: "Croissance", ar: "النمو" },
      desc: { fr: "Passage à l'échelle, expansion géographique.", ar: "التوسع والنمو والتمدد الجغرافي." }
    }
  ];
 
  // Map scores from scores_f2 and details
  const mappedScores = DIMENSION_CONFIG.map(dim => {
    const rawScoreVal = scores_data?.scores_f2?.[dim.f2Key] ?? 0;
    const detailObj = scores_data?.detail?.[dim.jsonKey] || {};
 
    const subDimensions = Object.keys(dim.subLabels).map(subKey => {
      const subVal = detailObj.sous_scores?.[subKey] ?? 0;
      return {
        key: subKey,
        name: dim.subLabels[subKey],
        score: subVal
      };
    });
 
    const justificationFr = detailObj.justification || "";
    const justificationAr = translateValue(justificationFr, 'ar');
 
    return {
      id: dim.id,
      title: dim.title,
      score: rawScoreVal,
      color: dim.color,
      description: dim.description,
      justification: {
        fr: justificationFr,
        ar: justificationAr
      },
      subDimensions
    };
  });
 
  // Map anomalies
  const mappedAnomalies = (detected_anomalies || []).map(an => ({
    id: an.id,
    dimension: an.dimension_impactee,
    penalty: an.penalite,
    justification: {
      fr: an.justification,
      ar: translateValue(an.justification, 'ar')
    },
    action: {
      fr: an.action,
      ar: translateValue(an.action, 'ar')
    },
    kbLink: an.kb_link
  }));
 
  // Map recommended resources
  const mappedResources = (recommended_resources || []).map(r => {
    const tauxAr = translateValue(r.taux, 'ar');
    const justificationFr = r.justification || "";
    let justificationAr = justificationFr;
 
    if (justificationFr.includes("Recommandé pour stade")) {
      const stageName = real_stage;
      const sectorName = secteur;
      const relevanceMatch = justificationFr.match(/Pertinence:\s*([\d\.]+)%/);
      const pertinenceVal = relevanceMatch ? relevanceMatch[1] : (r.pertinence || 0);
 
      const isRegional = justificationFr.includes("regions_interieures");
      const isBP = justificationFr.includes("absence_business_plan");
      const isAcc = justificationFr.includes("besoin_accompagnement");
      const isFin = justificationFr.includes("absence_financement") || justificationFr.includes("business_model_flou");
 
      let addressesAr = "";
      if (isRegional) addressesAr = "يعالج: المناطق الداخلية. ";
      if (isBP) addressesAr = "يعالج: غياب مخطط العمل. ";
      if (isAcc) addressesAr = "يعالج: الحاجة للمرافقة. ";
      if (isFin) addressesAr = "يعالج: غياب التمويل / نموذج أعمال غير واضح. ";
 
      justificationAr = `موصى به لمرحلة "${translateValue(stageName, 'ar')}"، قطاع "${translateValue(sectorName, 'ar')}". ${addressesAr}الملاءمة: ${pertinenceVal}%.`;
    } else {
      justificationAr = translateValue(justificationFr, 'ar');
    }
 
    return {
      id: r.id,
      name: {
        fr: r.nom,
        ar: translateValue(r.nom, 'ar')
      },
      organisme: {
        fr: r.organisme,
        ar: translateValue(r.organisme, 'ar')
      },
      type: {
        fr: translateValue(r.type, 'fr'),
        ar: translateValue(r.type, 'ar')
      },
      taux: {
        fr: r.taux,
        ar: tauxAr
      },
      urlSource: r.url_source,
      pertinence: r.pertinence,
      justification: {
        fr: justificationFr,
        ar: justificationAr
      }
    };
  });
 
  // Map roadmap horizons
  const mappedRoadmap = [
    {
      horizon: "immediate",
      title: { fr: "Immédiat (0 - 30 jours)", ar: "فوري (0 - 30 يوماً)" },
      actions: (roadmap_data?.immediat_0_30j || []).map(act => ({
        text: {
          fr: act,
          ar: translateValue(act, 'ar')
        },
        completed: false
      }))
    },
    {
      horizon: "shortTerm",
      title: { fr: "Court terme (1 - 3 mois)", ar: "المدى القريب (1 - 3 أشهر)" },
      actions: (roadmap_data?.court_terme_1_3m || []).map(act => ({
        text: {
          fr: act,
          ar: translateValue(act, 'ar')
        },
        completed: false
      }))
    },
    {
      horizon: "mediumTerm",
      title: { fr: "Moyen terme (3 - 12 mois)", ar: "المدى المتوسط (3 - 12 شهراً)" },
      actions: (roadmap_data?.moyen_terme_3_12m || []).map(act => ({
        text: {
          fr: act,
          ar: translateValue(act, 'ar')
        },
        completed: false
      }))
    }
  ];
 
  // Financing readiness scores
  const financingScore = financing_readiness_index ?? 0;
  const isBankable = is_financeable ?? false;
  const interpretationFr = fri_interpretation || "";
 
  let interpretationAr = interpretationFr;
  if (interpretationFr.includes(`Le score global est plafonné à ${financingScore}/100`)) {
    interpretationAr = `تم سقف الدرجة الإجمالية عند ${financingScore}/100 بسبب الضعف الحرج في درجة السوق (<30). (الدرجة الفعلية المحتسبة: ${financingScore}/100)`;
  } else {
    interpretationAr = translateValue(interpretationFr, 'ar');
  }
 
  const financingReadiness = {
    score: financingScore,
    status: isBankable ? 'bankable' : 'non_bankable',
    statusLabel: {
      fr: isBankable ? "Bancable (Éligible)" : "Non bancable (À consolider)",
      ar: isBankable ? "جاهز للتمويل (مؤهل)" : "غير جاهز للتمويل (بحاجة لتعزيز)"
    },
    description: {
      fr: interpretationFr,
      ar: interpretationAr
    }
  };

  // Map blockers
  const mappedBlockers = (data.blockers || []).map((b, idx) => {
    const domainMapping = {
      "organisationnel": { fr: "Organisationnel", ar: "تنظيمي" },
      "marché": { fr: "Marché", ar: "السوق" },
      "légal": { fr: "Légal", ar: "قانوني" },
      "financier": { fr: "Financier", ar: "مالي" }
    };
    const domain = domainMapping[b.domaine] || { fr: b.domaine || "Général", ar: b.domaine || "عام" };
    const priority = b.priorite === 1 ? 'high' : (b.priorite === 2 ? 'medium' : 'low');
    return {
      id: `blocker_${idx}`,
      domain,
      priority,
      title: {
        fr: b.description,
        ar: translateValue(b.description, 'ar')
      },
      desc: {
        fr: `Obstacle critique impactant le déploiement du projet dans la dimension ${b.domaine || 'générale'}.`,
        ar: `عقبة حرجة تؤثر على سير المشروع في مجال ${domain.ar}.`
      }
    };
  });
 
  return {
    startupName: nom_entreprise,
    entrepreneur_id: project_id,
    secteur,
    localisation,
    maturity: {
      perceivedStage: perceived_stage,
      realStage: real_stage,
      stages,
      alertMessage: {
        fr: gap_explanation || "",
        ar: translateValue(gap_explanation, 'ar')
      },
      gapsList: divergence_signals || []
    },
    scores: mappedScores,
    anomalies: mappedAnomalies,
    blockers: mappedBlockers,
    resources: mappedResources,
    roadmap: mappedRoadmap,
    financingReadiness,
    answers: raw_answers || { free_text: { text: "" } }
  };
}
