# f2_scoring/matrice_coeff.py
"""
Ce fichier contient les structures de données définissant :
1. Le dictionnaire des matrices de comparaison par paires AHP.
2. Le dictionnaire des poids AHP précalculés et validés par le ratio de cohérence (CR).
3. Le dictionnaire des ajustements sectoriels (bonus et malus sous forme d'ajustements de poids).
4. Le dictionnaire des règles de détection d'anomalies et d'application de pénalités.

Il est conforme aux spécifications de la Feature 2 de AINS Hackathon 2026.
"""

# =====================================================================
# 1. DICTIONNAIRE DES MATRICES AHP (Matrices de comparaison par paires)
# =====================================================================
# Ces matrices sont exclusives aux dimensions 4x4 et à la dimension globale 5x5.
AHP_MATRICES = {
    "market": [
        [1.0,   0.333, 0.500, 0.500],  # MS1 - TAM
        [3.0,   1.0,   3.0,   2.0],    # MS2 - Concurrence
        [2.0,   0.333, 1.0,   0.667],  # MS3 - Validation client
        [2.0,   0.500, 1.500, 1.0]     # MS4 - Modèle de revenus
    ],
    "commercial_offer": [
        [1.0,   2.0,   3.0,   0.500],  # CO1 - Prop. de valeur
        [0.500, 1.0,   2.0,   0.333],  # CO2 - Maturité produit
        [0.333, 0.500, 1.0,   0.250],  # CO3 - Stratégie de prix
        [2.0,   3.0,   4.0,   1.0]     # CO4 - Alignement besoins
    ],
    "innovation": [
        [1.0,   2.0,   3.0,   2.0],    # IN1 - Nouveauté locale
        [0.500, 1.0,   2.0,   1.0],    # IN2 - Intensité technologique
        [0.333, 0.500, 1.0,   0.500],  # IN3 - Barrières à l'entrée
        [0.500, 1.0,   2.0,   1.0]     # IN4 - Degré de rupture
    ],
    "scalability": [
        [1.0,   2.0,   3.0,   4.0],    # SC1 - Réplicabilité
        [0.500, 1.0,   2.0,   3.0],    # SC2 - Indépendance manuelle
        [0.333, 0.500, 1.0,   1.0],    # SC3 - Coûts de déploiement
        [0.250, 0.333, 1.0,   1.0]     # SC4 - Potentiel géographique
    ],
    "green": [
        [1.0,   0.500, 3.0,   2.0],    # GS1 - Climat / Air
        [2.0,   1.0,   4.0,   3.0],    # GS2 - Eau
        [0.333, 0.250, 1.0,   0.500],  # GS3 - Sols et biodiversité
        [0.500, 0.333, 2.0,   1.0]     # GS4 - Ressources & déchets
    ],
    "global": [
        [1.0,   2.0,   1.0,   2.0,   3.0],  # Market Score
        [0.500, 1.0,   0.500, 1.0,   2.0],  # Commercial Offer
        [1.0,   2.0,   1.0,   2.0,   3.0],  # Innovation
        [0.500, 1.0,   0.500, 1.0,   2.0],  # Scalability
        [0.333, 0.500, 0.333, 0.500, 1.0]   # Green Score
    ]
}

# =====================================================================
# 2. DICTIONNAIRE DES POIDS AHP PRÉCALCULÉS
# =====================================================================
# Ces poids ont été calculés et validés par rapport aux indices de cohérence (CR < 10%).
AHP_WEIGHTS = {
    "market": {
        "MS1": 0.1205,  # TAM (~12.1%)
        "MS2": 0.4542,  # Concurrence (~45.4%)
        "MS3": 0.1826,  # Validation client (~18.3%)
        "MS4": 0.2427   # Modèle de revenus (~24.3%)
    },
    "commercial_offer": {
        "CO1": 0.2772,  # Prop. de valeur (~27.7%)
        "CO2": 0.1610,  # Maturité produit (~16.1%)
        "CO3": 0.0960,  # Stratégie de prix (~9.6%)
        "CO4": 0.4658   # Alignement besoins (~46.6%)
    },
    "innovation": {
        "IN1": 0.4231,  # Nouveauté locale (~42.3%)
        "IN2": 0.2272,  # Intensité technologique (~22.7%)
        "IN3": 0.1225,  # Barrières à l'entrée (~12.2%)
        "IN4": 0.2272   # Degré de rupture (~22.7%)
    },
    "scalability": {
        "SC1": 0.4687,  # Réplicabilité (~46.9%)
        "SC2": 0.2800,  # Indépendance manuelle (~28.0%)
        "SC3": 0.1361,  # Coûts de déploiement (~13.6%)
        "SC4": 0.1152   # Potentiel géographique (~11.5%)
    },
    "green": {
        "GS1": 0.2772,  # Climat / Air (~27.7%)
        "GS2": 0.4658,  # Eau (~46.6%)
        "GS3": 0.0960,  # Sols et biodiversité (~9.6%)
        "GS4": 0.1610   # Ressources & déchets (~16.1%)
    },
    "global": {
        "market": 0.2976,            # Market Score (~29.8%)
        "commercial_offer": 0.1579,  # Commercial Offer (~15.8%)
        "innovation": 0.2976,        # Innovation (~29.8%)
        "scalability": 0.1579,       # Scalability (~15.8%)
        "green": 0.0889              # Green Score (~8.9%)
    }
}

# Ratios de cohérence (CR) de chaque matrice pour validation
AHP_CONSISTENCY_RATIOS = {
    "market": 0.0169,            # Validé (< 0.10)
    "commercial_offer": 0.0113,  # Validé (< 0.10)
    "innovation": 0.0037,        # Validé (< 0.10)
    "scalability": 0.0113,       # Validé (< 0.10)
    "green": 0.0113,            # Validé (< 0.10)
    "global": 0.0029             # Validé (< 0.10)
}

# =====================================================================
# 3. AJUSTEMENTS SECTORIELS (Poids Bonus et Malus par secteur)
# =====================================================================
# Selon le document méthodologique, ces coefficients viennent s'ajouter 
# directement aux poids relatifs des sous-scores pour la dimension concernée.
SECTOR_ADJUSTMENTS = {
    # Agriculture
    "Agriculture": {
        "market": {"MS1": 0.05, "MS2": 0.00, "MS3": 0.10, "MS4": 0.00},
        "commercial_offer": {"CO1": 0.00, "CO2": 0.00, "CO3": 0.10, "CO4": 0.05},
        "innovation": {"IN1": 0.10, "IN2": 0.00, "IN3": 0.00, "IN4": 0.05},
        "scalability": {"SC1": 0.00, "SC2": -0.05, "SC3": 0.05, "SC4": 0.10},
        "green": {"GS1": 0.05, "GS2": 0.15, "GS3": 0.10, "GS4": 0.05}
    },
    # Tech / Digital
    "Tech / Digital": {
        "market": {"MS1": 0.05, "MS2": 0.05, "MS3": 0.15, "MS4": 0.05},
        "commercial_offer": {"CO1": 0.10, "CO2": 0.05, "CO3": 0.05, "CO4": 0.00},
        "innovation": {"IN1": 0.00, "IN2": 0.10, "IN3": 0.10, "IN4": 0.00},
        "scalability": {"SC1": 0.10, "SC2": 0.10, "SC3": 0.05, "SC4": 0.05},
        "green": {"GS1": 0.10, "GS2": 0.00, "GS3": 0.00, "GS4": 0.00}
    },
    # Industrie
    "Industrie": {
        "market": {"MS1": 0.00, "MS2": 0.05, "MS3": 0.00, "MS4": 0.00},
        "commercial_offer": {"CO1": 0.00, "CO2": 0.10, "CO3": 0.05, "CO4": 0.00},
        "innovation": {"IN1": 0.05, "IN2": 0.05, "IN3": 0.10, "IN4": 0.00},
        "scalability": {"SC1": -0.10, "SC2": -0.10, "SC3": 0.00, "SC4": -0.05},
        "green": {"GS1": 0.15, "GS2": 0.10, "GS3": 0.10, "GS4": 0.10}
    },
    # Services
    "Services": {
        "market": {"MS1": 0.00, "MS2": 0.05, "MS3": 0.05, "MS4": 0.00},
        "commercial_offer": {"CO1": 0.05, "CO2": 0.00, "CO3": 0.00, "CO4": 0.10},
        "innovation": {"IN1": 0.10, "IN2": 0.00, "IN3": 0.00, "IN4": 0.05},
        "scalability": {"SC1": 0.05, "SC2": 0.00, "SC3": 0.00, "SC4": -0.07},
        "green": {"GS1": 0.05, "GS2": 0.00, "GS3": 0.05, "GS4": 0.05}
    },
    # Commerce
    "Commerce": {
        "market": {"MS1": 0.05, "MS2": -0.10, "MS3": 0.05, "MS4": 0.05},
        "commercial_offer": {"CO1": 0.05, "CO2": 0.05, "CO3": 0.10, "CO4": -0.05},
        "innovation": {"IN1": 0.00, "IN2": 0.05, "IN3": -0.10, "IN4": -0.05},
        "scalability": {"SC1": 0.05, "SC2": 0.00, "SC3": 0.10, "SC4": 0.05},
        "green": {"GS1": 0.10, "GS2": 0.00, "GS3": 0.00, "GS4": 0.10}
    }
}

# Alias simplifiés pour faciliter les requêtes et assurer la compatibilité
SECTOR_ALIASES = {
    "agriculture_sylviculture_peche":"Agriculture",
    "agroalimentaire": "Agriculture",
    "Agriculture": "Agriculture",
    "agritech / agroalimentaire": "Agriculture",
    "tech / digital": "Tech / Digital",
    "tech/digital": "Tech / Digital",
    "Tech":"Tech / Digital",
    "tech": "Tech / Digital",
    "fintech": "Tech / Digital",
    " services financiers": "Services",
    "edtech": "Tech / Digital",
    "edtech / formation": "Tech / Digital",
    "healthtech": "Tech / Digital",
    "healthtech / medtech": "Tech / Digital",
    "Industrie": "Industrie",
    "Industrie / manufacture": "Industrie",
    "services": "Services",
    "tourisme": "Services",
    "Services": "Services",
    "tourisme / culture": "Services",
    "Commerce":"Commerce",
    "commerce": "Commerce",
    "ecommerce": "Commerce",
    "e-commerce / retail": "Commerce"
}

# Rendre les ajustements accessibles via les alias simplifiés également
for alias, full_name in list(SECTOR_ALIASES.items()):
    SECTOR_ADJUSTMENTS[alias] = SECTOR_ADJUSTMENTS[full_name]

# =====================================================================
# 4. RÈGLES DE DÉTECTION D'ANOMALIES ET DE PÉNALITÉS (DÉCLARATIVE)
# =====================================================================
# Chaque règle est structurée de manière déclarative pour être facilement 
# interprétable et sérialisable (ex. en JSON).
ANOMALY_RULES = [
    # =========================================================================
    # ------------------ MARKET SCORE ANOMALIES ------------------
    # =========================================================================
    {
        "id": "ANOM_MS_1",
        "dimension": "market",
        "penalty_points": 8,
        "target_score": "market",
        "conditions": [
            {"variable": "MS3", "operator": ">=", "value": 70},
            {"variable": "MS4", "operator": "<=", "value": 20}
        ],
        "justification_template": (
            "Impressionnant ! Votre score de traction client atteint {MS3}/100 (LOI ou intentions). "
            "Cependant, votre modèle de revenus n'est évalué qu'à {MS4}/100. Cette divergence est un signal d'alarme pour les comités de crédit comme la BFPME : "
            "sans stratégie de monétisation claire, votre forte traction ne se transformera pas en rentabilité viable."
        ),
        "action_template": "Verrouillez votre pricing (abonnements, commissions ou freemium) en vous appuyant sur la ressource {kb_link} pour solidifier votre business plan.",
        "kb_link": "KB-BFPME-BP-004"
    },
    {
        "id": "ANOM_MS_2",
        "dimension": "market",
        "penalty_points": 6,
        "target_score": "market",
        "conditions": [
            {"variable": "MS1", "operator": ">=", "value": 80},
            {"variable": "MS2", "operator": "<=", "value": 12}
        ],
        "justification_template": (
            "Vous déclarez un marché total adressable (TAM) très large de {MS1}/100, mais votre score concurrentiel est anormalement bas ({MS2}/100). "
            "Pour un investisseur VC en Tunisie, un paysage concurrentiel 'inexistant' traduit souvent un angle mort dans votre étude de marché "
            "ou un manque de maturité du secteur ciblé."
        ),
        "action_template": "Cartographiez vos concurrents directs et indirects (locaux et informels) en utilisant la matrice sectorielle disponible dans le document {kb_link}.",
        "kb_link": "KB-APII-MKT-015"
    },
    {
        "id": "ANOM_MS_3",
        "dimension": "market",
        "penalty_points": 5,
        "target_score": "both_market_commercial",
        "conditions": [
            {"variable": "MS4", "operator": ">=", "value": 70},
            {"variable": "CO3", "operator": "<=", "value": 20}
        ],
        "justification_template": (
            "Votre modèle de revenus est évalué à {MS4}/100, mais votre stratégie de tarification s'effondre à {CO3}/100. "
            "Déclarer des flux de revenus solides sans une structure de prix cohérente et validée met en péril vos projections financières "
            "face aux exigences de la SOTUGAR pour les garanties de crédit."
        ),
        "action_template": "Structurez votre grille tarifaire (coût de revient + marge sectorielle) en consultant le guide pratique {kb_link}.",
        "kb_link": "KB-SOTUGAR-FIN-022"
    },
    {
        "id": "ANOM_MS_4",
        "dimension": "market",
        "penalty_points": 10,
        "target_score": "market",
        "conditions": [
            {"variable": "MS3", "operator": ">=", "value": 70},
            {"variable": "CO2", "operator": "<=", "value": 20}
        ],
        "justification_template": (
            "Avoir des engagements clients forts ({MS3}/100) alors que le produit est au stade de simple idée ({CO2}/100) présente un fort risque d'exécution. "
            "Les comités du Startup Act sont très vigilants face à ce profil : promettre une solution sans avoir initié de prototype (MVP) "
            "peut détruire votre crédibilité commerciale."
        ),
        "action_template": "Lancez le développement d'un prototype fonctionnel ou d'une maquette interactive en suivant le framework agile tunisien décrit dans {kb_link}.",
        "kb_link": "KB-TACT-MVP-009"
    },

    # =========================================================================
    # ------------------ COMMERCIAL OFFER ANOMALIES ------------------
    # =========================================================================
    {
        "id": "ANOM_CO_1",
        "dimension": "commercial_offer",
        "penalty_points": 8,
        "target_score": "commercial_offer",
        "conditions": [
            {"variable": "CO1", "operator": ">=", "value": 80},
            {"variable": "MS3", "operator": "<=", "value": 20}
        ],
        "justification_template": (
            "Votre proposition de valeur est notée à {CO1}/100, mais votre validation terrain est critique ({MS3}/100). "
            "C'est le syndrome classique du produit 'théorique' : une offre excellente sur le papier, mais qui n'a pas été confrontée "
            "à la réalité des décideurs ou des consommateurs tunisiens."
        ),
        "action_template": "Sortez du bureau et soumettez votre offre à au moins 10 prospects locaux. Utilisez la grille d'entretien du document {kb_link}.",
        "kb_link": "KB-ODC-DESIGN-002"
    },
    {
        "id": "ANOM_CO_2",
        "dimension": "commercial_offer",
        "penalty_points": 5,
        "target_score": "both_commercial_innovation",
        "conditions": [
            {"variable": "CO2", "operator": ">=", "value": 80},
            {"variable": "IN2", "operator": "<=", "value": 12}
        ],
        "justification_template": (
            "Le produit est déclaré fini ou commercialisé ({CO2}/100), mais son intensité technologique est quasi nulle ({IN2}/100). "
            "Sans barrière à l'entrée technologique, votre projet court un risque élevé de réplication immédiate par la concurrence, "
            "ce qui vous pénalisera lors d'un examen de labellisation Startup Act."
        ),
        "action_template": "Identifiez comment automatiser ou enrichir techniquement votre offre (IA, data, process propriétaires) à l'aide de la ressource {kb_link}.",
        "kb_link": "KB-TACT-LAB-014"
    },
    {
        "id": "ANOM_CO_3",
        "dimension": "commercial_offer",
        "penalty_points": 7,
        "target_score": "commercial_offer",
        "conditions": [
            {"variable": "CO3", "operator": ">=", "value": 70},
            {"variable": "MS3", "operator": "<=", "value": 30}
        ],
        "justification_template": (
            "Viser un prix premium ({CO3}/100) avec une validation client si faible ({MS3}/100) sur un marché à faible pouvoir d'achat (low-income) "
            "est une anomalie de positionnement majeure en Tunisie. Les barrières budgétaires locales briseront votre taux de conversion."
        ),
        "action_template": "Ajustez votre tarification via une offre de pénétration ou un modèle freemium adapté au contexte économique tunisien grâce au guide {kb_link}.",
        "kb_link": "KB-APII-PRICING-003"
    },
    {
        "id": "ANOM_CO_4",
        "dimension": "commercial_offer",
        "penalty_points": 6,
        "target_score": "commercial_offer",
        "conditions": [
            {"variable": "CO4", "operator": ">=", "value": 70},
            {"variable": "has_client_interviews", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Vous revendiquez un fort alignement offre-besoin ({CO4}/100) sans avoir documenté d'interviews clients réelles. "
            "Pour les incubateurs d'élite en Tunisie, l'absence de preuves qualitatives transforme cet alignement en une simple intuition non vérifiée."
        ),
        "action_template": "Menez et formalisez des fiches de comptes-rendus d'interviews clients en utilisant le modèle standardisé fourni dans {kb_link}.",
        "kb_link": "KB-IEEE-VALID-005"
    },

    # =========================================================================
    # ------------------ INNOVATION ANOMALIES ------------------
    # =========================================================================
    {
        "id": "ANOM_IN_1",
        "dimension": "innovation",
        "penalty_points": 8,
        "target_score": "innovation",
        "conditions": [
            {"variable": "IN1", "operator": ">=", "value": 70},
            {"variable": "IN3", "operator": "<=", "value": 12},
            {"variable": "IN2", "operator": "<=", "value": 20}
        ],
        "justification_template": (
            "Revendiquer une forte nouveauté locale ({IN1}/100) sans aucune barrière à l'entrée ({IN3}/100) ni intensité technique ({IN2}/100) "
            "crée un risque de 'Fast Follower'. N'importe quel acteur en Tunisie pourra copier votre idée en quelques semaines si vous validez le marché."
        ),
        "action_template": "Consultez le document {kb_link} pour comprendre comment bâtir des barrières non technologiques (ex: exclusivités, marque, réseau de distribution).",
        "kb_link": "KB-INNORPI-STRAT-001"
    },
    {
        "id": "ANOM_IN_2",
        "dimension": "innovation",
        "penalty_points": 6,
        "target_score": "innovation",
        "conditions": [
            {"variable": "IN2", "operator": ">=", "value": 80},
            {"variable": "CO2", "operator": "<=", "value": 20}
        ],
        "justification_template": (
            "Votre intensité technologique est excellente ({IN2}/100), mais votre produit reste confiné au stade de l'idée ({CO2}/100). "
            "C'est un profil typique de 'recherche de laboratoire'. Sans confrontation MVP, la technologie risque de ne jamais rencontrer "
            "un besoin de marché solvable en Tunisie."
        ),
        "action_template": "Définissez les spécifications techniques minimales de votre premier MVP en vous appuyant sur le canevas {kb_link}.",
        "kb_link": "KB-AINS-TECH-011"
    },
    {
        "id": "ANOM_IN_3",
        "dimension": "innovation",
        "penalty_points": 10,
        "target_score": "innovation",
        "conditions": [
            {"variable": "IN3", "operator": ">=", "value": 70},
            {"variable": "has_patent_deposit_art12", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Un brevet est revendiqué comme barrière ({IN3}/100), mais aucun dépôt n'est enregistré sous l'Article 12 du Startup Act tunisien. "
            "Légalement et financièrement, votre propriété intellectuelle n'est pas sécurisée sur le territoire national, bloquant tout investissement institutionnel."
        ),
        "action_template": "Initiez les démarches de dépôt de brevet ou d'enregistrement INNORPI en exploitant les avantages de l'Article 12 détaillés dans {kb_link}.",
        "kb_link": "KB-TACT-ART12-001"
    },
    {
        "id": "ANOM_IN_4",
        "dimension": "innovation",
        "penalty_points": 5,
        "target_score": "innovation",
        "conditions": [
            {"variable": "IN4", "operator": ">=", "value": 80},
            {"variable": "MS1", "operator": "<=", "value": 25}
        ],
        "justification_template": (
            "Une rupture disruptive majeure est déclarée ({IN4}/100), mais la taille de votre marché (TAM) est très faible ({MS1}/100). "
            "Les fonds de capital-risque (VC) tunisiens évitent les innovations lourdes confinées à des niches trop restreintes, car le retour sur investissement y est insuffisant."
        ),
        "action_template": "Explorez des cas d'usage adjacents ou une stratégie d'internationalisation précoce en suivant la méthodologie du guide {kb_link}.",
        "kb_link": "KB-ANAVA-SCALE-007"
    },

    # =========================================================================
    # ------------------ SCALABILITY ANOMALIES ------------------
    # =========================================================================
    {
        "id": "ANOM_SC_1",
        "dimension": "scalability",
        "penalty_points": 10,
        "target_score": "scalability",
        "conditions": [
            {"variable": "SC1", "operator": ">=", "value": 18}, # Ajusté si base sur 20 ou transformer selon vos métriques
            {"variable": "MS4", "operator": "<=", "value": 20}
        ],
        "justification_template": (
            "Déclarer une forte réplicabilité ({SC1}) sans modèle de revenus clair ({MS4}/100) déclenche l'effet d'incitation (Incentive Effect) de Stiglitz & Weiss. "
            "Les projets hautement scalables mais sans monétisation claire tendent à brûler du cash de manière risquée, ce qui effraie les financeurs."
        ),
        "action_template": "Validez votre premier modèle d'affaires unitaire (Unit Economics) en utilisant le simulateur financier {kb_link}.",
        "kb_link": "KB-SOTUGAR-RISK-005"
    },
    {
        "id": "ANOM_SC_2",
        "dimension": "scalability",
        "penalty_points": 8,
        "target_score": "scalability",
        "conditions": [
            {"variable": "SC1", "operator": ">=", "value": 70},
            {"variable": "SC2", "operator": "<=", "value": 20}
        ],
        "justification_template": (
            "Une haute réplicabilité est revendiquée ({SC1}/100), mais votre indépendance manuelle est critique ({SC2}/100). "
            "Si chaque nouveau client exige une intervention humaine lourde de votre équipe, votre modèle est linéaire et non scalable. "
            "L'écosystème ANAVA / Smart Capital ne pourra pas financer une croissance explosive sous ces conditions."
        ),
        "action_template": "Identifiez les goulots d'étranglement opérationnels et commencez à automatiser vos livraisons grâce aux outils décrits dans {kb_link}.",
        "kb_link": "KB-ANAVA-OPS-012"
    },
    {
        "id": "ANOM_SC_3",
        "dimension": "scalability",
        "penalty_points": 6,
        "target_score": "scalability",
        "conditions": [
            {"variable": "SC4", "operator": ">=", "value": 70},
            {"variable": "CO3", "operator": "<=", "value": 20}
        ],
        "justification_template": (
            "Un fort potentiel international est affiché ({SC4}/100), mais votre tarification est jugée inadaptée ({CO3}/100). "
            "Exporter une offre tunisienne exige une structure de prix incluant les coûts de transfert, de conformité légale croisée, "
            "et des devises convertibles (loi des changes)."
        ),
        "action_template": "Adaptez votre modèle de prix pour l'export (devises, taxes internationales) en consultant le guide pratique du CEPEX {kb_link}.",
        "kb_link": "KB-CEPEX-EXP-002"
    },
    {
        "id": "ANOM_SC_4",
        "dimension": "scalability",
        "penalty_points": 5,
        "target_score": "scalability",
        "conditions": [
            {"variable": "SC3", "operator": ">=", "value": 70},
            {"variable": "IN2", "operator": "<=", "value": 12}
        ],
        "justification_template": (
            "Revendiquer des coûts de déploiement très faibles ({SC3}/100) sur un service hautement manuel et sans socle technologique ({IN2}/100) "
            "est une illusion financière. La masse salariale requise pour grossir en Tunisie annulera rapidement vos marges théoriques."
        ),
        "action_template": "Modélisez l'évolution de vos charges de personnel en fonction de la croissance du volume de clients à l'aide du modèle {kb_link}.",
        "kb_link": "KB-BFPME-FIN-008"
    },

    # =========================================================================
    # ------------------ GREEN SCORE ANOMALIES ------------------
    # =========================================================================
    {
        "id": "ANOM_GS_1",
        "dimension": "green",
        "penalty_points": 7,
        "target_score": "green",
        "conditions": [
            {"variable": "GS4", "operator": ">=", "value": 70},
            {"variable": "GS1", "operator": "<=", "value": 20}
        ],
        "justification_template": (
            "Afficher un score d'économie circulaire de {GS4}/100 tout en dépendant à 100% des énergies fossiles ({GS1}/100) "
            "est assimilé à du 'Greenwashing' par les bailleurs de fonds internationaux (PNUD, Green Climate Fund) actifs en Tunisie. "
            "L'impact carbone global neutralise vos efforts de recyclage."
        ),
        "action_template": "Réalisez un bilan de vos sources d'approvisionnement énergétique et intégrez un plan de transition vers les énergies renouvelables via la ressource {kb_link}.",
        "kb_link": "KB-PNUD-ESG-001"
    },
    {
        "id": "ANOM_GS_2",
        "dimension": "green",
        "penalty_points": 10,
        "target_score": "green",
        "conditions": [
            {"variable": "GS2", "operator": ">=", "value": 70},
            {"variable": "sector", "operator": "in", "value": ["Agroalimentaire", "agroalimentaire","Agriculture"]},
            {"variable": "has_water_data", "operator": "==", "value": False}
        ],
        "justification_template": (
            "En Tunisie, pays en situation de stress hydrique structurel, revendiquer une gestion de l'eau irréprochable ({GS2}/100) "
            "dans le secteur {sector} sans fournir la moindre donnée hydrique chiffrée est un risque éliminatoire pour l'obtention d'autorisations (CRDA/SONEDE)."
        ),
        "action_template": "Mettez en place un tableau de suivi de votre consommation d'eau au litre près en vous basant sur la méthodologie sectorielle {kb_link}.",
        "kb_link": "KB-ANPE-AGRO-002"
    },
    {
        "id": "ANOM_GS_3",
        "dimension": "green",
        "penalty_points": 5,
        "target_score": "green",
        "conditions": [
            {"variable": "GS1", "operator": ">=", "value": 80},
            {"variable": "saas_physical_specified", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Votre bilan carbone est auto-évalué comme excellent ({GS1}/100), mais votre modèle opérationnel (numérique vs physique) n'est pas spécifié. "
            "Un diagnostic d'impact environnemental sérieux ne peut être validé sans séparer l'empreinte des serveurs logitiels de celle de la logistique matérielle."
        ),
        "action_template": "Précisez la nature de votre infrastructure et de vos flux logistiques dans la section Environnement en téléchargeant le framework {kb_link}.",
        "kb_link": "KB-ODC-ESG-004"
    },
    {
        "id": "ANOM_GS_4",
        "dimension": "green",
        "penalty_points": 8,
        "target_score": "green",
        "conditions": [
            {"variable": "GS3", "operator": ">=", "value": 70},
            {"variable": "sector", "operator": "in", "value": ["Industrie", "industrie"]},
            {"variable": "has_eie_document", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Déclarer des sols neutres ({GS3}/100) pour un projet dans le secteur {sector} sans disposer d'une Étude d'Impact Environnemental (EIE) "
            "officielle est juridiquement non conforme en Tunisie. L'ANPE bloque systématiquement l'implantation d'industries sans ce livrable."
        ),
        "action_template": "Commandez ou préparez un pré-audit d'EIE réglementaire en vous conformant au cahier des charges officiel de l'ANPE disponible dans {kb_link}.",
        "kb_link": "KB-ANPE-IND-007"
    },

    # =========================================================================
    # ------------------ SECTOR-SPECIFIC ANOMALIES ------------------
    # =========================================================================
    {
        "id": "ANOM_MS_5",
        "dimension": "market",
        "penalty_points": 8,
        "target_score": "market",
        "conditions": [
            {"variable": "sector", "operator": "in", "value": ["Commerce", "commerce"]},
            {"variable": "MS3", "operator": ">=", "value": 70},
            {"variable": "has_online_presence", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Dans le secteur du {sector}, vous annoncez une validation commerciale majeure ({MS3}/100) sans aucune présence en ligne documentée (site, réseaux, app). "
            "À l'ère de la numérisation des canaux, l'absence d'empreinte digitale jette un doute sur l'authenticité ou la scalabilité de vos transactions."
        ),
        "action_template": "Activez au moins un canal numérique vitrine ou e-commerce et référencez-le en vous guidant avec la ressource {kb_link}.",
        "kb_link": "KB-ODC-COMMERCE-011"
    },
    {
        "id": "ANOM_MS_6",
        "dimension": "market",
        "penalty_points": 6,
        "target_score": "market",
        "conditions": [
            {"variable": "sector", "operator": "in", "value": ["Industrie", "industrie"]},
            {"variable": "MS1", "operator": ">=", "value": 70},
            {"variable": "has_b2b_clients", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Pour un projet lié à l' {sector}, un fort volume de marché théorique ({MS1}/100) sans aucun client ou partenaire B2B contractualisé (ou sous LOI) "
            "indique un sérieux blocage du cycle de vente industriel, souvent très long en Tunisie."
        ),
        "action_template": "Engagez des discussions industrielles pour signer une première convention de test en adaptant le modèle juridique {kb_link}.",
        "kb_link": "KB-APII-B2B-006"
    },
    {
        "id": "ANOM_CO_5",
        "dimension": "commercial_offer",
        "penalty_points": 8,
        "target_score": "commercial_offer",
        "conditions": [
            {"variable": "sector", "operator": "in", "value": ["Services", "services"]},
            {"variable": "CO4", "operator": ">=", "value": 70},
            {"variable": "has_user_tests", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Dans le domaine des {sector}, l'alignement offre-besoin déclaré ({CO4}/100) est contredit par l'absence totale de tests utilisateurs réels. "
            "L'expérience client (UX) dans les services tunisiens est le premier facteur de rétention ; l'ignorer est un risque opérationnel lourd."
        ),
        "action_template": "Organisez une session de focus-group ou un test d'utilisabilité bêta en suivant le protocole méthodologique {kb_link}.",
        "kb_link": "KB-ODC-UX-001"
    },
    {
        "id": "ANOM_CO_6",
        "dimension": "commercial_offer",
        "penalty_points": 6,
        "target_score": "commercial_offer",
        "conditions": [
            {"variable": "sector", "operator": "in", "value": ["Agriculture", "Agriculture"]},
            {"variable": "CO3", "operator": ">=", "value": 70},
            {"variable": "price_benchmarked_vs_distrib", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Votre stratégie de prix dans le secteur {sector} est ambitieuse ({CO3}/100), mais vos tarifs n'ont pas été benchmarkés par rapport à la "
            "grande distribution tunisienne (Carrefour, Géant, Magasin Général). Vos marges risquent d'être écrasées par les centrales d'achat."
        ),
        "action_template": "Réalisez un relevé linéaire des prix concurrents et intégrez la taxe sur la valeur ajoutée et les marges distributeurs selon le modèle {kb_link}.",
        "kb_link": "KB-APII-AGRO-019"
    },
    {
        "id": "ANOM_IN_5",
        "dimension": "innovation",
        "penalty_points": 10,
        "target_score": "innovation",
        "conditions": [
            {"variable": "sector", "operator": "in", "value": ["Tech / Digital", "Tech"]},
            {"variable": "IN2", "operator": ">=", "value": 80},
            {"variable": "has_tech_stack", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Déclarer une intensité technologique de {IN2}/100 dans le secteur {sector} sans pouvoir documenter précisément votre Stack Technique "
            "est un 'Red Flag' absolu pour les experts du comité d'évaluation de Smart Capital. Cela s'apparente à un effet d'annonce sans fondement."
        ),
        "action_template": "Rédigez l'architecture détaillée de votre stack (Backend, Frontend, Cloud, Sécurité) en complétant le schéma technique de la ressource {kb_link}.",
        "kb_link": "KB-AINS-TECH-003"
    },
    {
        "id": "ANOM_IN_6",
        "dimension": "innovation",
        "penalty_points": 8,
        "target_score": "innovation",
        "conditions": [
            {"variable": "sector", "operator": "in", "value": ["Commerce", "commerce"]},
            {"variable": "IN4", "operator": ">=", "value": 70},
            {"variable": "is_identical_model", "operator": "==", "value": True}
        ],
        "justification_template": (
            "Votre projet dans le {sector} revendique une rupture disruptive ({IN4}/100), pourtant vos données indiquent un modèle strictement identique "
            "aux concurrents tunisiens existants. Le manque de différenciation réelle invalide le critère d'innovation indispensable au Startup Act."
        ),
        "action_template": "Redéfinissez votre avantage concurrentiel (ex: innovation de modèle d'affaires, expérience d'achat) en vous appuyant sur le guide {kb_link}.",
        "kb_link": "KB-TACT-LAB-005"
    },
    {
        "id": "ANOM_SC_5",
        "dimension": "scalability",
        "penalty_points": 8,
        "target_score": "scalability",
        "conditions": [
            {"variable": "sector", "operator": "in", "value": ["Industrie", "industrie"]},
            {"variable": "SC1", "operator": ">=", "value": 60},
            {"variable": "has_production_capacity", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Afficher une forte ambition de réplicabilité ({SC1}/100) en {sector} sans préciser votre capacité de production physique (machines, usine, main d'œuvre) "
            "est une anomalie majeure. La scalabilité industrielle est indissociable de la maîtrise de vos outils de production physiques."
        ),
        "action_template": "Dimensionnez vos besoins d'investissements matériels (CAPEX) et de capacité de production mensuelle à l'aide de la matrice {kb_link}.",
        "kb_link": "KB-BFPME-IND-014"
    },
    {
        "id": "ANOM_SC_6",
        "dimension": "scalability",
        "penalty_points": 7,
        "target_score": "scalability",
        "conditions": [
            {"variable": "sector", "operator": "in", "value": ["Services", "services"]},
            {"variable": "SC4", "operator": ">=", "value": 70},
            {"variable": "is_remotely_adaptable", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Viser un déploiement géographique international ({SC4}/100) pour une offre de {sector} qui n'est pas adaptable à distance ou en ligne "
            "est une contradiction. Les barrières logistiques physiques et douanières tunisiennes limiteront drastiquement votre expansion internationale."
        ),
        "action_template": "Modélisez une version numérisée ou un système de franchises pour exporter votre service en vous inspirant de la ressource {kb_link}.",
        "kb_link": "KB-GEWEET-SCALE-002"
    },
    {
        "id": "ANOM_GS_5",
        "dimension": "green",
        "penalty_points": 7,
        "target_score": "green",
        "conditions": [
            {"variable": "sector", "operator": "in", "value": ["Commerce", "commerce"]},
            {"variable": "GS4", "operator": ">=", "value": 70},
            {"variable": "packaging_logistics_documented", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Votre score de gestion des déchets dans le {sector} est excellent ({GS4}/100), mais vos processus d'emballage et de logistique (dernier kilomètre) "
            "ne sont pas documentés. Ce manque de transparence invalide la sincérité de votre engagement écologique auprès des critères RSE des investisseurs."
        ),
        "action_template": "Spécifiez l'utilisation de matériaux biodégradables ou l'optimisation de vos tournées de livraison en téléchargeant le guide {kb_link}.",
        "kb_link": "KB-PNUD-GREEN-009"
    },
    {
        "id": "ANOM_GS_6",
        "dimension": "green",
        "penalty_points": 5,
        "target_score": "green",
        "conditions": [
            {"variable": "sector", "operator": "in", "value": ["Tech / Digital", "Tech"]},
            {"variable": "GS1", "operator": ">=", "value": 70},
            {"variable": "green_hosting_policy", "operator": "==", "value": False}
        ],
        "justification_template": (
            "Revendiquer un fort score d'action climatique ({GS1}/100) dans le secteur {sector} sans politique d'hébergement éco-responsable (Green Hosting) "
            "est contradictoire. L'empreinte carbone des serveurs et de la data est le premier levier d'action environnementale d'une startup du numérique."
        ),
        "action_template": "Sélectionnez un fournisseur de cloud ou un data center certifié neutre en carbone en consultant le catalogue de solutions de la ressource {kb_link}.",
        "kb_link": "KB-IEEE-GREEN-012"
    },

    # =========================================================================
    # ------------------ INTER-SCORE / GLOBAL ANOMALIES ------------------
    # =========================================================================
    {
        "id": "ANOM_GLOBAL_1",
        "dimension": "global",
        "penalty_points": 8,
        "target_score": "global",
        "conditions": [
            {"variable": "IN4", "operator": ">=", "value": 80},
            {"variable": "IN2", "operator": ">=", "value": 70},
            {"variable": "market_score", "operator": "<=", "value": 35}
        ],
        "justification_template": (
            "Votre projet présente une technologie disruptive de pointe ({IN4}/100, {IN2}/100), mais votre Market Score global est critique ({market_score}/100). "
            "C'est le risque classique d'une 'technologie à la recherche d'un problème' : un produit sophistiqué mais sans opportunité de marché "
            "viable validée en Tunisie."
        ),
        "action_template": "Pivotez ou adaptez les fonctionnalités de votre technologie pour répondre à un besoin urgent et solvable du marché décrit dans {kb_link}.",
        "kb_link": "KB-AINS-INNOV-001"
    },
    {
        "id": "ANOM_GLOBAL_2",
        "dimension": "global",
        "penalty_points": 5,
        "target_score": "global",
        "conditions": [
            {"variable": "scalability_score", "operator": ">=", "value": 75},
            {"variable": "green_score", "operator": "<=", "value": 25}
        ],
        "justification_template": (
            "Votre fort potentiel d'échelle ({scalability_score}/100) combiné à une absence d'intégration écologique ({green_score}/100) dessine un modèle de croissance non durable. "
            "Les grands programmes d'accélération internationaux (comme ceux du PNUD ou de la Banque Mondiale en Tunisie) rejettent désormais "
            "les projets qui scalent au détriment direct des indicateurs environnementaux."
        ),
        "action_template": "Intégrez des indicateurs clés d'impact ESG dès votre phase de scale en appliquant les standards internationaux de la ressource {kb_link}.",
        "kb_link": "KB-PNUD-ESG-010"
    },
    {
        "id": "ANOM_GLOBAL_3",
        "dimension": "global",
        "penalty_points": 10,
        "target_score": "global",
        "conditions": [
            {"variable": "market_score", "operator": ">=", "value": 75},
            {"variable": "commercial_offer_score", "operator": ">=", "value": 70},
            {"variable": "green_score", "operator": "<=", "value": 20}
        ],
        "justification_template": (
            "Vos scores de performance de marché et commerciaux sont excellents ({market_score}/100, {commercial_offer_score}/100), "
            "mais votre considération environnementale est inexistante ({green_score}/100). Ignorer totalement les critères ESG à ce stade de réussite "
            "commerciale restreindra l'accès aux fonds d'investissement à impact européens actifs sur l'écosystème tunisien."
        ),
        "action_template": "Formulez une politique de responsabilité environnementale claire pour votre entreprise en vous basant sur le modèle de conformité {kb_link}.",
        "kb_link": "KB-GEWEET-ESG-003"
    },
    {
        "id": "ANOM_GLOBAL_4",
        "dimension": "global",
        "penalty_points": 15,
        "target_score": "global",
        "conditions": [
            {"variable": "market_score", "operator": ">=", "value": 70},
            {"variable": "commercial_offer_score", "operator": ">=", "value": 70},
            {"variable": "innovation_score", "operator": ">=", "value": 70},
            {"variable": "scalability_score", "operator": ">=", "value": 70},
            {"variable": "green_score", "operator": ">=", "value": 70},
            {"variable": "stage", "operator": "==", "value": "Ideation"}
        ],
        "justification_template": (
            "Alerte de surévaluation systémique ! L'ensemble de vos dimensions affiche des notes supérieures à 70/100 alors que vous déclarez être "
            "au stade d' {stage}. Ce biais de perception (effet Dunning-Kruger) est lourdement sanctionné par les jurys de hackathons et les banques, "
            "car il démontre un manque de lucidité face aux défis réels du terrain."
        ),
        "action_template": "Revisitez votre auto-évaluation de manière objective et alignez vos réponses sur des faits mesurables en suivant le guide de modération {kb_link}.",
        "kb_link": "KB-AINS-EVAL-001"
    },
    {
        "id": "ANOM_GLOBAL_5",
        "dimension": "global",
        "penalty_points": 12,
        "target_score": "global",
        "conditions": [
            {"variable": "sector", "operator": "in", "value": ["Industrie", "Industrie"]},
            {"variable": "scalability_score", "operator": ">=", "value": 70},
            {"variable": "innovation_score", "operator": ">=", "value": 65},
            {"variable": "green_score", "operator": "<=", "value": 30}
        ],
        "justification_template": (
            "Dans le secteur {sector}, votre projet combine forte scalabilité ({scalability_score}/100) et innovation ({innovation_score}/100), "
            "mais affiche un Green Score critique ({green_score}/100). Déployer à grande échelle une innovation industrielle polluante ou non optimisée énergétiquement "
            "vous exposera à des sanctions de l'ANPE et à un refus de financement européen."
        ),
        "action_template": "Intégrez des écoconceptions industrielles et des technologies d'efficience dans vos lignes de production à l'aide du document de référence {kb_link}.",
        "kb_link": "KB-ANPE-IND-012"
    },
    {
        "id": "ANOM_GLOBAL_6",
        "dimension": "global",
        "penalty_points": 10,
        "target_score": "global",
        "conditions": [
            {"variable": "sector", "operator": "in", "value": ["Agriculture", "agriculture"]},
            {"variable": "market_score", "operator": ">=", "value": 70},
            {"variable": "GS2", "operator": "<=", "value": 25}
        ],
        "justification_template": (
            "Votre projet {sector} valide un marché fort ({market_score}/100) mais présente un score de risque hydrique critique ({GS2}/100). "
            "Produire et vendre massivement des produits agroalimentaires en Tunisie sans adresser la crise de l'eau actuelle menace directement "
            "votre continuité d'exploitation à court terme."
        ),
        "action_template": "Adoptez des technologies d'économie d'eau (circuit fermé, recyclage) en vous référant au plan d'urgence agricole de la note sectorielle {kb_link}.",
        "kb_link": "KB-APII-AGRO-005"
    }
]

# =====================================================================
# 5. FONCTIONS UTILS DE CALCUL ET D'ÉVALUATION D'ANOMALIES
# =====================================================================
def evaluate_condition(variable_value, operator, target_value):
    """Évalue une condition logique standard."""
    if operator == "==":
        return variable_value == target_value
    elif operator == "!=":
        return variable_value != target_value
    elif operator == ">=":
        return variable_value >= target_value
    elif operator == "<=":
        return variable_value <= target_value
    elif operator == ">":
        return variable_value > target_value
    elif operator == "<":
        return variable_value < target_value
    elif operator == "in":
        return variable_value in target_value
    return False

def check_anomalies(data_profile):
    """
    Parcourt toutes les anomalies et retourne la liste des anomalies déclenchées
    ainsi que les points de pénalité à déduire par score cible.
    
    data_profile doit être un dictionnaire contenant les valeurs réelles 
    des sous-scores (MS1, CO2, etc.), des scores composites (market_score, etc.)
    et des données de contexte (sector, stage, has_water_data, etc.).
    """
    triggered = []
    penalties = {
        "market": 0,
        "commercial_offer": 0,
        "innovation": 0,
        "scalability": 0,
        "green": 0,
        "global": 0
    }
    
    for rule in ANOMALY_RULES:
        conditions_met = True
        for cond in rule["conditions"]:
            var_name = cond["variable"]
            # Récupère la valeur du profil avec une valeur par défaut cohérente (False ou 0)
            var_val = data_profile.get(var_name, False if isinstance(cond["value"], bool) else 0)
            
            # Évaluation
            if not evaluate_condition(var_val, cond["operator"], cond["value"]):
                conditions_met = False
                break
                
        if conditions_met:
            triggered.append(rule)
            target = rule["target_score"]
            penalty = rule["penalty_points"]
            
            if target == "both_market_commercial":
                penalties["market"] += penalty
                penalties["commercial_offer"] += penalty
            elif target == "both_commercial_innovation":
                penalties["commercial_offer"] += penalty
                penalties["innovation"] += penalty
            else:
                penalties[target] += penalty
                
    return triggered, penalties

def get_adjusted_weights(dimension, sector=None):
    """
    Calcule et normalise les poids AHP d'une dimension en appliquant les bonus/malus sectoriels.
    """
    if dimension not in AHP_WEIGHTS:
        raise ValueError(f"Dimension inconnue : {dimension}")
        
    base_weights = AHP_WEIGHTS[dimension].copy()
    if not sector or sector not in SECTOR_ADJUSTMENTS:
        return base_weights
        
    adjustments = SECTOR_ADJUSTMENTS[sector].get(dimension, {})
    
    # 1. Appliquer les ajustements
    adjusted = {}
    for sub, w in base_weights.items():
        adj = adjustments.get(sub, 0.0)
        adjusted[sub] = max(0.0, w + adj)  # Pas de poids négatif
        
    # 2. Renormaliser les poids pour qu'ils somment à 1.0 (si nécessaire)
    total = sum(adjusted.values())
    if total > 0:
        for sub in adjusted:
            adjusted[sub] = round(adjusted[sub] / total, 4)
            
    return adjusted
