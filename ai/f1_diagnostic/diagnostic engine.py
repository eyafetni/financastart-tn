"""
AINS Hackathon 2026 – Feature 1
Moteur de Diagnostic Adaptatif — Questionnaire Intelligent
Classifie la vraie maturité entrepreneuriale (pas celle déclarée)
"""

import json
import uuid
from datetime import datetime



STADES = {
    1: {"nom": "Ideation", "description": "Idée sans validation ni équipe complète", "financement": "Love money / Concours", "score_min": 0, "score_max": 15},
    2: {"nom": "Market Validation", "description": "Premiers clients / traction naissante", "financement": "Microfinance / BTS", "score_min": 16, "score_max": 30},
    3: {"nom": "Structuration", "description": "Structure juridique / business plan", "financement": "APII / ANPE", "score_min": 31, "score_max": 50},
    4: {"nom": "Fundraising", "description": "Dossier bancable en construction", "financement": "BFPME / Startup Act", "score_min": 51, "score_max": 65},
    5: {"nom": "Launch Planning", "description": "Produit validé / prêt à lever", "financement": "Capital risque / ANAVA", "score_min": 66, "score_max": 80},
    6: {"nom": "Growth", "description": "Revenus existants / expansion", "financement": "Lignes bancaires / AFD / EU", "score_min": 81, "score_max": 100},
}



SECTEURS = {
    "agriculture_sylviculture_peche": {
        "label": "Agriculture / Sylviculture / Pêche",
        "mots_cles": [
            "agri", "agro", "agricol", "agroaliment", "food", "sylvicult","sylvi",
            "forêt","foret", "peche", "pêche", "élevage", "elevage",
            "cultures", "céréales", "cereales", "maraich", "arboricult","aqua",
            "aquaculture", "halieutique" , "argi-tech", "agri-tech", "agritech", "foodtech"
        ]
    },
    "industrie_construction": {
        "label": "Industrie / Construction",
        "mots_cles": [
            "indus", "industrie", "manufactur", "usine", "fabricat", "product","prod",
            "construct", "bâtiment", "batiment","trav", "travaux", "btp","immo",
            "immobilier", "génie civil", "genie civil", "matériaux", "materiaux",
            "mécanique", "mecanique", "metal","metallurgi", "chimie","chimique","textil",
            "plasturgi", "automobile", "aéronautique", "aeronautique", "énergie", "energie",
        ]
    },
    "commerce_transport_logistique": {
        "label": "Commerce / Transport / Logistique",
        "mots_cles": [
            "commerce", "vente", "retail", "boutique", "distribut","logistique",
            "transport", "livraison", "fret", "import","export","supply chain", "supply", "chain",
            "entrepôt", "entrepot", "transit","grossiste","detail","gros", "détaillant",
            "detaillant","e-commerce", "ecommerce", "marketplace", "transport",
            "mobilité", "mobilite", "last mile", "last-mile"
        ]
    },
    "service_tourisme": {
        "label": "Service / Tourisme",
        "mots_cles": [
            "service", "conseil", "formation", "consulting", "tourisme",
            "hôtel", "hotel", "restaurant", "café", "cafe", "restaurat",
            "hébergement", "hebergement", "voyage", "agence de voyage",
            "bien-être", "bien être", "santé", "sante", "éducation", "education",
            "immobilier service", "nettoyage", "maintenance",
        ]
    },
    "tech_services_entreprise": {
        "label": "Technologie et Services Entreprise",
        "mots_cles": [
            "tech", "digital", "logiciel", "app", "web", "ia", "ai", "saas",
            "software", "développement", "developpement", "informatique",
            "cyber","cybersecurité", "cybersécurité", "cloud", "data", "fintech",
            "edtech", "healthtech", "b2b", "erp", "crm", "automatisation",
            "robotique", "iot", "blockchain", "marketplace","platform", "plateforme"
        ]
    },
}


DIMENSIONS_F2 = {
    "MKT": "Marché & Traction",
    "COM": "Offre Commerciale",
    "INO": "Innovation & Différenciation",
    "SCA": "Scalabilité & Croissance",
    "ESG": "Impact & Environnement"
}

QUESTIONS_F2 = {
    "type_cible": {
        "id": "type_cible",
        "dimension": "MKT",
        "question": "Quel est le modèle d'interaction et la cible prioritaire de votre solution ?",
        "options": [
            {"index": 0, "valeur": "B2C",            "texte": "Grand public / Utilisateurs individuels"},
            {"index": 1, "valeur": "B2B_SME",         "texte": "Petites et Moyennes Entreprises / Professionnels indépendants"},
            {"index": 2, "valeur": "B2B_Enterprise",  "texte": "Grands Comptes / Groupes Industriels / Corporates"},
            {"index": 3, "valeur": "B2B2C",           "texte": "Modèle intermédiaire (via un partenaire pour toucher le client final)"},
            {"index": 4, "valeur": "B2G",             "texte": "Gouvernements / Ministères / Collectivités Publiques"}
        ]
    },
    "potentiel_financier_marche": {
        "id": "potentiel_financier_marche",
        "dimension": "MKT",
        "question": "Quelle est la valeur financière annuelle estimée de votre marché immédiatement accessible (SOM) ?",
        "options": [
            {"index": 0, "valeur": "niche_ultra_locale",           "texte": "Marché de niche très restreint (Moins de 1M DT / an)"},
            {"index": 1, "valeur": "marche_local_limite",          "texte": "Marché local avec un plafond rapide (1M à 5M DT / an)"},
            {"index": 2, "valeur": "marche_national_intermediaire", "texte": "Marché national significatif (5M à 20M DT / an)"},
            {"index": 3, "valeur": "marche_regional_scalable",     "texte": "Marché à fort potentiel d'extension régionale (20M à 50M DT / an)"},
            {"index": 4, "valeur": "marche_global_massif",         "texte": "Marché de masse international (Plus de 50M DT / an)"}
        ]
    },
    "intensite_concurrence": {
        "id": "intensite_concurrence",
        "dimension": "MKT",
        "question": "Comment se structure l'intensité concurrentielle sur votre segment cible ?",
        "options": [
            {"index": 0, "valeur": "hyper_competition",  "texte": "Marché saturé, guerre des prix féroce avec des géants installés"},
            {"index": 1, "valeur": "forte_concurrence",  "texte": "Plusieurs acteurs directs bien financés et identifiés"},
            {"index": 2, "valeur": "marche_partage",     "texte": "Concurrence modérée, fragmentation permettant de prendre des parts"},
            {"index": 3, "valeur": "faible_concurrence", "texte": "Marché émergent, solutions alternatives indirectes ou obsolètes"},
            {"index": 4, "valeur": "ocean_bleu",         "texte": "Pionnier absolu, aucun concurrent direct sur cette proposition de valeur"}
        ]
    },
    "niveau_traction": {
        "id": "niveau_traction",
        "dimension": "MKT",
        "question": "Quel est l'état réel et mesurable de votre validation commerciale sur le terrain ?",
        "options": [
            {"index": 0, "valeur": "ideation_pure",        "texte": "Zéro utilisateur, validation théorique uniquement"},
            {"index": 1, "valeur": "premiers_testeurs",    "texte": "Bêta-testeurs actifs ou utilisateurs pilotes non-payants"},
            {"index": 2, "valeur": "traction_initiale",    "texte": "Premières transactions ou contrats signés (Preuve de Concept payante)"},
            {"index": 3, "valeur": "traction_significative","texte": "Portefeuille clients en croissance régulière et acquisition active"},
            {"index": 4, "valeur": "croissance_organique", "texte": "Revenus récurrents stables (MRR/ARR) avec fort taux de rétention"}
        ]
    },
    "modele_revenu": {
        "id": "modele_revenu",
        "dimension": "MKT",
        "question": "Où en est la validation empirique de votre mécanisme de capture de valeur ?",
        "options": [
            {"index": 0, "valeur": "non_defini",           "texte": "Modèle de revenus flou, gratuité totale sans stratégie de conversion"},
            {"index": 1, "valeur": "transactionnel_standard","texte": "Vente unique (one-shot), revenus dépendants de chaque acte de vente"},
            {"index": 2, "valeur": "commission_marketplace","texte": "Modèle basé sur des frais de transaction ou de mise en relation"},
            {"index": 3, "valeur": "abonnement_saas",      "texte": "Revenus récurrents prévisibles (SaaS, abonnements périodiques)"},
            {"index": 4, "valeur": "multi_stream_optimise", "texte": "Modèle hybride validé (Abonnement + Commissions + Options premium)"}
        ]
    },
    "business_plan_f2": {
        "id": "business_plan_f2",
        "dimension": "COM",
        "question": "Quel est le niveau de maturité de votre modélisation financière et stratégique ?",
        "options": [
            {"index": 0, "valeur": "non_commence",          "texte": "Aucune projection financière ni business plan formalisé"},
            {"index": 1, "valeur": "ebauche_initiale",      "texte": "Structure de coûts basique estimée sans métriques clés (LTV, CAC)"},
            {"index": 2, "valeur": "en_cours_de_validation","texte": "Business Model Canvas complet avec prévisions financières à 3 ans"},
            {"index": 3, "valeur": "valide_equipe",         "texte": "Modèle financier complet validé par des mentors ou experts internes"},
            {"index": 4, "valeur": "valide_audite_externe", "texte": "Plan d'affaires validé et audité par des investisseurs ou cabinets tiers"}
        ]
    },
    "maturite_produit": {
        "id": "maturite_produit",
        "dimension": "COM",
        "question": "Où se situe votre solution sur l'échelle de développement technique ?",
        "options": [
            {"index": 0, "valeur": "concept_wireframe",     "texte": "Maquettes graphiques, storyboards ou slides de présentation uniquement"},
            {"index": 1, "valeur": "prototype_poc",         "texte": "Prototype de laboratoire fonctionnel mais instable (Preuve de Concept)"},
            {"index": 2, "valeur": "mvp_valide",            "texte": "Produit Minimum Viable déployé et testé en conditions réelles"},
            {"index": 3, "valeur": "industrialise_stable",  "texte": "Produit fini, stable, sécurisé et prêt pour un déploiement massif"},
            {"index": 4, "valeur": "scalable_architecture", "texte": "Produit hautement disponible, API-fié et prêt pour l'international"}
        ]
    },
    "strategie_prix": {
        "id": "strategie_prix",
        "dimension": "COM",
        "question": "Comment votre structure tarifaire (pricing) est-elle perçue par le marché ?",
        "options": [
            {"index": 0, "valeur": "arbitraire",          "texte": "Prix fixé au hasard ou à l'intuition sans étude terrain"},
            {"index": 1, "valeur": "cost_plus_margin",    "texte": "Tarification basique calculée uniquement sur les coûts + une marge fixe"},
            {"index": 2, "valeur": "alignement_concurrence","texte": "Prix calqué horizontalement sur les solutions existantes"},
            {"index": 3, "valeur": "valeur_percue",       "texte": "Prix indexé sur le ROI (Retour sur Investissement) généré pour le client"},
            {"index": 4, "valeur": "dynamique_usage",     "texte": "Pricing hautement optimisé à l'usage, testé et validé par des cohortes"}
        ]
    },
    "alignement_besoins": {
        "id": "alignement_besoins",
        "dimension": "COM",
        "question": "À quel point votre produit résout-il un problème critique (Pain Point) pour votre cible ?",
        "options": [
            {"index": 0, "valeur": "aucun_interet",       "texte": "Le problème ciblé n'intéresse pas le marché ou n'existe pas"},
            {"index": 1, "valeur": "nice_to_have",        "texte": "Outil de confort secondaire, déclenche peu d'intentions d'achat"},
            {"index": 2, "valeur": "important_non_urgent","texte": "Problème réel mais le client remet souvent l'achat à plus tard"},
            {"index": 3, "valeur": "must_have_urgent",    "texte": "Besoin critique, les clients recherchent activement une solution"},
            {"index": 4, "valeur": "total_pmf",           "texte": "Dépendance forte au produit, rétention exceptionnelle (Product-Market Fit validé)"}
        ]
    },
    "nouveaute_locale": {
        "id": "nouveaute_locale",
        "dimension": "INO",
        "question": "Quelle est l'originalité de votre positionnement sur votre zone géographique cible ?",
        "options": [
            {"index": 0, "valeur": "copie_conforme",    "texte": "Réplication exacte d'un service déjà omniprésent localement"},
            {"index": 1, "valeur": "amelioration_mineure","texte": "Même concept que les concurrents avec une simple option en plus"},
            {"index": 2, "valeur": "adaptation_locale",  "texte": "Importation et adaptation d'un concept étranger inexistant ici"},
            {"index": 3, "valeur": "premiere_nationale", "texte": "Concept totalement inédit et pionnier à l'échelle du pays"},
            {"index": 4, "valeur": "disruption_globale", "texte": "Innovation de rupture sans équivalent à l'échelle internationale"}
        ]
    },
    "intensite_tech": {
        "id": "intensite_tech",
        "dimension": "INO",
        "question": "Quelle est l'épaisseur technologique sous-jacente à votre solution ?",
        "options": [
            {"index": 0, "valeur": "no_code_standard",       "texte": "Assemblage d'outils tiers existants sans aucun code propriétaire"},
            {"index": 1, "valeur": "developpement_classique", "texte": "Application Web ou Mobile standard sans complexité technique"},
            {"index": 2, "valeur": "integration_avancee",    "texte": "Système connecté avec des architectures Cloud et intégration poussée d'API"},
            {"index": 3, "valeur": "ia_proprietaire",        "texte": "Algorithmes d'Intelligence Artificielle ou traitement de données propriétaires"},
            {"index": 4, "valeur": "deeptech_science",       "texte": "DeepTech issue de laboratoires de recherche, biotechnologies ou hardware complexe"}
        ]
    },
    "barrieres_entree": {
        "id": "barrieres_entree",
        "dimension": "INO",
        "question": "De quel avantage défensif disposez-vous pour empêcher une copie rapide par un concurrent ?",
        "options": [
            {"index": 0, "valeur": "aucune_barriere",       "texte": "N'importe quel développeur peut copier le concept en deux semaines"},
            {"index": 1, "valeur": "avance_operationnelle", "texte": "Simple avantage de rapidité d'exécution ou de communication"},
            {"index": 2, "valeur": "moat_commercial",       "texte": "Exclusivités commerciales, partenariats clés ou base de données qualifiée"},
            {"index": 3, "valeur": "effet_de_reseau",       "texte": "Barrière forte grâce aux effets de réseau (plus d'utilisateurs = incopiable)"},
            {"index": 4, "valeur": "propriete_intellectuelle","texte": "Brevet déposé, secret industriel strict ou technologie hautement complexe"}
        ]
    },
    "degre_rupture": {
        "id": "degre_rupture",
        "dimension": "INO",
        "question": "Comment votre innovation modifie-t-elle les habitudes des acteurs du secteur ?",
        "options": [
            {"index": 0, "valeur": "evolution_nulle",          "texte": "L'utilisateur ne change absolument rien à ses processus actuels"},
            {"index": 1, "valeur": "optimisation_incrementale","texte": "Simple gain de temps ou économie marginale sur un processus existant"},
            {"index": 2, "valeur": "transformation_process",   "texte": "Modification visible des habitudes de travail ou de consommation"},
            {"index": 3, "valeur": "forte_substitution",       "texte": "Rend obsolètes les anciennes méthodes pour une grande partie des utilisateurs"},
            {"index": 4, "valeur": "changement_paradigme",     "texte": "Crée un nouvel usage ou une nouvelle industrie à part entière"}
        ]
    },
    "replicabilite": {
        "id": "replicabilite",
        "dimension": "SCA",
        "question": "Quel est le niveau de complexité pour déployer votre solution sur un nouveau territoire ?",
        "options": [
            {"index": 0, "valeur": "dependance_physique_stricte",   "texte": "Nécessite des infrastructures lourdes, des locaux et des équipes physiques"},
            {"index": 1, "valeur": "contraintes_reglementaires",    "texte": "Soumis à des autorisations légales longues et complexes par pays"},
            {"index": 2, "valeur": "deploiement_operationnel_modere","texte": "Nécessite l'ouverture d'un bureau réduit et du support local"},
            {"index": 3, "valeur": "facilement_replicable",         "texte": "Processus hautement standardisés, déploiement rapide sans gros ajustements"},
            {"index": 4, "valeur": "immediate_pure_player",         "texte": "Modèle 100% digital, expansion internationale instantanée sans barrière"}
        ]
    },
    "independance_manuelle": {
        "id": "independance_manuelle",
        "dimension": "SCA",
        "question": "Comment évolue votre masse salariale par rapport à l'augmentation de vos clients ?",
        "options": [
            {"index": 0, "valeur": "modele_artisanal",    "texte": "Progression strictement linéaire (Plus de clients = besoin d'autant de staff)"},
            {"index": 1, "valeur": "semi_automatise",     "texte": "L'humain reste au cœur de la livraison de valeur, goulot d'étranglement fort"},
            {"index": 2, "valeur": "paliers_de_croissance","texte": "Recrutements par vagues nécessaires pour soutenir la charge technique"},
            {"index": 3, "valeur": "haute_automatisation","texte": "L'infrastructure gère la hausse, le staff n'augmente que pour le support"},
            {"index": 4, "valeur": "zero_marginal_cost",  "texte": "Automatisation totale, coût marginal de livraison d'un nouveau client quasi nul"}
        ]
    },
    "couts_deploiement": {
        "id": "couts_deploiement",
        "dimension": "SCA",
        "question": "Quel est le niveau d'investissement financier (CAPEX) requis pour onboarder un grand volume de clients ?",
        "options": [
            {"index": 0, "valeur": "capex_prohibitif",          "texte": "Nécessite des millions d'investissements matériels ou marketing préalables"},
            {"index": 1, "valeur": "investissements_lourds",    "texte": "Besoin de lever des fonds massifs pour financer le fonds de roulement"},
            {"index": 2, "valeur": "besoin_modere",             "texte": "Coûts d'acquisition d'infrastructure absorbables par la marge opérationnelle"},
            {"index": 3, "valeur": "faibles_couts",             "texte": "Coût de configuration initial très faible pour chaque groupe de clients"},
            {"index": 4, "valeur": "croissance_organique_gratuite","texte": "Coût marginal d'infrastructure transparent, autofinancement par le volume"}
        ]
    },
    "potentiel_geo": {
        "id": "potentiel_geo",
        "dimension": "SCA",
        "question": "Quelle est l'échelle géographique inscrite dans l'architecture même de votre projet ?",
        "options": [
            {"index": 0, "valeur": "hyper_local",      "texte": "Solution viable uniquement à l'échelle d'une ville ou communauté restreinte"},
            {"index": 1, "valeur": "regional",         "texte": "Portée limitée à quelques gouvernorats ou régions spécifiques"},
            {"index": 2, "valeur": "national",         "texte": "Conçu pour couvrir l'intégralité du territoire national uniquement"},
            {"index": 3, "valeur": "continental_mena", "texte": "Adapté nativement pour cibler l'Afrique du Nord et le Moyen-Orient (MENA)"},
            {"index": 4, "valeur": "global_born_global","texte": "Produit 'Born Global', conçu sans frontières géographiques ni culturelles"}
        ]
    },
    "climat_air": {
        "id": "climat_air",
        "dimension": "ESG",
        "question": "Quelle est la contribution directe ou indirecte de votre entreprise sur l'empreinte carbone ?",
        "options": [
            {"index": 0, "valeur": "impact_negatif_lourd",    "texte": "Activité fortement carbonée sans politique de réduction ou compensation"},
            {"index": 1, "valeur": "impact_negatif_modere",   "texte": "Génère des émissions de GES mais des efforts d'optimisation sont en cours"},
            {"index": 2, "valeur": "neutralite_passive",      "texte": "Impact neutre par défaut (services numériques de base non éco-conçus)"},
            {"index": 3, "valeur": "impact_positif_mesurable","texte": "Réduction active et prouvée des émissions (efficacité, circuits courts)"},
            {"index": 4, "valeur": "impact_regeneratif",      "texte": "Modèle de captation carbone ou solution réduisant l'impact de tout un secteur"}
        ]
    },
    "donnees_eau_fournies": {
        "id": "donnees_eau_fournies",
        "dimension": "ESG",
        "question": "Quel niveau d'intelligence et de précision intégrez-vous dans la gestion ou la préservation de l'eau ?",
        "options": [
            {"index": 0, "valeur": "aucune_mesure",             "texte": "Consommation d'eau non mesurée, aucune conscience de la ressource"},
            {"index": 1, "valeur": "estimation_theorique",      "texte": "Évaluation de l'empreinte eau basée sur des moyennes théoriques floues"},
            {"index": 2, "valeur": "suivi_manuel_partiel",      "texte": "Relevés réguliers mais manuels de la consommation avec correctifs tardifs"},
            {"index": 3, "valeur": "suivi_digital_temps_reel",  "texte": "Monitoring digital continu (IoT/Capteurs) avec alertes instantanées"},
            {"index": 4, "valeur": "optimisation_ia_predictive","texte": "Pilotage automatisé par IA prédisant les besoins et réduisant au strict minimum"}
        ]
    },
    "sols_biodiversite": {
        "id": "sols_biodiversite",
        "dimension": "ESG",
        "question": "Comment votre activité interagit-elle avec la santé des sols et les écosystèmes vivants ?",
        "options": [
            {"index": 0, "valeur": "degradation_active",      "texte": "Utilisation d'intrants chimiques ou processus accélérant l'érosion"},
            {"index": 1, "valeur": "non_evalue",              "texte": "Aucun impact direct évident et aucune métrique d'impact collectée"},
            {"index": 2, "valeur": "preservation_passive",    "texte": "Pratiques limitant la casse (réduction des déchets, respect des lois)"},
            {"index": 3, "valeur": "impact_positif_certifie", "texte": "Amélioration mesurable de la qualité des terres ou baisse drastique des intrants"},
            {"index": 4, "valeur": "regeneratif_ecosysteme",  "texte": "Restauration active de la biodiversité locale ou des sols (agriculture verte)"}
        ]
    },
    "ressources_dechets": {
        "id": "ressources_dechets",
        "dimension": "ESG",
        "question": "Quel est le cycle de vie des matières premières et des déchets générés par votre chaîne de valeur ?",
        "options": [
            {"index": 0, "valeur": "economie_lineaire_lourde", "texte": "Modèle 'Extraire, Fabriquer, Jeter' avec production résiduelle massive"},
            {"index": 1, "valeur": "gestion_dechets_standard", "texte": "Tri basique et respect des réglementations municipales de gestion standard"},
            {"index": 2, "valeur": "reduction_a_la_source",    "texte": "Actions concrètes pour réduire la consommation de matières en amont"},
            {"index": 3, "valeur": "revalorisation_upcycling", "texte": "Transformation des déchets ou sous-produits en nouvelles matières marchandes"},
            {"index": 4, "valeur": "circularite_totale",       "texte": "Modèle Zéro-Déchet natif où 100% des extrants réintègrent un cycle vertueux"}
        ]
    }
}


def poser_scoring_f2():
    reponses = {}

    dim_courante = None
    for qid, q in QUESTIONS_F2.items():
        # Afficher un séparateur de dimension à chaque changement
        if q["dimension"] != dim_courante:
            dim_courante = q["dimension"]
        textes_options = [opt["texte"] for opt in q["options"]]
        reponse_texte  = poser_question(q["question"], textes_options)

        # Retrouver l'index et la valeur correspondant au texte choisi
        idx_choisi   = next(i for i, opt in enumerate(q["options"]) if opt["texte"] == reponse_texte)
        valeur_choisie = q["options"][idx_choisi]["valeur"]

        reponses[qid] = {"index": idx_choisi, "valeur": valeur_choisie}

    return reponses


def afficher_titre():
    print("═" * 60)
    print("       diagnostic de daturité dntrepreneuriale".upper())
    print("   Ce diagnostic évalue votre projet objectivement".upper())


def poser_question(question, options=None, type_reponse="choix"):
    print(f"\n{'─'*50}")
    print(f"  {question}")

    if type_reponse == "oui_non":
        options = ["Oui", "Non"]

    if options:
        for i, opt in enumerate(options, 1):
            print(f"    {i}. {opt}")
        while True:
            try:
                rep = input("  → Votre choix (numéro) : ").strip()
                idx = int(rep) - 1
                if 0 <= idx < len(options):
                    print(f"  ✓ {options[idx]}")
                    return options[idx]
                else:
                    print(f"  ⚠ Entrez un nombre entre 1 et {len(options)}")
            except ValueError:
                print("  ⚠ Entrez un nombre valide")

    elif type_reponse == "texte":
        rep = input("  → Votre réponse : ").strip()
        return rep if rep else "Non précisé"

    elif type_reponse == "nombre":
        while True:
            try:
                rep = input("  → Votre réponse (nombre) : ").strip()
                return float(rep)
            except ValueError:
                print("  ⚠ Entrez un nombre valide (ex: 50000)")


def alerte_divergence(message):
    print(f"\n  ⚠️  SIGNAL DÉTECTÉ : {message}")


class ScoreEngine:
    def __init__(self):
        self.score = 0
        self.gaps = []
        self.blockers = []
        self.signaux_divergence = []

    def ajouter_points(self, pts, raison=None):
        self.score += pts

    def ajouter_gap(self, gap):
        if gap not in self.gaps:
            self.gaps.append(gap)

    def ajouter_blocker(self, domaine, description, priorite):
        self.blockers.append({
            "domaine": domaine,
            "description": description,
            "priorite": priorite
        })

    def signal_divergence(self, message):
        self.signaux_divergence.append(message)
        alerte_divergence(message)

    def get_stade_reel(self):
        for num, stade in STADES.items():
            if stade["score_min"] <= self.score <= stade["score_max"]:
                return stade["nom"], num
        if self.score > 100:
            return STADES[6]["nom"], 6
        return STADES[1]["nom"], 1




def branche_agriculture_sylviculture_peche(engine, profil):
    print("\n Section spécifique : Agriculture / Sylviculture / Pêche")

    certif = poser_question(
        "Avez-vous des certifications sanitaires ou phytosanitaires (ISO 22000, HACCP, GlobalG.A.P., etc.) ?",
        type_reponse="oui_non"
    )
    if certif == "Oui":
        engine.ajouter_points(8, "Certifications sanitaires/phytosanitaires")
        profil["certifications_sanitaires"] = True
    else:
        engine.ajouter_gap("Certifications sanitaires/phytosanitaires manquantes")
        engine.ajouter_blocker("réglementaire", "Absence de certification sanitaire ou phytosanitaire", 2)
        profil["certifications_sanitaires"] = False

    chaine_froid = poser_question(
        "Avez-vous une chaîne de froid opérationnelle ou un accord avec un prestataire logistique ?",
        type_reponse="oui_non"
    )
    if chaine_froid == "Oui":
        engine.ajouter_points(6)
        profil["chaine_froid"] = True
    else:
        engine.ajouter_gap("Chaîne de froid / logistique non sécurisée")
        profil["chaine_froid"] = False

    saisonnalite = poser_question(
        "Votre activité est-elle saisonnière ?",
        ["Oui, fortement saisonnière", "Partiellement", "Non, activité régulière toute l'année"]
    )
    if "régulière" in saisonnalite:
        engine.ajouter_points(4)
    elif "Partiellement" in saisonnalite:
        engine.ajouter_points(2)
    else:
        engine.ajouter_gap("Dépendance saisonnière forte — modèle de revenus à stabiliser")
    profil["saisonnalite"] = saisonnalite

    acces_foncier = poser_question(
        "Disposez-vous d'un accès sécurisé au foncier (terres, concession maritime, forêt) ?",
        ["Oui, propriété ou bail long terme", "Oui, location court terme", "Non, accès incertain"]
    )
    if "propriété ou bail" in acces_foncier:
        engine.ajouter_points(5)
    elif "location court terme" in acces_foncier:
        engine.ajouter_points(2)
    else:
        engine.ajouter_gap("Accès foncier non sécurisé")
    profil["acces_foncier"] = acces_foncier


def branche_industrie_construction(engine, profil):
    print("\n Section spécifique : Industrie / Construction")

    equipements = poser_question(
        "Avez-vous les équipements de production / chantier nécessaires ?",
        ["Oui, opérationnels et amortis", "Oui, en cours d'acquisition", "Non, besoin de financement", "Non"]
    )
    if "opérationnels" in equipements:
        engine.ajouter_points(10)
        profil["equipements"] = "operationnels"
    elif "acquisition" in equipements:
        engine.ajouter_points(5)
        profil["equipements"] = "en_cours"
    else:
        engine.ajouter_gap("Équipements non disponibles")
        engine.ajouter_blocker("financier", "Besoin d'investissement équipements / matériel", 1)
        profil["equipements"] = "absent"

    iso = poser_question(
        "Êtes-vous certifié ISO ou en cours de certification ?",
        ["Certifié (ISO 9001, ISO 14001 ou autre)", "En cours de certification", "Non, pas encore"]
    )
    if "Certifié" in iso:
        engine.ajouter_points(8)
        profil["certification_iso"] = "certifie"
    elif "cours" in iso:
        engine.ajouter_points(3)
        profil["certification_iso"] = "en_cours"
    else:
        engine.ajouter_gap("Certification ISO non obtenue")
        profil["certification_iso"] = "absent"

    foprodi = poser_question(
        "Avez-vous déposé un dossier FOPRODI ou sollicité un appui APII/UTICA ?",
        type_reponse="oui_non"
    )
    if foprodi == "Oui":
        engine.ajouter_points(5)
        profil["foprodi_apii"] = True
    else:
        profil["foprodi_apii"] = False

    sous_traitance = poser_question(
        "Travaillez-vous avec des donneurs d'ordre ou en sous-traitance ?",
        ["Oui, contrats formels signés", "Oui, informellement", "Non, clientèle directe uniquement"]
    )
    if "formels" in sous_traitance:
        engine.ajouter_points(6)
    elif "informellement" in sous_traitance:
        engine.ajouter_points(2)
    profil["sous_traitance"] = sous_traitance


def branche_commerce_transport_logistique(engine, profil):
    print("\n Section spécifique : Commerce / Transport / Logistique")

    reseau_distribution = poser_question(
        "Avez-vous un réseau de distribution ou des points de vente établis ?",
        ["Oui, réseau structuré multi-canaux", "Oui, un ou deux points de vente", "Non, encore en construction"]
    )
    if "multi-canaux" in reseau_distribution:
        engine.ajouter_points(10)
    elif "un ou deux" in reseau_distribution:
        engine.ajouter_points(5)
    else:
        engine.ajouter_gap("Réseau de distribution non établi")
    profil["reseau_distribution"] = reseau_distribution

    parc_vehicules = poser_question(
        "Pour le transport / la logistique : disposez-vous d'un parc de véhicules ou d'un accord avec un transporteur ?",
        ["Oui, parc propre opérationnel", "Oui, accord avec prestataire", "Non"]
    )
    if "propre" in parc_vehicules:
        engine.ajouter_points(8)
    elif "accord" in parc_vehicules:
        engine.ajouter_points(4)
    else:
        engine.ajouter_gap("Capacité logistique / transport non assurée")
    profil["capacite_logistique"] = parc_vehicules

    digital = poser_question(
        "Avez-vous une présence digitale ou une plateforme e-commerce ?",
        ["Oui, e-commerce actif avec commandes", "Oui, présence digitale (réseaux sociaux/site)", "Non"]
    )
    if "e-commerce actif" in digital:
        engine.ajouter_points(6)
    elif "présence" in digital:
        engine.ajouter_points(2)
    else:
        engine.ajouter_gap("Absence de présence digitale")
    profil["presence_digitale"] = digital

    stock = poser_question(
        "Gérez-vous un stock ou des approvisionnements de manière structurée ?",
        ["Oui, avec un système de gestion de stock", "Oui, manuellement", "Non"]
    )
    if "système" in stock:
        engine.ajouter_points(4)
    elif "manuellement" in stock:
        engine.ajouter_points(2)
    profil["gestion_stock"] = stock


def branche_service_tourisme(engine, profil):
    print("\n Section spécifique : Service / Tourisme")

    classement = poser_question(
        "Votre établissement est-il classé ou agréé (hôtel classé, agence de voyage agréée, etc.) ?",
        ["Oui, classé / agréé officiellement", "En cours de classement / agrément", "Non / Non applicable"]
    )
    if "officiellement" in classement:
        engine.ajouter_points(8)
        profil["classement_agree"] = "obtenu"
    elif "cours" in classement:
        engine.ajouter_points(3)
        profil["classement_agree"] = "en_cours"
    else:
        profil["classement_agree"] = "absent"

    fidelisation = poser_question(
        "Avez-vous une base de clients fidèles ou un programme de fidélisation ?",
        ["Oui, base de données clients active et programme structuré",
         "Oui, clientèle régulière sans programme formel",
         "Non, clientèle de passage"]
    )
    if "programme structuré" in fidelisation:
        engine.ajouter_points(8)
    elif "régulière" in fidelisation:
        engine.ajouter_points(4)
    else:
        engine.ajouter_gap("Absence de stratégie de fidélisation client")
    profil["fidelisation"] = fidelisation

    numerisation = poser_question(
        "Utilisez-vous des outils numériques pour la gestion (réservations en ligne, CRM, etc.) ?",
        ["Oui, plateforme de réservation / CRM opérationnel", "Partiellement", "Non"]
    )
    if "opérationnel" in numerisation:
        engine.ajouter_points(6)
    elif "Partiellement" in numerisation:
        engine.ajouter_points(2)
    profil["numerisation_service"] = numerisation

    saisonnalite = poser_question(
        "Votre activité est-elle fortement saisonnière (ex : tourisme estival) ?",
        ["Oui, fortement saisonnière", "Partiellement", "Non, activité régulière toute l'année"]
    )
    if "régulière" in saisonnalite:
        engine.ajouter_points(4)
    elif "Partiellement" in saisonnalite:
        engine.ajouter_points(2)
    else:
        engine.ajouter_gap("Forte saisonnalité — revenus concentrés sur quelques mois")
    profil["saisonnalite"] = saisonnalite


def branche_tech_services_entreprise(engine, profil):
    print("\n Section spécifique : Technologie et Services Entreprise")

    mvp = poser_question(
        "Avez-vous un MVP (produit minimum viable) ou une offre de service formalisée ?",
        ["Oui, en production / déployé chez des clients",
         "Oui, en test avec utilisateurs / clients pilotes réels",
         "En développement / conception",
         "Non"]
    )
    if "production" in mvp:
        engine.ajouter_points(12)
        profil["mvp_statut"] = "production"
    elif "test" in mvp:
        engine.ajouter_points(8)
        profil["mvp_statut"] = "test"
    elif "développement" in mvp or "conception" in mvp:
        engine.ajouter_points(3)
        profil["mvp_statut"] = "dev"
        engine.ajouter_gap("MVP / offre non encore livrée")
    else:
        engine.ajouter_gap("Aucun MVP — stade idéation confirmé")
        engine.ajouter_blocker("technique", "Pas de produit ou service développé", 1)
        profil["mvp_statut"] = "absent"

    mrr = poser_question(
        "Avez-vous un MRR (revenu mensuel récurrent) ou des contrats de service récurrents ?",
        ["Oui, > 5 000 TND/mois", "Oui, < 5 000 TND/mois", "Non, mais des utilisateurs / clients actifs", "Non"]
    )
    if "Oui, > 5 000" in mrr:
        engine.ajouter_points(15)
        profil["mrr"] = "fort"
    elif "Oui, < 5 000" in mrr:
        engine.ajouter_points(8)
        profil["mrr"] = "faible"
    elif "actifs" in mrr:
        engine.ajouter_points(4)
        profil["mrr"] = "zero_avec_users"
    else:
        engine.ajouter_gap("Aucun revenu récurrent ou contrat de service")
        profil["mrr"] = "zero"

    ip = poser_question(
        "Avez-vous protégé votre propriété intellectuelle (brevet, marque déposée, droits logiciels) ?",
        type_reponse="oui_non"
    )
    if ip == "Oui":
        engine.ajouter_points(5)
        profil["propriete_intellectuelle"] = True
    else:
        profil["propriete_intellectuelle"] = False

    scalabilite = poser_question(
        "Votre modèle est-il scalable sans augmentation proportionnelle des coûts ?",
        ["Oui, fortement scalable (SaaS, plateforme)", "Partiellement scalable", "Non, croissance = coûts linéaires"]
    )
    if "fortement" in scalabilite:
        engine.ajouter_points(6)
    elif "Partiellement" in scalabilite:
        engine.ajouter_points(3)
    else:
        engine.ajouter_gap("Modèle peu scalable — croissance coûteuse")
    profil["scalabilite"] = scalabilite


def detecter_secteur(desc_lower):
    scores = {}
    for cle, info in SECTEURS.items():
        score = sum(1 for mot in info["mots_cles"] if mot in desc_lower)
        if score > 0:
            scores[cle] = score

    if scores:
        return max(scores, key=scores.get)
    return None


def run_diagnostic():
    afficher_titre()
    engine = ScoreEngine()
    profil = {}

    


    print("\n ÉTAPE 1 — Présentation de votre projet")
    nom_entreprise = poser_question(
        "Nom de votre entreprise / projet :",
        type_reponse="texte"
    )
    profil["nom_entreprise"] = nom_entreprise

    print("─" * 50)
    print("  Décrivez votre projet en quelques lignes en précisant :")
    print("    • Le secteur d'activité :")
    print("      — Agriculture/Sylviculture/Pêche")
    print("      — Industrie/Construction")
    print("      — Commerce/Transport/Logistique")
    print("      — Service/Tourisme")
    print("      — Technologie et Services Entreprise")
    print("    • La région où vous êtes basé  (ex: Tunis, Sfax, Sousse...)")
    #print("    • Le nom de votre entreprise ou projet")
    print("    • Selon vous, à quel stade en êtes-vous aujourd'hui ?")
    print("      (Ideation / Market Validation / Structuration /")
    print("       Fundraising / Launch Planning / Growth)")

    
    
    
    description_libre = poser_question(
        "Votre description (appuyez sur Entrée quand vous avez terminé) :",
        type_reponse="texte"
    )
    profil["description_libre"] = description_libre

    entrepreneur_id = f"ENT-{str(uuid.uuid4())[:6].upper()}"
    profil["entrepreneur_id"] = entrepreneur_id

    # ── Extraction guidée depuis la description libre ──
    print("\n  Merci ! Quelques précisions rapides pour compléter votre profil :\n")



    # ── Détection automatique du secteur ──
    desc_lower = description_libre.lower()
    secteur_cle_detecte = detecter_secteur(desc_lower)
    secteur_cle = None

    SECTEURS_LABELS = [info["label"] for info in SECTEURS.values()]
    SECTEURS_CLES   = list(SECTEURS.keys())

    if secteur_cle_detecte:
        label_detecte = SECTEURS[secteur_cle_detecte]["label"]
        print(f"\n  ─────────────────────────────────────────────────")
        print(f"  Secteur détecté depuis votre description : {label_detecte}")
        confirmation = poser_question(
            "Est-ce correct ?",
            type_reponse="oui_non"
        )
        if confirmation == "Oui":
            secteur_cle = secteur_cle_detecte

    if not secteur_cle:
        choix_label = poser_question(
            "Confirmez votre secteur d'activité :",
            SECTEURS_LABELS
        )
        secteur_cle = SECTEURS_CLES[SECTEURS_LABELS.index(choix_label)]

    profil["secteur"] = secteur_cle
    profil["secteur_label"] = SECTEURS[secteur_cle]["label"]

    # ── Extraction de la localisation ──
    REGIONS = ["Bizerte", "Tunis", "Ariana", "Ben Arous", "Manouba", "Nabeul", "Sfax", "Zaghouan", "Beja", "Jendouba", "Siliana", "Kasserine", "Kef", "Kaireon", "Sousse", "Monastir", "Mahdia", "Sidi Bouzid", "Tozeur", "Kebili", "Gabes", "Gafsa", "Medenine", "Tataouine"]
    localisation_detectee = None
    for region in REGIONS:
        if region.lower() in desc_lower:
            localisation_detectee = region
            break

    if localisation_detectee:
        print(f"\n  ─────────────────────────────────────────────────")
        print(f"  Région détectée depuis votre description : {localisation_detectee}")
        confirmation_loc = poser_question(
            "Est-ce correct ?",
            type_reponse="oui_non"
        )
        if confirmation_loc == "Non":
            localisation_detectee = None

    if not localisation_detectee:
        localisation_detectee = poser_question(
            "Confirmez votre région :",
            REGIONS
        )

    localisation = localisation_detectee
    profil["localisation"] = localisation

    # ── Extraction du stade perçu ──
    STADES_NOMS = [s["nom"] for s in STADES.values()]
    stade_percu_detecte = None
    for nom in STADES_NOMS:
        if nom.lower() in desc_lower:
            stade_percu_detecte = nom
            break

    if stade_percu_detecte:
        print(f"\n  ─────────────────────────────────────────────────")
        print(f"  Stade perçu détecté depuis votre description : {stade_percu_detecte}")
        confirmation_stade = poser_question(
            "Est-ce correct ?",
            type_reponse="oui_non"
        )
        if confirmation_stade == "Non":
            stade_percu_detecte = None

    if not stade_percu_detecte:
        stade_percu_detecte = poser_question(
            "Selon vous, à quel stade est votre projet aujourd'hui ?",
            STADES_NOMS
        )

    stade_percu = stade_percu_detecte
    profil["stade_percu"] = stade_percu

    # ── Question équipe ──
    equipe = poser_question(
        "Votre équipe fondatrice est-elle complète ?",
        ["Oui, équipe complète avec rôles définis",
         "Partiellement (certains rôles clés manquants)",
         "Non, je suis seul pour l'instant"]
    )
    if "complète" in equipe:
        engine.ajouter_points(8)
        profil["equipe"] = "complete"
    elif "Partiellement" in equipe:
        engine.ajouter_points(3)
        engine.ajouter_gap("Équipe incomplète — rôles clés manquants")
        profil["equipe"] = "partielle"
    else:
        engine.ajouter_gap("Fondateur seul — équipe à constituer")
        engine.ajouter_blocker("organisationnel", "Absence d'équipe fondatrice", 2)
        profil["equipe"] = "solo"

    print("\n ÉTAPE 2 — Questions sectorielles")

    if secteur_cle == "agriculture_sylviculture_peche":
        branche_agriculture_sylviculture_peche(engine, profil)
    elif secteur_cle == "industrie_construction":
        branche_industrie_construction(engine, profil)
    elif secteur_cle == "commerce_transport_logistique":
        branche_commerce_transport_logistique(engine, profil)
    elif secteur_cle == "service_tourisme":
        branche_service_tourisme(engine, profil)
    elif secteur_cle == "tech_services_entreprise":
        branche_tech_services_entreprise(engine, profil)

    print("\n ÉTAPE 3 — Structure juridique")

    rne = poser_question(
        "Avez-vous un RNE (Registre National des Entreprises) ?",
        type_reponse="oui_non"
    )
    if rne == "Oui":
        engine.ajouter_points(10)
        profil["rne"] = True

        forme_juridique = poser_question(
            "Quelle est votre forme juridique ?",
            ["SARL", "SA", "Entreprise individuelle", "Association / ONG", "Startup Act labellisée"]
        )
        profil["forme_juridique"] = forme_juridique
        if forme_juridique == "Startup Act labellisée":
            engine.ajouter_points(8)
    else:
        engine.ajouter_gap("Pas de RNE enregistré")
        engine.ajouter_blocker("légal", "Entreprise non enregistrée", 1)
        profil["rne"] = False
        profil["forme_juridique"] = None

        stades_avances = ["Fundraising", "Launch Planning", "Growth"]
        if stade_percu in stades_avances:
            engine.signal_divergence(
                f"Vous vous croyez en '{stade_percu}' mais n'avez pas de RNE — "
                "impossible de constituer un dossier bancable sans entité juridique."
            )


    print("\n ÉTAPE 4 — Revenus et validation marché")

    a_revenus = poser_question(
        "Avez-vous des revenus générés par votre activité ?",
        type_reponse="oui_non"
    )

    if a_revenus == "Oui":
        ca = poser_question(
            "Quel est votre chiffre d'affaires annuel approximatif (en TND) ?",
            type_reponse="nombre"
        )
        profil["chiffre_affaires"] = ca

        anciennete = poser_question(
            "Depuis combien de temps générez-vous ces revenus ?",
            ["Moins de 6 mois", "6 à 12 mois", "1 à 3 ans", "Plus de 3 ans"]
        )
        profil["anciennete_revenus"] = anciennete

        if ca >= 500000:
            engine.ajouter_points(20)
        elif ca >= 100000:
            engine.ajouter_points(15)
        elif ca >= 20000:
            engine.ajouter_points(10)
        else:
            engine.ajouter_points(5)

        if "Plus de 3 ans" in anciennete:
            engine.ajouter_points(8)
        elif "1 à 3 ans" in anciennete:
            engine.ajouter_points(5)
        elif "6 à 12 mois" in anciennete:
            engine.ajouter_points(3)

    else:
        profil["chiffre_affaires"] = 0
        a_clients_payants = poser_question(
            "Avez-vous des clients payants (même sans CA récurrent) ?",
            type_reponse="oui_non"
        )

        if a_clients_payants == "Oui":
            engine.ajouter_points(8)
            lettres = poser_question(
                "Avez-vous des lettres d'intention ou contrats signés ?",
                type_reponse="oui_non"
            )
            if lettres == "Oui":
                engine.ajouter_points(5)
                profil["lettres_intention"] = True
            else:
                engine.ajouter_gap("Pas de contrats / lettres d'intention formalisés")
                profil["lettres_intention"] = False
        else:
            validation = poser_question(
                "Qui a validé votre idée jusqu'à présent ?",
                ["Des experts du secteur (mentors, professionnels)",
                 "Des proches / famille / amis",
                 "Personne encore",
                 "Des clients potentiels lors d'entretiens formels"]
            )

            if "clients potentiels" in validation:
                engine.ajouter_points(5)
                profil["validation_type"] = "clients_potentiels"
            elif "experts" in validation:
                engine.ajouter_points(3)
                profil["validation_type"] = "experts"
            elif "proches" in validation:
                engine.ajouter_gap("Validation uniquement par des proches — pas une preuve marché")
                engine.signal_divergence(
                    "Des amis ou de la famille intéressés par votre idée ≠ traction marché réelle. "
                    "Aucun client payant détecté."
                )
                profil["validation_type"] = "proches"
            else:
                engine.ajouter_gap("Aucune validation externe effectuée")
                engine.ajouter_blocker("marché", "Idée non validée par le marché", 1)
                profil["validation_type"] = "aucune"

    
    print("\n ÉTAPE 5 — Business Plan et dossier")

    bp = poser_question(
        "Avez-vous un business plan documenté ?",
        ["Oui, complet avec projections financières sur 3 ans",
         "Oui, mais incomplet ou sans projections",
         "En cours de rédaction",
         "Non"]
    )

    if "complet" in bp:
        engine.ajouter_points(10)
        profil["business_plan"] = "complet"
    elif "incomplet" in bp:
        engine.ajouter_points(4)
        engine.ajouter_gap("Business plan incomplet ou sans projections financières")
        profil["business_plan"] = "incomplet"
    elif "cours" in bp:
        engine.ajouter_points(2)
        profil["business_plan"] = "en_cours"
    else:
        engine.ajouter_gap("Pas de business plan documenté")
        engine.ajouter_blocker("financier", "Absence de business plan", 2)
        profil["business_plan"] = "absent"

        if stade_percu in ["Fundraising", "Launch Planning"]:
            engine.signal_divergence(
                f"Vous vous positionnez en '{stade_percu}' mais n'avez pas de business plan. "
                "Aucune institution financière tunisienne n'étudiera un dossier sans BP."
            )

    # ── BLOC 6 : Innovation ──
    print("\n ÉTAPE 6 — Innovation et différenciation")

    innovation = poser_question(
        "Votre solution existe-t-elle déjà sur le marché tunisien ?",
        ["Non, c'est totalement nouveau en Tunisie",
         "Des solutions similaires existent mais la mienne est différenciée",
         "Des solutions identiques existent depuis moins de 2 ans",
         "Des solutions identiques existent depuis plus de 2 ans"]
    )

    if "totalement nouveau" in innovation:
        engine.ajouter_points(8)
        profil["innovation_niveau"] = "haute"
    elif "différenciée" in innovation:
        engine.ajouter_points(5)
        profil["innovation_niveau"] = "moyenne"
    elif "moins de 2 ans" in innovation:
        engine.ajouter_points(2)
        profil["innovation_niveau"] = "faible"
        engine.ajouter_gap("Marché déjà occupé par des concurrents récents")
    else:
        profil["innovation_niveau"] = "tres_faible"
        engine.ajouter_gap("Produit / service existant sur le marché tunisien depuis plus de 2 ans")
        engine.signal_divergence(
            "Votre solution existe déjà sur le marché tunisien depuis plusieurs années. "
            "L'innovation perçue ne se traduit pas en différenciation réelle."
        )

    # ── BLOC 7 : Accompagnement et financement ──
    print("\n ÉTAPE 7 — Accompagnement et financement")

    accompagnement = poser_question(
        "Avez-vous bénéficié d'un programme d'accompagnement ?",
        ["Oui, actuellement en incubateur/accélérateur",
         "Oui, programme terminé",
         "Non, jamais"]
    )
    if "actuellement" in accompagnement:
        engine.ajouter_points(6)
        profil["accompagnement"] = "en_cours"
    elif "terminé" in accompagnement:
        engine.ajouter_points(3)
        profil["accompagnement"] = "termine"
    else:
        profil["accompagnement"] = "jamais"

    financement_obtenu = poser_question(
        "Avez-vous déjà obtenu un financement externe ?",
        ["Oui, capital-risque ou business angel",
         "Oui, financement public (APII, BFPME, BTS...)",
         "Oui, love money uniquement",
         "Non, aucun financement externe"]
    )
    if "capital-risque" in financement_obtenu:
        engine.ajouter_points(12)
        profil["financement"] = "capital_risque"
    elif "public" in financement_obtenu:
        engine.ajouter_points(8)
        profil["financement"] = "public"
    elif "love money" in financement_obtenu:
        engine.ajouter_points(3)
        profil["financement"] = "love_money"
    else:
        profil["financement"] = "aucun"

    # ── BLOC 8 : Scoring Multi-Dimensionnel F2 ──
    print("\n ÉTAPE 8 — Évaluation Multi-Dimensionnelle")
    print("─" * 50)
    print("  Ces questions évaluent votre projet sur 5 dimensions :")
    print("  Marché, Offre Commerciale, Innovation, Scalabilité, Impact.")
    reponses_f2 = poser_scoring_f2()

    # ─────────────────────────────────────────────
    # CALCUL FINAL
    # ─────────────────────────────────────────────

    stade_reel_nom, stade_reel_num = engine.get_stade_reel()

    stade_percu_num = next(
        (num for num, s in STADES.items() if s["nom"] == stade_percu), 1
    )

    gap_detecte = stade_reel_nom != stade_percu
    gap_explication = None

    if gap_detecte:
        direction = "surestimé" if stade_reel_num < stade_percu_num else "sous-estimé"
        ecart = abs(stade_reel_num - stade_percu_num)
        gap_explication = (
            f"L'entrepreneur a {direction} son stade de {ecart} niveau(x). "
            f"Il se perçoit en '{stade_percu}' mais le diagnostic objectif indique '{stade_reel_nom}'. "
            f"Causes principales : {', '.join(engine.gaps[:3]) if engine.gaps else 'voir détails'}."
        )

    # ─────────────────────────────────────────────
    # AFFICHAGE DU RÉSULTAT
    # ─────────────────────────────────────────────

    print("\n")
    print("   RÉSULTATS DU DIAGNOSTIC")
    print("\n")
    print(f"  Projet        : {profil.get('nom_entreprise', 'N/A')} ({entrepreneur_id})")
    print(f"  Secteur       : {profil['secteur_label']}")
    print(f"  Localisation  : {localisation}")
    print(f"\n  Stade perçu   : {stade_percu}")
    print(f"  Stade réel    : {stade_reel_nom}  (score: {engine.score}/100)")

    if gap_detecte:
        print(f"\n GAP DÉTECTÉ !")
        print(f"  {gap_explication}")
    else:
        print(f"\n Votre auto-évaluation correspond au diagnostic.")

    if engine.gaps:
        print(f"\n Lacunes identifiées :")
        for g in engine.gaps:
            print(f"     • {g}")

    if engine.blockers:
        print(f"\n Blockers prioritaires :")
        sorted_blockers = sorted(engine.blockers, key=lambda x: x["priorite"])
        for b in sorted_blockers:
            print(f"     [{b['priorite']}] {b['domaine'].upper()} — {b['description']}")

    stade_info = STADES[stade_reel_num]
    print(f"\n Financement adapté à votre stade réel : {stade_info['financement']}")
    print("\n")


    output = {
        "entrepreneur_id": entrepreneur_id,
        "secteur": profil.get("secteur", "Non précisé"),
        "stade_reel": stade_reel_nom,
        "stade_percu": stade_percu,
        "score_diagnostic": engine.score,
        "gap_detecte": gap_detecte,
        "gap_explication": gap_explication,
        "gaps": engine.gaps,
        "blockers": engine.blockers,
        "localisation": profil.get("localisation", "Non précisé"),
        "profil_complet": profil,
        "signaux_divergence": engine.signaux_divergence,
        "financement_recommande": stade_info["financement"],
        "reponses": reponses_f2,
    }

    filename = f"diagnostic_{entrepreneur_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n Fichier JSON exporté : {filename}")
    print("═" * 60 + "\n")

    return output
if __name__ == "__main__":
    result = run_diagnostic()
