import json
from datetime import datetime

STADES = {
    1: {"nom": "Ideation", "description": "Idée sans validation ni équipe complète", "financement": "Love money / Concours", "score_min": 0, "score_max": 15},
    2: {"nom": "Market Validation", "description": "Premiers clients / traction naissante", "financement": "Microfinance / BTS", "score_min": 16, "score_max": 30},
    3: {"nom": "Structuration", "description": "Structure juridique / business plan", "financement": "APII / ANPE", "score_min": 31, "score_max": 50},
    4: {"nom": "Fundraising", "description": "Dossier bancable en construction", "financement": "BFPME / Startup Act", "score_min": 51, "score_max": 65},
    5: {"nom": "Launch Planning", "description": "Produit validé / prêt à lever", "financement": "Capital risque / ANAVA", "score_min": 66, "score_max": 80},
    6: {"nom": "Growth", "description": "Revenus existants / expansion", "financement": "Lignes bancaires / AFD / EU", "score_min": 81, "score_max": 100},
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
            {"index": 0, "valeur": "B2C", "texte": "Grand public / Utilisateurs individuels"},
            {"index": 1, "valeur": "B2B_SME", "texte": "Petites et Moyennes Entreprises / Professionnels indépendants"},
            {"index": 2, "valeur": "B2B_Enterprise", "texte": "Grands Comptes / Groupes Industriels / Corporates"},
            {"index": 3, "valeur": "B2B2C", "texte": "Modèle intermédiaire (via un partenaire pour toucher le client final)"},
            {"index": 4, "valeur": "B2G", "texte": "Gouvernements / Ministères / Collectivités Publiques"}
        ]
    },
    "potentiel_financier_marche": {
        "id": "potentiel_financier_marche",
        "dimension": "MKT",
        "question": "Quelle est la valeur financière annuelle estimée de votre marché immédiatement accessible (SOM) ?",
        "options": [
            {"index": 0, "valeur": "niche_ultra_locale", "texte": "Marché de niche très restreint (Moins de 1M DT / an)"},
            {"index": 1, "valeur": "marche_local_limite", "texte": "Marché local avec un plafond rapide (1M à 5M DT / an)"},
            {"index": 2, "valeur": "marche_national_intermediaire", "texte": "Marché national significatif (5M à 20M DT / an)"},
            {"index": 3, "valeur": "marche_regional_scalable", "texte": "Marché à fort potentiel d'extension régionale (20M à 50M DT / an)"},
            {"index": 4, "valeur": "marche_global_massif", "texte": "Marché de masse international (Plus de 50M DT / an)"}
        ]
    },
    "intensite_concurrence": {
        "id": "intensite_concurrence",
        "dimension": "MKT",
        "question": "Comment se structure l'intensité concurrentielle sur votre segment cible ?",
        "options": [
            {"index": 0, "valeur": "hyper_competition", "texte": "Marché saturé, guerre des prix féroce avec des géants installés"},
            {"index": 1, "valeur": "forte_concurrence", "texte": "Plusieurs acteurs directs bien financés et identifiés"},
            {"index": 2, "valeur": "marche_partage", "texte": "Concurrence modérée, fragmentation permettant de prendre des parts"},
            {"index": 3, "valeur": "faible_concurrence", "texte": "Marché émergent, solutions alternatives indirectes ou obsolètes"},
            {"index": 4, "valeur": "ocean_bleu", "texte": "Pionnier absolu, aucun concurrent direct sur cette proposition de valeur"}
        ]
    },
    "niveau_traction": {
        "id": "niveau_traction",
        "dimension": "MKT",
        "question": "Quel est l'état réel et mesurable de votre validation commerciale sur le terrain ?",
        "options": [
            {"index": 0, "valeur": "ideation_pure", "texte": "Zéro utilisateur, validation théorique uniquement"},
            {"index": 1, "valeur": "premiers_testeurs", "texte": "Bêta-testeurs actifs ou utilisateurs pilotes non-payants"},
            {"index": 2, "valeur": "traction_initiale", "texte": "Premières transactions ou contrats signés (Preuve de Concept payante)"},
            {"index": 3, "valeur": "traction_significative", "texte": "Portefeuille clients en croissance régulière et acquisition active"},
            {"index": 4, "valeur": "croissance_organique", "texte": "Revenus récurrents stables (MRR/ARR) avec fort taux de rétention"}
        ]
    },
    "modele_revenu": {
        "id": "modele_revenu",
        "dimension": "MKT",
        "question": "Où en est la validation empirique de votre mécanisme de capture de valeur ?",
        "options": [
            {"index": 0, "valeur": "non_defini", "texte": "Modèle de revenus flou, gratuité totale sans stratégie de conversion"},
            {"index": 1, "valeur": "transactionnel_standard", "texte": "Vente unique (one-shot), revenus dépendants de chaque acte de vente"},
            {"index": 2, "valeur": "commission_marketplace", "texte": "Modèle basé sur des frais de transaction ou de mise en relation"},
            {"index": 3, "valeur": "abonnement_saas", "texte": "Revenus récurrents prévisibles (SaaS, abonnements périodiques)"},
            {"index": 4, "valeur": "multi_stream_optimise", "texte": "Modèle hybride validé (Abonnement + Commissions + Options premium)"}
        ]
    },
    "business_plan_f2": {
        "id": "business_plan_f2",
        "dimension": "COM",
        "question": "Quel est le niveau de maturité de votre modélisation financière et stratégique ?",
        "options": [
            {"index": 0, "valeur": "non_commence", "texte": "Aucune projection financière ni business plan formalisé"},
            {"index": 1, "valeur": "ebauche_initiale", "texte": "Structure de coûts basique estimée sans métriques clés (LTV, CAC)"},
            {"index": 2, "valeur": "en_cours_de_validation", "texte": "Business Model Canvas complet avec prévisions financières à 3 ans"},
            {"index": 3, "valeur": "valide_equipe", "texte": "Modèle financier complet validé par des mentors ou experts internes"},
            {"index": 4, "valeur": "valide_audite_externe", "texte": "Plan d'affaires validé et audité par des investisseurs ou cabinets tiers"}
        ]
    },
    "maturite_produit": {
        "id": "maturite_produit",
        "dimension": "COM",
        "question": "Où se situe votre solution sur l'échelle de développement technique ?",
        "options": [
            {"index": 0, "valeur": "concept_wireframe", "texte": "Maquettes graphiques, storyboards ou slides de présentation uniquement"},
            {"index": 1, "valeur": "prototype_poc", "texte": "Prototype de laboratoire fonctionnel mais instable (Preuve de Concept)"},
            {"index": 2, "valeur": "mvp_valide", "texte": "Produit Minimum Viable déployé et testé en conditions réelles"},
            {"index": 3, "valeur": "industrialise_stable", "texte": "Produit fini, stable, sécurisé et prêt pour un déploiement massif"},
            {"index": 4, "valeur": "scalable_architecture", "texte": "Produit hautement disponible, API-fié et prêt pour l'international"}
        ]
    },
    "strategie_prix": {
        "id": "strategie_prix",
        "dimension": "COM",
        "question": "Comment votre structure tarifaire (pricing) est-elle perçue par le marché ?",
        "options": [
            {"index": 0, "valeur": "arbitraire", "texte": "Prix fixé au hasard ou à l'intuition sans étude terrain"},
            {"index": 1, "valeur": "cost_plus_margin", "texte": "Tarification basique calculée uniquement sur les coûts + une marge fixe"},
            {"index": 2, "valeur": "alignement_concurrence", "texte": "Prix calqué horizontalement sur les solutions existantes"},
            {"index": 3, "valeur": "valeur_percue", "texte": "Prix indexé sur le ROI (Retour sur Investissement) généré pour le client"},
            {"index": 4, "valeur": "dynamique_usage", "texte": "Pricing hautement optimisé à l'usage, testé et validé par des cohortes"}
        ]
    },
    "alignement_besoins": {
        "id": "alignement_besoins",
        "dimension": "COM",
        "question": "À quel point votre produit résout-il un problème critique (Pain Point) pour votre cible ?",
        "options": [
            {"index": 0, "valeur": "aucun_interet", "texte": "Le problème ciblé n'intéresse pas le marché ou n'existe pas"},
            {"index": 1, "valeur": "nice_to_have", "texte": "Outil de confort secondaire, déclenche peu d'intentions d'achat"},
            {"index": 2, "valeur": "important_non_urgent", "texte": "Problème réel mais le client remet souvent l'achat à plus tard"},
            {"index": 3, "valeur": "must_have_urgent", "texte": "Besoin critique, les clients recherchent activement une solution"},
            {"index": 4, "valeur": "total_pmf", "texte": "Dépendance forte au produit, rétention exceptionnelle (Product-Market Fit validé)"}
        ]
    },
    "nouveaute_locale": {
        "id": "nouveaute_locale",
        "dimension": "INO",
        "question": "Quelle est l'originalité de votre positionnement sur votre zone géographique cible ?",
        "options": [
            {"index": 0, "valeur": "copie_conforme", "texte": "Réplication exacte d'un service déjà omniprésent localement"},
            {"index": 1, "valeur": "amelioration_mineure", "texte": "Même concept que les concurrents avec une simple option en plus"},
            {"index": 2, "valeur": "adaptation_locale", "texte": "Importation et adaptation d'un concept étranger inexistant ici"},
            {"index": 3, "valeur": "premiere_nationale", "texte": "Concept totalement inédit et pionnier à l'échelle du pays"},
            {"index": 4, "valeur": "disruption_globale", "texte": "Innovation de rupture sans équivalent à l'échelle internationale"}
        ]
    },
    "intensite_tech": {
        "id": "intensite_tech",
        "dimension": "INO",
        "question": "Quelle est l'épaisseur technologique sous-jacente à votre solution ?",
        "options": [
            {"index": 0, "valeur": "no_code_standard", "texte": "Assemblage d'outils tiers existants sans aucun code propriétaire"},
            {"index": 1, "valeur": "developpement_classique", "texte": "Application Web ou Mobile standard sans complexité technique"},
            {"index": 2, "valeur": "integration_avancee", "texte": "Système connecté avec des architectures Cloud et intégration poussée d'API"},
            {"index": 3, "valeur": "ia_proprietaire", "texte": "Algorithmes d'Intelligence Artificielle ou traitement de données propriétaires"},
            {"index": 4, "valeur": "deeptech_science", "texte": "DeepTech issue de laboratoires de recherche, biotechnologies ou hardware complexe"}
        ]
    },
    "barrieres_entree": {
        "id": "barrieres_entree",
        "dimension": "INO",
        "question": "De quel avantage défensif disposez-vous pour empêcher une copie rapide par un concurrent ?",
        "options": [
            {"index": 0, "valeur": "aucune_barriere", "texte": "N'importe quel développeur peut copier le concept en deux semaines"},
            {"index": 1, "valeur": "avance_operationnelle", "texte": "Simple avantage de rapidité d'exécution ou de communication"},
            {"index": 2, "valeur": "moat_commercial", "texte": "Exclusivités commerciales, partenariats clés ou base de données qualifiée"},
            {"index": 3, "valeur": "effet_de_reseau", "texte": "Barrière forte grâce aux effets de réseau (plus d'utilisateurs = incopiable)"},
            {"index": 4, "valeur": "propriete_intellectuelle", "texte": "Brevet déposé, secret industriel strict ou technologie hautement complexe"}
        ]
    },
    "degre_rupture": {
        "id": "degre_rupture",
        "dimension": "INO",
        "question": "Comment votre innovation modifie-t-elle les habitudes des acteurs du secteur ?",
        "options": [
            {"index": 0, "valeur": "evolution_nulle", "texte": "L'utilisateur ne change absolument rien à ses processus actuels"},
            {"index": 1, "valeur": "optimisation_incrementale", "texte": "Simple gain de temps ou économie marginale sur un processus existant"},
            {"index": 2, "valeur": "transformation_process", "texte": "Modification visible des habitudes de travail ou de consommation"},
            {"index": 3, "valeur": "forte_substitution", "texte": "Rend obsolètes les anciennes méthodes pour une grande partie des utilisateurs"},
            {"index": 4, "valeur": "changement_paradigme", "texte": "Crée un nouvel usage ou une nouvelle industrie à part entière"}
        ]
    },
    "replicabilite": {
        "id": "replicabilite",
        "dimension": "SCA",
        "question": "Quel est le niveau de complexité pour déployer votre solution sur un nouveau territoire ?",
        "options": [
            {"index": 0, "valeur": "dependance_physique_stricte", "texte": "Nécessite des infrastructures lourdes, des locaux et des équipes physiques"},
            {"index": 1, "valeur": "contraintes_reglementaires", "texte": "Soumis à des autorisations légales longues et complexes par pays"},
            {"index": 2, "valeur": "deploiement_operationnel_modere", "texte": "Nécessite l'ouverture d'un bureau réduit et du support local"},
            {"index": 3, "valeur": "facilement_replicable", "texte": "Processus hautement standardisés, déploiement rapide sans gros ajustements"},
            {"index": 4, "valeur": "immediate_pure_player", "texte": "Modèle 100% digital, expansion internationale instantanée sans barrière"}
        ]
    },
    "independance_manuelle": {
        "id": "independance_manuelle",
        "dimension": "SCA",
        "question": "Comment évolue votre masse salariale par rapport à l'augmentation de vos clients ?",
        "options": [
            {"index": 0, "valeur": "modele_artisanal", "texte": "Progression strictement linéaire (Plus de clients = besoin d'autant de staff)"},
            {"index": 1, "valeur": "semi_automatise", "texte": "L'humain reste au cœur de la livraison de valeur, goulot d'étranglement fort"},
            {"index": 2, "valeur": "paliers_de_croissance", "texte": "Recrutements par vagues nécessaires pour soutenir la charge technique"},
            {"index": 3, "valeur": "haute_automatisation", "texte": "L'infrastructure gère la hausse, le staff n'augmente que pour le support"},
            {"index": 4, "valeur": "zero_marginal_cost", "texte": "Automatisation totale, coût marginal de livraison d'un nouveau client quasi nul"}
        ]
    },
    "couts_deploiement": {
        "id": "couts_deploiement",
        "dimension": "SCA",
        "question": "Quel est le niveau d'investissement financier (CAPEX) requis pour onboarder un grand volume de clients ?",
        "options": [
            {"index": 0, "valeur": "capex_prohibitif", "texte": "Nécessite des millions d'investissements matériels ou marketing préalables"},
            {"index": 1, "valeur": "investissements_lourds", "texte": "Besoin de lever des fonds massifs pour financer le fonds de roulement"},
            {"index": 2, "valeur": "besoin_modere", "texte": "Coûts d'acquisition d'infrastructure absorbables par la marge opérationnelle"},
            {"index": 3, "valeur": "faibles_couts", "texte": "Coût de configuration initial très faible pour chaque groupe de clients"},
            {"index": 4, "valeur": "croissance_organique_gratuite", "texte": "Coût marginal d'infrastructure transparent, autofinancement par le volume"}
        ]
    },
    "potentiel_geo": {
        "id": "potentiel_geo",
        "dimension": "SCA",
        "question": "Quelle est l'échelle géographique inscrite dans l'architecture même de votre projet ?",
        "options": [
            {"index": 0, "valeur": "hyper_local", "texte": "Solution viable uniquement à l'échelle d'une ville ou communauté restreinte"},
            {"index": 1, "valeur": "regional", "texte": "Portée limitée à quelques gouvernorats ou régions spécifiques"},
            {"index": 2, "valeur": "national", "texte": "Conçu pour couvrir l'intégralité du territoire national uniquement"},
            {"index": 3, "valeur": "continental_mena", "texte": "Adapté nativement pour cibler l'Afrique du Nord et le Moyen-Orient (MENA)"},
            {"index": 4, "valeur": "global_born_global", "texte": "Produit 'Born Global', conçu sans frontières géographiques ni culturelles"}
        ]
    },
    "climat_air": {
        "id": "climat_air",
        "dimension": "ESG",
        "question": "Quelle est la contribution directe ou indirecte de votre entreprise sur l'empreinte carbone ?",
        "options": [
            {"index": 0, "valeur": "impact_negatif_lourd", "texte": "Activité fortement carbonée sans politique de réduction ou compensation"},
            {"index": 1, "valeur": "impact_negatif_modere", "texte": "Génère des émissions de GES mais des efforts d'optimisation sont en cours"},
            {"index": 2, "valeur": "neutralite_passive", "texte": "Impact neutre par défaut (services numériques de base non éco-conçus)"},
            {"index": 3, "valeur": "impact_positif_mesurable", "texte": "Réduction active et prouvée des émissions (efficacité, circuits courts)"},
            {"index": 4, "valeur": "impact_regeneratif", "texte": "Modèle de captation carbone ou solution réduisant l'impact de tout un secteur"}
        ]
    },
    "donnees_eau_fournies": {
        "id": "donnees_eau_fournies",
        "dimension": "ESG",
        "question": "Quel niveau d'intelligence et de précision intégrez-vous dans la gestion ou la préservation de l'eau ?",
        "options": [
            {"index": 0, "valeur": "aucune_mesure", "texte": "Consommation d'eau non mesurée, aucune conscience de la ressource"},
            {"index": 1, "valeur": "estimation_theorique", "texte": "Évaluation de l'empreinte eau basée sur des moyennes théoriques floues"},
            {"index": 2, "valeur": "suivi_manuel_partiel", "texte": "Relevés réguliers mais manuels de la consommation avec correctifs tardifs"},
            {"index": 3, "valeur": "suivi_digital_temps_reel", "texte": "Monitoring digital continu (IoT/Capteurs) avec alertes instantanées"},
            {"index": 4, "valeur": "optimisation_ia_predictive", "texte": "Pilotage automatisé par IA prédisant les besoins et réduisant au strict minimum"}
        ]
    },
    "sols_biodiversite": {
        "id": "sols_biodiversite",
        "dimension": "ESG",
        "question": "Comment votre activité interagit-elle avec la santé des sols et les écosystèmes vivants ?",
        "options": [
            {"index": 0, "valeur": "degradation_active", "texte": "Utilisation d'intrants chimiques ou processus accélérant l'érosion"},
            {"index": 1, "valeur": "non_evalue", "texte": "Aucun impact direct évident et aucune métrique d'impact collectée"},
            {"index": 2, "valeur": "preservation_passive", "texte": "Pratiques limitant la casse (réduction des déchets, respect des lois)"},
            {"index": 3, "valeur": "impact_positif_certifie", "texte": "Amélioration mesurable de la qualité des terres ou baisse drastique des intrants"},
            {"index": 4, "valeur": "regeneratif_ecosysteme", "texte": "Restauration active de la biodiversité locale ou des sols (agriculture verte)"}
        ]
    },
    "ressources_dechets": {
        "id": "ressources_dechets",
        "dimension": "ESG",
        "question": "Quel est le cycle de vie des matières premières et des déchets générés par votre chaîne de valeur ?",
        "options": [
            {"index": 0, "valeur": "economie_lineaire_lourde", "texte": "Modèle 'Extraire, Fabriquer, Jeter' avec production résiduelle massive"},
            {"index": 1, "valeur": "gestion_dechets_standard", "texte": "Tri basique et respect des réglementations municipales de gestion standard"},
            {"index": 2, "valeur": "reduction_a_la_source", "texte": "Actions concrètes pour réduire la consommation de matières en amont"},
            {"index": 3, "valeur": "revalorisation_upcycling", "texte": "Transformation des déchets ou sous-produits en nouvelles matières marchandes"},
            {"index": 4, "valeur": "circularite_totale", "texte": "Modèle Zéro-Déchet natif où 100% des extrants réintègrent un cycle vertueux"}
        ]
    }
}


class ScoreEngine:
    def __init__(self):
        self.score = 0
        self.gaps = []
        self.blockers = []
        self.signaux_divergence = []
        self.score_breakdown = {}

    def ajouter_points(self, pts, raison=None):
        self.score += pts
        if raison:
            if raison not in self.score_breakdown:
                self.score_breakdown[raison] = 0
            self.score_breakdown[raison] += pts

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

    def get_stade_reel(self):
        for num, stade in STADES.items():
            if stade["score_min"] <= self.score <= stade["score_max"]:
                return stade["nom"], num
        if self.score > 100:
            return STADES[6]["nom"], 6
        return STADES[1]["nom"], 1


def evaluer_equipe(engine, data):
    equipe = data.get("equipe")
    if equipe == "complete":
        engine.ajouter_points(8, "Équipe complète")
    elif equipe == "partielle":
        engine.ajouter_points(3, "Équipe partielle")
        engine.ajouter_gap("Équipe incomplète — rôles clés manquants")
    else:  
        engine.ajouter_gap("Fondateur seul — équipe à constituer")
        engine.ajouter_blocker("organisationnel", "Absence d'équipe fondatrice", 2)


def evaluer_secteur(engine, data):
    secteur = data.get("secteur")
    if secteur == "industrie_construction":
        evaluer_industrie_construction(engine, data)
    elif secteur == "agriculture_sylviculture_peche":
        evaluer_agriculture(engine, data)
    elif secteur == "commerce_transport_logistique":
        evaluer_commerce(engine, data)
    elif secteur == "service_tourisme":
        evaluer_service_tourisme(engine, data)
    elif secteur == "tech_services_entreprise":
        evaluer_tech_services(engine, data)


def evaluer_industrie_construction(engine, data):
    equipements = data.get("indus_equipements")
    if equipements == "operationnels":
        engine.ajouter_points(10, "Équipements opérationnels")
    elif equipements == "en_cours":
        engine.ajouter_points(5, "Équipements en cours d'acquisition")
    else:
        engine.ajouter_gap("Équipements non disponibles")
        engine.ajouter_blocker("financier", "Besoin d'investissement équipements / matériel", 1)

    iso = data.get("indus_iso")
    if iso == "certifie":
        engine.ajouter_points(8, "Certification ISO obtenue")
    elif iso == "en_cours":
        engine.ajouter_points(3, "Certification ISO en cours")
    else:
        engine.ajouter_gap("Certification ISO non obtenue")

    if data.get("indus_foprodi"):
        engine.ajouter_points(5, "Dossier FOPRODI/APII")

    sous_traitance = data.get("indus_sous_traitance")
    if sous_traitance == "formels":
        engine.ajouter_points(6, "Contrats de sous-traitance formels")
    elif sous_traitance == "informellement":
        engine.ajouter_points(2, "Relations informelles")


def evaluer_agriculture(engine, data):
    if data.get("agri_certifications_sanitaires"):
        engine.ajouter_points(8, "Certifications sanitaires/phytosanitaires")
    else:
        engine.ajouter_gap("Certifications sanitaires/phytosanitaires manquantes")
        engine.ajouter_blocker("réglementaire", "Absence de certification sanitaire", 2)

    if data.get("agri_chaine_froid"):
        engine.ajouter_points(6, "Chaîne de froid opérationnelle")
    else:
        engine.ajouter_gap("Chaîne de froid / logistique non sécurisée")

    saisonnalite = data.get("agri_saisonnalite")
    if "régulière" in str(saisonnalite):
        engine.ajouter_points(4, "Activité régulière toute l'année")
    elif "Partiellement" in str(saisonnalite):
        engine.ajouter_points(2, "Activité partiellement saisonnière")
    else:
        engine.ajouter_gap("Dépendance saisonnière forte")

    acces_foncier = data.get("agri_acces_foncier")
    if "propriété ou bail" in str(acces_foncier):
        engine.ajouter_points(5, "Accès foncier sécurisé")
    elif "location" in str(acces_foncier):
        engine.ajouter_points(2, "Accès foncier court terme")
    else:
        engine.ajouter_gap("Accès foncier non sécurisé")


def evaluer_commerce(engine, data):
    reseau = data.get("com_reseau_distribution")
    if "multi-canaux" in str(reseau):
        engine.ajouter_points(10, "Réseau de distribution multi-canaux")
    elif "un ou deux" in str(reseau):
        engine.ajouter_points(5, "Points de vente établis")
    else:
        engine.ajouter_gap("Réseau de distribution non établi")

    parc = data.get("com_parc_vehicules")
    if "propre" in str(parc):
        engine.ajouter_points(8, "Parc de véhicules opérationnel")
    elif "accord" in str(parc):
        engine.ajouter_points(4, "Accord avec prestataire logistique")
    else:
        engine.ajouter_gap("Capacité logistique/transport non assurée")

    digital = data.get("com_digital")
    if "e-commerce actif" in str(digital):
        engine.ajouter_points(6, "E-commerce actif")
    elif "présence" in str(digital):
        engine.ajouter_points(2, "Présence digitale")
    else:
        engine.ajouter_gap("Absence de présence digitale")

    stock = data.get("com_stock")
    if "système" in str(stock):
        engine.ajouter_points(4, "Gestion de stock systématisée")
    elif "manuellement" in str(stock):
        engine.ajouter_points(2, "Gestion manuelle")


def evaluer_service_tourisme(engine, data):
    classement = data.get("service_classement")
    if classement == "obtenu":
        engine.ajouter_points(8, "Établissement classé/agréé")
    elif classement == "en_cours":
        engine.ajouter_points(3, "Classement en cours")

    fidelisation = data.get("service_fidelisation")
    if "programme structuré" in str(fidelisation):
        engine.ajouter_points(8, "Programme de fidélisation")
    elif "régulière" in str(fidelisation):
        engine.ajouter_points(4, "Clientèle régulière")
    else:
        engine.ajouter_gap("Absence de stratégie de fidélisation")

    numerisation = data.get("service_numerisation")
    if "opérationnel" in str(numerisation):
        engine.ajouter_points(6, "Outils numériques opérationnels")
    elif "Partiellement" in str(numerisation):
        engine.ajouter_points(2, "Numérisation partielle")

    saisonnalite = data.get("service_saisonnalite")
    if "régulière" in str(saisonnalite):
        engine.ajouter_points(4, "Activité régulière")
    elif "Partiellement" in str(saisonnalite):
        engine.ajouter_points(2, "Saisonnalité modérée")
    else:
        engine.ajouter_gap("Forte saisonnalité")


def evaluer_tech_services(engine, data):
    mvp = data.get("tech_mvp")
    if mvp == "production":
        engine.ajouter_points(12, "MVP en production")
    elif mvp == "test":
        engine.ajouter_points(8, "MVP en test")
    elif mvp == "dev":
        engine.ajouter_points(3, "MVP en développement")
        engine.ajouter_gap("MVP/offre non encore livrée")
    else:
        engine.ajouter_gap("Aucun MVP")
        engine.ajouter_blocker("technique", "Pas de produit développé", 1)

    mrr = data.get("tech_mrr")
    if mrr == "fort":
        engine.ajouter_points(15, "MRR > 5000 TND/mois")
    elif mrr == "faible":
        engine.ajouter_points(8, "MRR < 5000 TND/mois")
    elif mrr == "zero_avec_users":
        engine.ajouter_points(4, "Utilisateurs actifs sans revenus")
    else:
        engine.ajouter_gap("Aucun revenu récurrent")

    if data.get("tech_ip"):
        engine.ajouter_points(5, "Propriété intellectuelle protégée")

    scalabilite = data.get("tech_scalabilite")
    if "fortement" in str(scalabilite):
        engine.ajouter_points(6, "Modèle fortement scalable")
    elif "Partiellement" in str(scalabilite):
        engine.ajouter_points(3, "Modèle partiellement scalable")
    else:
        engine.ajouter_gap("Modèle peu scalable")


def evaluer_rne_juridique(engine, data, stade_percu):
    if data.get("rne"):
        engine.ajouter_points(10, "Entreprise enregistrée (RNE)")
        
        forme = data.get("forme_juridique")
        if forme == "Startup Act labellisée":
            engine.ajouter_points(8, "Label Startup Act")
    else:
        engine.ajouter_gap("Pas de RNE enregistré")
        engine.ajouter_blocker("légal", "Entreprise non enregistrée", 1)
        
        stades_avances = ["Fundraising", "Launch Planning", "Growth"]
        if stade_percu in stades_avances:
            engine.signal_divergence(
                f"Vous vous croyez en '{stade_percu}' mais n'avez pas de RNE — "
                "impossible de constituer un dossier bancable sans entité juridique."
            )


def evaluer_revenus_validation(engine, data, stade_percu):
    if data.get("a_revenus"):
        ca = data.get("chiffre_affaires", 0)
        
        if ca >= 500000:
            engine.ajouter_points(20, "CA très important (>500k TND)")
        elif ca >= 100000:
            engine.ajouter_points(15, "CA important (100k-500k TND)")
        elif ca >= 20000:
            engine.ajouter_points(10, "CA significatif (20k-100k TND)")
        else:
            engine.ajouter_points(5, "CA initial (<20k TND)")
        
        anciennete = data.get("anciennete_revenus")
        if "Plus de 3 ans" in str(anciennete):
            engine.ajouter_points(8, "Revenus depuis >3 ans")
        elif "1 à 3 ans" in str(anciennete):
            engine.ajouter_points(5, "Revenus depuis 1-3 ans")
        elif "6 à 12 mois" in str(anciennete):
            engine.ajouter_points(3, "Revenus depuis 6-12 mois")
    else:
        if data.get("a_clients_payants"):
            engine.ajouter_points(8, "Clients payants identifiés")
            
            if data.get("lettres_intention"):
                engine.ajouter_points(5, "Lettres d'intention/contrats signés")
            else:
                engine.ajouter_gap("Pas de contrats formalisés")
        else:
            validation = data.get("validation_type")
            if validation == "clients_potentiels":
                engine.ajouter_points(5, "Validation par clients potentiels")
            elif validation == "experts":
                engine.ajouter_points(3, "Validation par experts")
            elif validation == "proches":
                engine.ajouter_gap("Validation uniquement par des proches")
                engine.signal_divergence(
                    "Des amis ou famille intéressés ≠ traction marché réelle. "
                    "Aucun client payant détecté."
                )
            else:
                engine.ajouter_gap("Aucune validation externe")
                engine.ajouter_blocker("marché", "Idée non validée", 1)


def evaluer_business_plan(engine, data, stade_percu):
    bp = data.get("business_plan")
    if bp == "complet":
        engine.ajouter_points(10, "Business plan complet")
    elif bp == "incomplet":
        engine.ajouter_points(4, "Business plan incomplet")
        engine.ajouter_gap("Business plan incomplet ou sans projections")
    elif bp == "en_cours":
        engine.ajouter_points(2, "Business plan en cours")
    else:
        engine.ajouter_gap("Pas de business plan documenté")
        engine.ajouter_blocker("financier", "Absence de business plan", 2)
        
        if stade_percu in ["Fundraising", "Launch Planning"]:
            engine.signal_divergence(
                f"Vous vous positionnez en '{stade_percu}' mais n'avez pas de business plan. "
                "Aucune institution ne financera un dossier sans BP."
            )


def evaluer_innovation(engine, data):
    innovation = data.get("innovation")
    if "totalement nouveau" in str(innovation):
        engine.ajouter_points(8, "Innovation très haute (totalement nouveau)")
    elif "différenciée" in str(innovation):
        engine.ajouter_points(5, "Innovation moyenne (différenciée)")
    elif "moins de 2 ans" in str(innovation):
        engine.ajouter_points(2, "Innovation faible")
        engine.ajouter_gap("Marché déjà occupé par concurrents récents")
    else:
        engine.ajouter_gap("Produit existant depuis >2 ans")
        engine.signal_divergence(
            "Votre solution existe déjà depuis plusieurs années. "
            "L'innovation perçue ne se traduit pas en différenciation réelle."
        )


def evaluer_accompagnement_financement(engine, data):
    accompagnement = data.get("accompagnement")
    if accompagnement == "en_cours":
        engine.ajouter_points(6, "Accompagnement en cours")
    elif accompagnement == "termine":
        engine.ajouter_points(3, "Accompagnement terminé")

    financement = data.get("financement")
    if financement == "capital_risque":
        engine.ajouter_points(12, "Financement par capital-risque")
    elif financement == "public":
        engine.ajouter_points(8, "Financement public obtenu")
    elif financement == "love_money":
        engine.ajouter_points(3, "Love money reçu")


def scoring_f2(engine, data):
    """Évaluation multi-dimensionnelle F2"""
    
    reponses_f2 = data.get("reponses_f2", {})
    points_par_index = {
        0: 0,
        1: 3,
        2: 6,
        3: 9,
        4: 12
    }
    
    total_f2 = 0
    scores_par_dimension = {}
    
    for qid, question_data in reponses_f2.items():
        if isinstance(question_data, dict) and "index" in question_data:
            idx = question_data.get("index", 0)
            pts = points_par_index.get(idx, 0)
            
            if qid in QUESTIONS_F2:
                dimension = QUESTIONS_F2[qid].get("dimension")
                if dimension not in scores_par_dimension:
                    scores_par_dimension[dimension] = 0
                scores_par_dimension[dimension] += pts
            
            total_f2 += pts
    
    engine.ajouter_points(total_f2 // 2, "Évaluation Multi-dimensionnelle F2")
    
    return scores_par_dimension


def run_diagnostic_from_json(input_filepath):
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return None
    
    entrepreneur_id = data.get("entrepreneur_id", "ID_UNKNOWN")
    nom_entreprise = data.get("nom_entreprise", "Projet sans nom")
    localisation = data.get("localisation", "Non précisée")
    stade_percu = data.get("stade_percu", "Ideation")
    

    engine = ScoreEngine()
    
    evaluer_equipe(engine, data)
    evaluer_secteur(engine, data)
    evaluer_rne_juridique(engine, data, stade_percu)
    evaluer_revenus_validation(engine, data, stade_percu)
    evaluer_business_plan(engine, data, stade_percu)
    evaluer_innovation(engine, data)
    evaluer_accompagnement_financement(engine, data)
    scores_f2 = scoring_f2(engine, data)
    
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
            f"Auto-évaluation : '{stade_percu}' | Diagnostic : '{stade_reel_nom}'. "
            f"Lacunes principales : {', '.join(engine.gaps[:3]) if engine.gaps else 'voir détails'}."
        )
    
    stade_info = STADES[stade_reel_num]
    
    
    output = {
        "entrepreneur_id": entrepreneur_id,
        "nom_entreprise": nom_entreprise,
        "secteur": data.get("secteur"),
        "localisation": localisation,
        "stade_percu": stade_percu,
        "stade_reel": stade_reel_nom,
        "gap_detecte": gap_detecte,
        "gap_explication": gap_explication,
        "gaps": engine.gaps,
        "blockers": engine.blockers,
        "signaux_divergence": engine.signaux_divergence,
        "financement_recommande": stade_info["financement"],
        "reponses_f2": data.get("reponses_f2", {}),
        "scores_f2": scores_f2,
    }
    
    filename = f"diagnostic_{entrepreneur_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    return output


if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "final_input.json"
    result = run_diagnostic_from_json(input_file)