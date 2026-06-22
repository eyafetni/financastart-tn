import json
RULES_DATABASE = [
    # ── AGRICULTURE ──
    {
        "id": "ANOM_AGRI_SAISONNALITE_SANS_PLAN",
        "dimension": "strategy",
        "penalty_points": 12,
        "target_score": "commercial_offer_score",
        "conditions": [
            {"variable": "secteur", "operator": "==", "value": "agriculture_sylviculture_peche"},
            {"variable": "saisonnalite", "operator": "==", "value": "Oui, fortement saisonnière"},
            {"variable": "business_plan", "operator": "in", "value": ["absent", "incomplet"]}
        ],
        "justification_template": (
            "Risque de trésorerie saisonnier non couvert : Votre activité est fortement "
            "saisonnière mais votre modélisation financière est absente ou incomplète. "
            "Sans projection des flux de trésorerie inter-saisons, aucune banque tunisienne "
            "(BTS, BFPME) ne financera votre cycle d'exploitation agricole. La saisonnalité "
            "exige un plan de financement du fonds de roulement spécifique."
        ),
        "action_template": "Construisez un plan de trésorerie mensuel sur 18 mois intégrant les pics et creux saisonniers selon le modèle {kb_link}.",
        "kb_link": "KB-BTS-AGRO-CASHFLOW-006"
    },
    {
        "id": "ANOM_AGRI_CHAINE_FROID_REVENUS",
        "dimension": "financial_health",
        "penalty_points": 20,
        "target_score": "global",
        "conditions": [
            {"variable": "secteur", "operator": "==", "value": "agriculture_sylviculture_peche"},
            {"variable": "chaine_froid", "operator": "==", "value": False},
            {"variable": "chiffre_affaires", "operator": ">", "value": 50000}
        ],
        "justification_template": (
            "Incohérence logistique critique : Vous déclarez {chiffre_affaires} TND de chiffre "
            "d'affaires dans le secteur agro-alimentaire/pêche sans chaîne de froid "
            "opérationnelle ni accord logistique. La traçabilité et la conservation sont "
            "des obligations réglementaires ANCSEP et un prérequis à tout contrat de "
            "fourniture formalisé avec la GMS ou l'export."
        ),
        "action_template": "Contractualisez avec un prestataire frigorifique et documentez votre traçabilité selon le référentiel {kb_link}.",
        "kb_link": "KB-ANPE-AGRO-COLD-003"
    },

    # ── INDUSTRIE ──
    {
        "id": "ANOM_IND_ISO_SOUS_TRAITANCE_GAP",
        "dimension": "strategy",
        "penalty_points": 14,
        "target_score": "commercial_offer_score",
        "conditions": [
            {"variable": "secteur", "operator": "==", "value": "industrie_construction"},
            {"variable": "certification_iso", "operator": "==", "value": "absent"},
            {"variable": "sous_traitance", "operator": "==", "value": "Oui, contrats formels signés"}
        ],
        "justification_template": (
            "Dépendance contractuelle sans qualification qualité : Vous travaillez en "
            "sous-traitance avec des contrats formels, mais sans certification ISO. "
            "Les donneurs d'ordre industriels tunisiens et internationaux imposent "
            "la certification qualité comme critère d'homologation fournisseur. "
            "Votre position contractuelle ne résistera pas à un audit de supply chain."
        ),
        "action_template": "Lancez le processus ISO 9001 via l'INNORPI en priorisant les chapitres opérationnels selon {kb_link}.",
        "kb_link": "KB-INNORPI-ISO-IND-004"
    },

    # ── COMMERCE / LOGISTIQUE ──
    {
        "id": "ANOM_COM_RESEAU_SANS_BP",
        "dimension": "mindset_coachability",
        "penalty_points": 13,
        "target_score": "team_score",
        "conditions": [
            {"variable": "secteur", "operator": "==", "value": "commerce_transport_logistique"},
            {"variable": "reseau_distribution", "operator": "==", "value": "Oui, réseau structuré multi-canaux"},
            {"variable": "business_plan", "operator": "in", "value": ["absent", "incomplet"]}
        ],
        "justification_template": (
            "Réseau de distribution actif sans modélisation financière : Vous opérez "
            "un réseau commercial multi-canaux structuré mais sans business plan documenté. "
            "Sans projection de marges par canal et sans CAC par point de vente, "
            "vous gérez un réseau de distribution à l'aveugle. Les banques tunisiennes "
            "refuseront tout financement de croissance en l'absence de ce document."
        ),
        "action_template": "Modélisez la rentabilité de chaque canal (marges, CAC, rotation stock) avec le canevas financier {kb_link}.",
        "kb_link": "KB-BFPME-DISTRIB-FIN-005"
    },

    # ── TOURISME / SERVICES ──
    {
        "id": "ANOM_SERV_FIDELISATION_SAISONNALITE",
        "dimension": "strategy",
        "penalty_points": 14,
        "target_score": "commercial_offer_score",
        "conditions": [
            {"variable": "secteur", "operator": "==", "value": "service_tourisme"},
            {"variable": "saisonnalite", "operator": "==", "value": "Oui, fortement saisonnière"},
            {"variable": "fidelisation", "operator": "==", "value": "Non, clientèle de passage"}
        ],
        "justification_template": (
            "Double vulnérabilité saisonnière : Votre activité touristique est fortement "
            "saisonnière et repose exclusivement sur une clientèle de passage sans programme "
            "de fidélisation. Cette combinaison génère une dépendance totale aux flux "
            "conjoncturels sans aucun revenu garanti hors-saison. Le modèle n'est "
            "pas bancable sans lissage des revenus sur 12 mois."
        ),
        "action_template": "Développez une offre hors-saison (MICE, clientèle domestique) et un programme de fidélité numérique selon le modèle {kb_link}.",
        "kb_link": "KB-ONTT-OFFSEASON-004"
    },

    # ── TECH ──
    {
        "id": "ANOM_TECH_IP_SANS_ARTICLE12",
        "dimension": "strategy",
        "penalty_points": 22,
        "target_score": "product_tech_score",
        "conditions": [
            {"variable": "secteur", "operator": "==", "value": "tech_services_entreprise"},
            {"variable": "propriete_intellectuelle", "operator": "==", "value": False},
            {"variable": "mrr", "operator": "in", "value": ["fort", "faible"]},
            {"variable": "rne", "operator": "==", "value": True}
        ],
        "justification_template": (
            "Valeur technologique non protégée malgré des revenus actifs : Vous générez "
            "des revenus récurrents avec une solution tech mais sans aucune propriété "
            "intellectuelle protégée (brevet, marque, droits logiciels). L'Article 12 "
            "de la Loi Startup Act 2018-20 prévoit la prise en charge intégrale par "
            "l'État des frais de dépôt de brevet. Chaque mois sans dépôt est une "
            "fenêtre ouverte pour qu'un concurrent copie votre solution sans recours légal."
        ),
        "action_template": "Initiez le dépôt via le portail Startup Act (Art. 12) — zéro frais, traitement prioritaire. Procédure détaillée dans {kb_link}.",
        "kb_link": "KB-TACT-ART12-TECH-002"
    },
    {
        "id": "ANOM_TECH_MRR_FORT_SANS_ACCOMPAGNEMENT",
        "dimension": "ecosystem_integration",
        "penalty_points": 8,
        "target_score": "global",
        "conditions": [
            {"variable": "secteur", "operator": "==", "value": "tech_services_entreprise"},
            {"variable": "mrr", "operator": "==", "value": "fort"},
            {"variable": "accompagnement", "operator": "==", "value": "jamais"},
            {"variable": "financement", "operator": "==", "value": "aucun"}
        ],
        "justification_template": (
            "Traction forte isolée de l'écosystème — Opportunité d'accélération manquée : "
            "Vous générez plus de 5 000 TND/mois sans avoir jamais bénéficié d'un "
            "programme d'accompagnement ni de financement externe. À ce niveau de traction, "
            "vous êtes directement éligible aux programmes d'accélération Flat6Labs, "
            "ANAVA Growth ou Wamda, qui apportent capital, mentors et réseau régional. "
            "Rester hors écosystème à ce stade ralentit votre croissance de façon mesurable."
        ),
        "action_template": "Postulez aux programmes d'accélération Scale-up actifs (Flat6Labs Tunis, ANAVA Scale) avec le kit de dossier disponible dans {kb_link}.",
        "kb_link": "KB-ANAVA-SCALE-APPLY-001"
    },

    # ── CROSS-SECTORIEL ──
    {
        "id": "ANOM_GLOBAL_ACCOMP_TERMINE_STAGNATION",
        "dimension": "mindset_coachability",
        "penalty_points": 13,
        "target_score": "team_score",
        "conditions": [
            {"variable": "accompagnement", "operator": "==", "value": "termine"},
            {"variable": "stade_reel", "operator": "==", "value": "Ideation"},
            {"variable": "chiffre_affaires", "operator": "==", "value": 0}
        ],
        "justification_template": (
            "Post-incubation sans progression : Vous avez terminé un programme "
            "d'accompagnement mais votre diagnostic vous place toujours en 'Ideation' "
            "avec un CA nul. Soit le programme était inadapté, soit l'exécution "
            "post-programme a été nulle. Repasser en incubateur sans analyser les "
            "causes d'échec reproduira le même résultat."
        ),
        "action_template": "Réalisez un post-mortem de votre période d'incubation et identifiez vos 3 blockers d'exécution principaux selon le framework {kb_link}.",
        "kb_link": "KB-EXEC-POSTMORTEM-INCUB-001"
    },
    {
        "id": "ANOM_FRAUD_MEGALOMANIA_STAGE",
        "dimension": "mindset_coachability",
        "penalty_points": 30,
        "target_score": "team_score",
        "conditions": [
            {"variable": "stade_percu", "operator": "==", "value": "Growth"},
            {"variable": "stade_reel", "operator": "==", "value": "Ideation"}
        ],
        "justification_template": "Dissonance cognitive majeure : Vous percevez votre startup au stade de 'Growth', alors que les indicateurs objectifs vous placent en phase d''Ideation'.",
        "action_template": "Reprenez les fondamentaux de la validation de marché. Concentrez-vous sur la création d'un MVP plutôt que sur des projections de croissance illusoires.",
        "kb_link": "KB-MINDSET-STAGES-012"
    },
    {
        "id": "ANOM_FRAUD_IMPOSSIBLE_SCALE",
        "dimension": "financial_health",
        "penalty_points": 40,
        "target_score": "global",
        "conditions": [
            {"variable": "chiffre_affaires", "operator": ">", "value": 1000000},
            {"variable": "equipe", "operator": "==", "value": "solo"},
            {"variable": "stade_reel", "operator": "in", "value": ["Ideation", "Concept"]}
        ],
        "justification_template": "Alerte fraude / Données suspectes : Un chiffre d'affaires déclaré de {chiffre_affaires} TND est opérationnellement impossible pour un fondateur 'solo' dont le projet est évalué au stade {stade_reel}.",
        "action_template": "Veuillez auditer et corriger vos déclarations financières.",
        "kb_link": "KB-FIN-AUDIT-004"
    },
    {
        "id": "ANOM_LEGAL_IMPOSSIBLE_GRANT",
        "dimension": "financial_health",
        "penalty_points": 25,
        "target_score": "commercial_offer_score",
        "conditions": [
            {"variable": "financement", "operator": "==", "value": "subventions"},
            {"variable": "rne", "operator": "==", "value": False}
        ],
        "justification_template": "Incohérence déclarative : Vous indiquez être financé par des 'subventions' tout en n'ayant aucune existence légale (RNE: false). Les bailleurs tunisiens n'octroient aucune subvention à des entités non enregistrées.",
        "action_template": "Clarifiez la nature de vos fonds et régularisez votre statut juridique pour accéder aux véritables subventions d'État.",
        "kb_link": "KB-FIN-GRANTS-008"
    },
    {
        "id": "ANOM_ECO_GREEN_NO_SUPPORT",
        "dimension": "ecosystem_integration",
        "penalty_points": 10,
        "target_score": "global",
        "conditions": [
            {"variable": "secteur", "operator": "==", "value": "green"},
            {"variable": "accompagnement", "operator": "==", "value": "jamais"}
        ],
        "justification_template": "Opportunité gâchée dans le secteur {secteur} : Vous n'êtes intégré à aucun programme d'accompagnement alors que l'écosystème GreenTech tunisien propose de nombreuses structures dédiées.",
        "action_template": "Postulez aux cohortes d'incubation spécialisées en économie verte et circulaire (ANPE, CITET, etc.).",
        "kb_link": "KB-ECO-GREEN-005"
    },
    {
        "id": "ANOM_TECH_GHOST_INNOVATION",
        "dimension": "product_tech_score",
        "penalty_points": 15,
        "target_score": "product_tech_score",
        "conditions": [
            {"variable": "innovation_niveau", "operator": "==", "value": "forte"},
            {"variable": "business_plan", "operator": "==", "value": "non_commence"},
            {"variable": "stade_reel", "operator": "==", "value": "Ideation"}
        ],
        "justification_template": "Vœu pieux technologique : Revendiquer une innovation de niveau '{innovation_niveau}' au stade de simple idée, sans le moindre début de formalisation stratégique (Business Plan non commencé), décrédibilise votre projet.",
        "action_template": "Prouvez la faisabilité de votre innovation. Rédigez un document d'architecture technique ou un cahier des charges fonctionnel.",
        "kb_link": "KB-TECH-PROOF-003"
    },
    {
        "id": "ANOM_STRAT_WASTED_ACCOMPANIMENT",
        "dimension": "mindset_coachability",
        "penalty_points": 12,
        "target_score": "team_score",
        "conditions": [
            {"variable": "accompagnement", "operator": "==", "value": "en_cours"},
            {"variable": "business_plan", "operator": "==", "value": "non_commence"},
            {"variable": "stade_reel", "operator": "in", "value": ["Market Validation", "Growth"]}
        ],
        "justification_template": "Inefficacité de l'accompagnement : Vous êtes suivi par une structure, mais votre Business Plan n'a pas débuté alors que vous êtes au stade {stade_reel}. Cela traduit une difficulté à exécuter les jalons stratégiques.",
        "action_template": "Exigez de votre incubateur des ateliers intensifs sur la modélisation financière.",
        "kb_link": "KB-EXEC-MENTORSHIP-009"
    },
    {
        "id": "ANOM_PERF_SCORE_PARADOX",
        "dimension": "strategy",
        "penalty_points": 20,
        "target_score": "global",
        "conditions": [
            {"variable": "score_diagnostic", "operator": "<", "value": 20},
            {"variable": "stade_percu", "operator": "in", "value": ["Market Validation", "Growth"]}
        ],
        "justification_template": "Signal de détresse structurelle : Vous évaluez le projet à un stade avancé ({stade_percu}), mais votre score de viabilité s'effondre à {score_diagnostic}/100. Vos fondations sont extrêmement fragiles.",
        "action_template": "Faites une pause opérationnelle (Freeze). Révisez chaque bloc défaillant de votre diagnostic avant de brûler davantage de capital.",
        "kb_link": "KB-STRAT-PIVOT-015"
    },
    {
        "id": "ANOM_TEAM_SOLO_FATIGUE",
        "dimension": "team_viability",
        "penalty_points": 10,
        "target_score": "team_score",
        "conditions": [
            {"variable": "equipe", "operator": "==", "value": "solo"},
            {"variable": "stade_reel", "operator": "==", "value": "Growth"}
        ],
        "justification_template": "Risque de Burnout : Gérer seul une startup en phase de 'Growth' est un goulot d'étranglement majeur (Key-Man Risk) rédhibitoire pour les investisseurs.",
        "action_template": "Recrutez un bras droit opérationnel (COO) ou ouvrez votre capital pour intégrer un co-fondateur.",
        "kb_link": "KB-TEAM-SCALING-007"
    },
    {
        "id": "ANOM_FIN_SUSPICIOUS_SPEED",
        "dimension": "financial_health",
        "penalty_points": 18,
        "target_score": "global",
        "conditions": [
            {"variable": "chiffre_affaires", "operator": ">", "value": 500000},
            {"variable": "anciennete_revenus", "operator": "==", "value": "Moins d'un an"},
            {"variable": "innovation_niveau", "operator": "==", "value": "faible"}
        ],
        "justification_template": "Hyper-croissance inexpliquée : Générer plus de 500k TND en moins d'un an avec une innovation '{innovation_niveau}' indique un modèle de PME classique de négoce/service, et non une startup technologique scalable.",
        "action_template": "Orientez-vous plutôt vers des fonds de Private Equity classiques ou le secteur bancaire tunisien.",
        "kb_link": "KB-FIN-SME-VS-STARTUP-001"
    },
    {
        "id": "ANOM_STRAT_MISSING_GAP_EXPLANATION",
        "dimension": "mindset_coachability",
        "penalty_points": 5,
        "target_score": "global",
        "conditions": [
            {"variable": "gap_detecte", "operator": "==", "value": True},
            {"variable": "gap_explication", "operator": "==", "value": None}
        ],
        "justification_template": "Anomalie d'audit : Le système détecte une faille logique profonde dans vos réponses, mais l'origine du biais n'est pas qualifiée.",
        "action_template": "Repassez le diagnostic avec intégrité en vous basant sur des faits accomplis.",
        "kb_link": "KB-MINDSET-HONESTY-002"
    },
    {
        "id": "ANOM_ECO_REGIONAL_FUNDS_MISSED",
        "dimension": "financial_health",
        "penalty_points": 10,
        "target_score": "commercial_offer_score",
        "conditions": [
            {"variable": "localisation", "operator": "not_in", "value": ["Tunis", "Autre région"]},
            {"variable": "financement", "operator": "==", "value": "aucun"},
            {"variable": "rne", "operator": "==", "value": True}
        ],
        "justification_template": "Leviers régionaux inexploités : Vous êtes légalement constitué (RNE valide) à {localisation} mais ne bénéficiez d'aucun financement. Vous passez à côté de primes de développement régional spécifiques (PDRI).",
        "action_template": "Sollicitez le bureau régional de l'APII de {localisation} pour déposer un dossier de prime d'investissement régional.",
        "kb_link": "KB-FIN-REGIONAL-006"
    },
    {
        "id": "ANOM_TECH_HIGH_INNOV_NO_FUNDS",
        "dimension": "strategy",
        "penalty_points": 12,
        "target_score": "product_tech_score",
        "conditions": [
            {"variable": "innovation_niveau", "operator": "==", "value": "forte"},
            {"variable": "financement", "operator": "==", "value": "aucun"}
        ],
        "justification_template": "Incohérence R&D : Développer une innovation de niveau '{innovation_niveau}' nécessite du capital patient. Revendiquer cela en étant totalement autofinancé est hautement improbable.",
        "action_template": "Sécurisez vos avancées par un financement d'amorçage (Bourse d'innovation de Smart Capital, subvention ANPR).",
        "kb_link": "KB-TECH-RD-FUNDING-010"
    },
    {
        "id": "ANOM_EXEC_STAGNATION_RISK",
        "dimension": "mindset_coachability",
        "penalty_points": 15,
        "target_score": "global",
        "conditions": [
            {"variable": "stade_reel", "operator": "==", "value": "Ideation"},
            {"variable": "accompagnement", "operator": "==", "value": "en_cours"},
            {"variable": "business_plan", "operator": "==", "value": "non_commence"}
        ],
        "justification_template": "Syndrome de l'éternel incubé : Vous êtes accompagné, toujours au stade d'idée, et sans business plan. Vous consommez des ressources d'accompagnement sans produire d'output concret.",
        "action_template": "Fixez-vous un ultimatum : Sortez un prototype et un business plan fonctionnel sous 30 jours.",
        "kb_link": "KB-EXEC-VELOCITY-008"
    },
    {
        "id": "ANOM_FRAUD_ZERO_TRACTION_GROWTH",
        "dimension": "strategy",
        "penalty_points": 25,
        "target_score": "commercial_offer_score",
        "conditions": [
            {"variable": "stade_percu", "operator": "==", "value": "Growth"},
            {"variable": "chiffre_affaires", "operator": "==", "value": 0}
        ],
        "justification_template": "Illusion de croissance : Revendiquer un stade de 'Growth' avec un chiffre d'affaires strictement égal à zéro est un non-sens absolu.",
        "action_template": "Redescendez vos ambitions à la phase de 'Market Validation' et concentrez-vous sur l'acquisition de votre premier client payant.",
        "kb_link": "KB-STRAT-GROWTH-013"
    },
    {
        "id": "ANOM_TEAM_NO_TECH_COFOUNDER_INNOVATION",
        "dimension": "team_viability",
        "penalty_points": 18,
        "target_score": "team_score",
        "conditions": [
            {"variable": "innovation_niveau", "operator": "==", "value": "forte"},
            {"variable": "equipe", "operator": "==", "value": "solo"}
        ],
        "justification_template": "Déficit structurel R&D : Construire une innovation '{innovation_niveau}' en tant que fondateur 'solo' crée un point de défaillance unique critique si vous n'avez pas de profil CTO internalisé.",
        "action_template": "Associez-vous immédiatement à un ingénieur ou un profil technique avec des parts au capital (Equity).",
        "kb_link": "KB-TEAM-CTO-002"
    },
    {
        "id": "ANOM_STRAT_MISALIGNED_FUNDING",
        "dimension": "financial_health",
        "penalty_points": 10,
        "target_score": "commercial_offer_score",
        "conditions": [
            {"variable": "financement_recommande", "operator": "==", "value": "APII / ANPE"},
            {"variable": "stade_percu", "operator": "==", "value": "Growth"}
        ],
        "justification_template": "Recommandation désalignée : Votre profil pointe vers des mécanismes d'appui classiques ('{financement_recommande}'), mais vous visez une phase de '{stade_percu}'. Ces guichets ne sont pas calibrés pour le capital-risque intensif.",
        "action_template": "Préparez votre Data Room financière et commencez à approcher les fonds d'investissement (VCs) de la place.",
        "kb_link": "KB-FIN-VC-009"
    }
]

# ==========================================
# 2. FONCTIONS INTERNES DU MOTEUR
# ==========================================

def extract_and_flatten_context(entrepreneur_json):
    """Extrait et aplatit les variables du payload pour l'évaluation."""
    profil = entrepreneur_json.get("profil_complet", {}) or {}
    ca_brut = profil.get("chiffre_affaires")
    
    flat_data = {
        "entrepreneur_id": entrepreneur_json.get("entrepreneur_id"),
        "stade_reel": entrepreneur_json.get("stade_reel"),
        "stade_percu": entrepreneur_json.get("stade_percu"),
        "score_diagnostic": entrepreneur_json.get("score_diagnostic", 0),
        "gap_detecte": entrepreneur_json.get("gap_detecte", False),
        "gap_explication": entrepreneur_json.get("gap_explication"),
        "secteur": entrepreneur_json.get("secteur"),
        "localisation": entrepreneur_json.get("localisation"),
        "financement_recommande": entrepreneur_json.get("financement_recommande"),
        
        "equipe": profil.get("equipe"),
        "rne": profil.get("rne", False),
        "chiffre_affaires": float(ca_brut) if ca_brut is not None else 0.0,
        "anciennete_revenus": profil.get("anciennete_revenus"),
        "business_plan": profil.get("business_plan"),
        "innovation_niveau": profil.get("innovation_niveau"),
        "accompagnement": profil.get("accompagnement"),
        "financement": profil.get("financement")
    }
    return flat_data

def evaluate_condition(actual_val, operator, target_val):
    """Évalue une condition unitaire selon son opérateur."""
    if operator == "==":
        return actual_val == target_val
    elif operator == "!=":
        return actual_val != target_val
    elif operator == ">":
        return actual_val is not None and actual_val > target_val
    elif operator == "<":
        return actual_val is not None and actual_val < target_val
    elif operator == "in":
        return actual_val in target_val if target_val else False
    elif operator == "not_in":
        return actual_val not in target_val if target_val else True
    return False

# ==========================================
# 3. INTERFACE POINT D'ENTRÉE DU MODULE
# ==========================================

def extract_anomalies(payload):
    """
    Exécute le catalogue complet des règles sur le payload (dict ou chaîne JSON).
    Retourne la liste des anomalies détectées formatée pour l'orchestrateur principal.
    """
    # Désérialisation si c'est une chaîne JSON
    entrepreneur_json = json.loads(payload) if isinstance(payload, str) else payload
    
    context = extract_and_flatten_context(entrepreneur_json)
    anomalies_detectees = []
    
    for rule in RULES_DATABASE:
        match_rule = True
        
        # Évaluation des conditions de la règle
        for cond in rule["conditions"]:
            var_name = cond["variable"]
            operator = cond["operator"]
            target_value = cond["value"]
            
            actual_value = context.get(var_name)
            
            if not evaluate_condition(actual_value, operator, target_value):
                match_rule = False
                break
                
        # Formatage de l'anomalie si le profil déclenche la règle
        if match_rule:
            try:
                justification = rule["justification_template"].format(**context)
                action = rule["action_template"].format(**context)
            except KeyError:
                justification = rule["justification_template"]
                action = rule["action_template"]
                
            # Remplacement de 'description' par 'justification' dans l'output
            anomalies_detectees.append({
                "id": rule["id"],
                "justification": justification,  # Changement effectué ici
                "dimension": rule["dimension"],
                "penalty_points": rule["penalty_points"],
                "target_score": rule["target_score"],
                "action": action,
                "kb_link": rule["kb_link"]
            })
            
    return anomalies_detectees