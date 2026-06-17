"""
AINS Hackathon 2026 – Feature 1
Moteur de Diagnostic Adaptatif — Questionnaire Intelligent
Classifie la vraie maturité entrepreneuriale (pas celle déclarée)
"""

import json
import uuid
from datetime import datetime


# ─────────────────────────────────────────────
# TAXONOMIE DES 6 STADES
# ─────────────────────────────────────────────
STADES = {
    1: {
        "nom": "Ideation",
        "description": "Idée sans validation ni équipe complète",
        "financement": "Love money / Concours",
        "score_min": 0,
        "score_max": 15,
    },
    2: {
        "nom": "Market Validation",
        "description": "Premiers clients / traction naissante",
        "financement": "Microfinance / BTS",
        "score_min": 16,
        "score_max": 30,
    },
    3: {
        "nom": "Structuration",
        "description": "Structure juridique / business plan",
        "financement": "APII / ANPE",
        "score_min": 31,
        "score_max": 50,
    },
    4: {
        "nom": "Fundraising",
        "description": "Dossier bancable en construction",
        "financement": "BFPME / Startup Act",
        "score_min": 51,
        "score_max": 65,
    },
    5: {
        "nom": "Launch Planning",
        "description": "Produit validé / prêt à lever",
        "financement": "Capital risque / ANAVA",
        "score_min": 66,
        "score_max": 80,
    },
    6: {
        "nom": "Growth",
        "description": "Revenus existants / expansion",
        "financement": "Lignes bancaires / AFD / EU",
        "score_min": 81,
        "score_max": 100,
    },
}

# ─────────────────────────────────────────────
# HELPERS UI
# ─────────────────────────────────────────────

def afficher_titre():
    print("\n")
    print("       Diagnostic de Maturité Entrepreneuriale")
    print("   Ce diagnostic évalue votre projet objectivement.")


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


# ─────────────────────────────────────────────
# MOTEUR DE SCORE
# ─────────────────────────────────────────────

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


# ─────────────────────────────────────────────
# BRANCHES SECTORIELLES
# ─────────────────────────────────────────────

def branche_agroalimentaire(engine, profil):
    print("\n  📌 Section spécifique : Agroalimentaire")

    certif = poser_question(
        "Avez-vous des certifications sanitaires (ISO 22000, HACCP, etc.) ?",
        type_reponse="oui_non"
    )
    if certif == "Oui":
        engine.ajouter_points(8, "Certifications sanitaires")
        profil["certifications_sanitaires"] = True
    else:
        engine.ajouter_gap("Certifications sanitaires manquantes")
        engine.ajouter_blocker("réglementaire", "Absence de certification sanitaire", 2)
        profil["certifications_sanitaires"] = False

    chaine_froid = poser_question(
        "Avez-vous une chaîne de froid opérationnelle ou un accord avec un prestataire ?",
        type_reponse="oui_non"
    )
    if chaine_froid == "Oui":
        engine.ajouter_points(6)
    else:
        engine.ajouter_gap("Chaîne de froid non sécurisée")

    saisonnalite = poser_question(
        "Votre activité est-elle saisonnière ?",
        ["Oui, fortement saisonnière", "Partiellement", "Non, activité régulière"]
    )
    if saisonnalite == "Non, activité régulière":
        engine.ajouter_points(4)
    elif saisonnalite == "Partiellement":
        engine.ajouter_points(2)
    else:
        engine.ajouter_gap("Dépendance saisonnière forte — modèle de revenus à stabiliser")

    profil["saisonnalite"] = saisonnalite


def branche_tech(engine, profil):
    print("\n  📌 Section spécifique : Tech")

    mvp = poser_question(
        "Avez-vous un MVP (produit minimum viable) fonctionnel ?",
        ["Oui, en production", "Oui, en test avec utilisateurs réels", "En développement", "Non"]
    )
    if mvp == "Oui, en production":
        engine.ajouter_points(12)
        profil["mvp_statut"] = "production"
    elif mvp == "Oui, en test avec utilisateurs réels":
        engine.ajouter_points(8)
        profil["mvp_statut"] = "test"
    elif mvp == "En développement":
        engine.ajouter_points(3)
        profil["mvp_statut"] = "dev"
        engine.ajouter_gap("MVP non encore livré")
    else:
        engine.ajouter_gap("Aucun MVP — stade idéation confirmé")
        engine.ajouter_blocker("technique", "Pas de produit développé", 1)
        profil["mvp_statut"] = "absent"

    mrr = poser_question(
        "Avez-vous un MRR (revenu mensuel récurrent) ?",
        ["Oui, > 5 000 TND/mois", "Oui, < 5 000 TND/mois", "Non, mais des utilisateurs actifs", "Non"]
    )
    if "Oui, > 5 000" in mrr:
        engine.ajouter_points(15)
        profil["mrr"] = "fort"
    elif "Oui, < 5 000" in mrr:
        engine.ajouter_points(8)
        profil["mrr"] = "faible"
    elif "utilisateurs actifs" in mrr:
        engine.ajouter_points(4)
        profil["mrr"] = "zero_avec_users"
    else:
        engine.ajouter_gap("Aucun revenu récurrent")
        profil["mrr"] = "zero"

    ip = poser_question(
        "Avez-vous protégé votre propriété intellectuelle (brevet, marque déposée) ?",
        type_reponse="oui_non"
    )
    if ip == "Oui":
        engine.ajouter_points(5)
        profil["propriete_intellectuelle"] = True
    else:
        profil["propriete_intellectuelle"] = False


def branche_industrie(engine, profil):
    print("\n  📌 Section spécifique : Industrie")

    equipements = poser_question(
        "Avez-vous les équipements de production nécessaires ?",
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
        engine.ajouter_blocker("financier", "Besoin d'investissement équipements", 1)
        profil["equipements"] = "absent"

    iso = poser_question(
        "Êtes-vous certifié ISO ou en cours de certification ?",
        ["Certifié ISO 9001 ou autre", "En cours de certification", "Non, pas encore"]
    )
    if "Certifié" in iso:
        engine.ajouter_points(8)
    elif "cours" in iso:
        engine.ajouter_points(3)
    else:
        engine.ajouter_gap("Certification ISO non obtenue")

    foprodi = poser_question(
        "Avez-vous déposé un dossier FOPRODI ?",
        type_reponse="oui_non"
    )
    if foprodi == "Oui":
        engine.ajouter_points(5)
        profil["foprodi"] = True
    else:
        profil["foprodi"] = False


# ─────────────────────────────────────────────
# QUESTIONNAIRE PRINCIPAL
# ─────────────────────────────────────────────

def run_diagnostic():
    afficher_titre()
    engine = ScoreEngine()
    profil = {}

    # ── BLOC 1 : Profil de base + Auto-évaluation (texte libre) ──
    print("\n  📋 ÉTAPE 1 — Présentation de votre projet")
    print("  " + "─" * 50)
    print("  Décrivez votre projet en quelques lignes en précisant :")
    print("    • Le secteur d'activité  (ex: Agroalimentaire, Tech, Industrie, Services...)")
    print("    • La région où vous êtes basé  (ex: Tunis, Sfax, Sousse...)")
    print("    • Le nom de votre entreprise ou projet")
    print("    • Selon vous, à quel stade en êtes-vous aujourd'hui ?")
    print("      (Ideation / Market Validation / Structuration /")
    print("       Fundraising / Launch Planning / Growth)")
    print()

    description_libre = poser_question(
        "Votre description (appuyez sur Entrée quand vous avez terminé) :",
        type_reponse="texte"
    )
    profil["description_libre"] = description_libre

    entrepreneur_id = f"ENT-{str(uuid.uuid4())[:6].upper()}"
    profil["entrepreneur_id"] = entrepreneur_id

    # ── Extraction guidée depuis la description libre ──
    print("\n  Merci ! Quelques précisions rapides pour compléter votre profil :\n")

    nom_entreprise = poser_question(
        "Nom de votre entreprise / projet :",
        type_reponse="texte"
    )
    profil["nom_entreprise"] = nom_entreprise

    # Extraction du secteur
    SECTEURS_VALIDES = ["Agroalimentaire", "Tech", "Industrie", "Services", "Commerce", "Autre"]
    secteur_detecte = None
    desc_lower = description_libre.lower()
    if any(k in desc_lower for k in ["agri", "food", "agricol", "agroaliment"]):
        secteur_detecte = "Agroalimentaire"
    elif any(k in desc_lower for k in ["tech", "digital", "logiciel", "app", "web", "ia", "ai", "saas"]):
        secteur_detecte = "Tech"
    elif any(k in desc_lower for k in ["industri", "manufactur", "product", "usine", "fabricat"]):
        secteur_detecte = "Industrie"
    elif any(k in desc_lower for k in ["service", "conseil", "formation", "consulting"]):
        secteur_detecte = "Services"
    elif any(k in desc_lower for k in ["commerc", "vente", "retail", "boutique", "distribut"]):
        secteur_detecte = "Commerce"

    if secteur_detecte:
        print(f"\n  ─────────────────────────────────────────────────")
        print(f"  Secteur détecté depuis votre description : {secteur_detecte}")
        confirmation = poser_question(
            "Est-ce correct ?",
            type_reponse="oui_non"
        )
        if confirmation == "Non":
            secteur_detecte = None

    if not secteur_detecte:
        secteur_detecte = poser_question(
            "Confirmez votre secteur d'activité :",
            SECTEURS_VALIDES
        )

    profil["secteur"] = secteur_detecte.lower().replace(" / ", "_").replace(" ", "_")

    # Extraction de la localisation
    REGIONS = ["Tunis", "Sfax", "Sousse", "Monastir", "Bizerte", "Autre région"]
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

    # Extraction du stade perçu
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

    # Question équipe (reste en choix guidé — information non extractible fiablement)
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

    # ── BLOC 2 : Branches sectorielles ──
    print("\n  📋 ÉTAPE 2 — Questions sectorielles")
    if profil["secteur"] == "agroalimentaire":
        branche_agrifood(engine, profil)
    elif profil["secteur"] == "tech":
        branche_tech(engine, profil)
    elif profil["secteur"] == "industrie":
        branche_industrie(engine, profil)
    else:
        # Branche générique pour services/commerce/autre
        print("\n  📌 Section générique")
        activite_principale = poser_question(
            "Votre activité principale est-elle clairement définie et documentée ?",
            ["Oui, avec un business model détaillé",
             "Partiellement définie",
             "Non, encore en réflexion"]
        )
        if "détaillé" in activite_principale:
            engine.ajouter_points(8)
        elif "Partiellement" in activite_principale:
            engine.ajouter_points(3)
        else:
            engine.ajouter_gap("Business model non défini")

    # ── BLOC 3 : Structure juridique ──
    print("\n  📋 ÉTAPE 3 — Structure juridique")

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

        # Signal divergence potentiel si l'entrepreneur se croit à Fundraising+
        stades_avances = ["Fundraising", "Launch Planning", "Growth"]
        if stade_percu in stades_avances:
            engine.signal_divergence(
                f"Vous vous croyez en '{stade_percu}' mais n'avez pas de RNE — "
                "impossible de constituer un dossier bancable sans entité juridique."
            )

    # ── BLOC 4 : Revenus et validation marché ──
    print("\n  📋 ÉTAPE 4 — Revenus et validation marché")

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
                engine.ajouter_gap("Pas de contrats/lettres d'intention formalisés")
                profil["lettres_intention"] = False
        else:
            # Creuser la validation
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

    # ── BLOC 5 : Business Plan et dossier ──
    print("\n  📋 ÉTAPE 5 — Business Plan et dossier")

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

        # Signal divergence si prétend Fundraising sans BP
        if stade_percu in ["Fundraising", "Launch Planning"]:
            engine.signal_divergence(
                f"Vous vous positionnez en '{stade_percu}' mais n'avez pas de business plan. "
                "Aucune institution financière tunisienne n'étudiera un dossier sans BP."
            )

    # ── BLOC 6 : Innovation ──
    print("\n  📋 ÉTAPE 6 — Innovation et différenciation")

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
        engine.ajouter_gap("Produit existant sur le marché tunisien depuis plus de 2 ans")
        # Cas divergence 3 : prétend très innovant mais produit ancien
        engine.signal_divergence(
            "Votre solution existe déjà sur le marché tunisien depuis plusieurs années. "
            "L'innovation perçue ne se traduit pas en différenciation réelle."
        )

    # ── BLOC 7 : Accompagnement et financement ──
    print("\n  📋 ÉTAPE 7 — Accompagnement et financement")

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

    # ─────────────────────────────────────────────
    # CALCUL FINAL
    # ─────────────────────────────────────────────

    stade_reel_nom, stade_reel_num = engine.get_stade_reel()

    # Trouver le numéro du stade perçu
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

    print("\n" + "═" * 60)
    print("   📊  RÉSULTATS DU DIAGNOSTIC")
    print("═" * 60)
    print(f"  Projet        : {profil.get('nom_entreprise', 'N/A')} ({entrepreneur_id})")
    print(f"  Secteur       : {profil['secteur']}")
    print(f"  Localisation  : {localisation}")
    print(f"\n  Stade perçu   : {stade_percu}")
    print(f"  Stade réel    : {stade_reel_nom}  (score: {engine.score}/100)")

    if gap_detecte:
        print(f"\n  ⚠️  GAP DÉTECTÉ !")
        print(f"  {gap_explication}")
    else:
        print(f"\n  ✅ Votre auto-évaluation correspond au diagnostic.")

    if engine.gaps:
        print(f"\n  🔴 Lacunes identifiées :")
        for g in engine.gaps:
            print(f"     • {g}")

    if engine.blockers:
        print(f"\n  🚧 Blockers prioritaires :")
        sorted_blockers = sorted(engine.blockers, key=lambda x: x["priorite"])
        for b in sorted_blockers:
            print(f"     [{b['priorite']}] {b['domaine'].upper()} — {b['description']}")

    stade_info = STADES[stade_reel_num]
    print(f"\n  💡 Financement adapté à votre stade réel : {stade_info['financement']}")
    print("═" * 60)

    # ─────────────────────────────────────────────
    # EXPORT JSON — Contrat F1
    # ─────────────────────────────────────────────

    output = {
        "entrepreneur_id": entrepreneur_id,
        "timestamp": datetime.now().isoformat(),
        "stade_reel": stade_reel_nom,
        "stade_percu": stade_percu,
        "score_diagnostic": engine.score,
        "gap_detecte": gap_detecte,
        "gap_explication": gap_explication,
        "gaps": engine.gaps,
        "blockers": engine.blockers,
        "secteur": profil.get("secteur", "Non précisé"),
        "localisation": profil.get("localisation", "Non précisé"),
        "profil_complet": profil,
        "signaux_divergence": engine.signaux_divergence,
        "financement_recommande": stade_info["financement"],
    }

    filename = f"diagnostic_{entrepreneur_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n  📁 Fichier JSON exporté : {filename} (dans le dossier où vous avez lancé le script)")
    print("═" * 60 + "\n")

    return output


# ─────────────────────────────────────────────
# CAS DE DIVERGENCE DOCUMENTÉS (Tests)
# ─────────────────────────────────────────────

def run_cas_divergence():
    """
    Simule les 3 cas de divergence documentés sans interaction utilisateur.
    Retourne les 3 JSONs pour documentation et tests.
    """

    cas = []

    # ── CAS 1 : Prêt pour BFPME (Fundraising) → Structuration ──
    cas1 = {
        "entrepreneur_id": "ENT-CAS01",
        "timestamp": datetime.now().isoformat(),
        "stade_reel": "Structuration",
        "stade_percu": "Fundraising",
        "score_diagnostic": 22,
        "gap_detecte": True,
        "gap_explication": (
            "L'entrepreneur se croit prêt pour financement BFPME mais n'a pas de RNE enregistré "
            "et aucun business plan documenté. La BFPME exige une entité juridique formelle "
            "et un dossier bancable complet — deux prérequis absents ici."
        ),
        "gaps": [
            "Pas de RNE enregistré",
            "Pas de business plan documenté",
            "Zéro client payant"
        ],
        "blockers": [
            {"domaine": "légal", "description": "Entreprise non enregistrée", "priorite": 1},
            {"domaine": "financier", "description": "Absence de business plan", "priorite": 2},
            {"domaine": "marché", "description": "Validation client insuffisante", "priorite": 3}
        ],
        "secteur": "agroalimentaire",
        "localisation": "Sfax",
        "signaux_divergence": [
            "Vous vous croyez en 'Fundraising' mais n'avez pas de RNE — impossible de constituer un dossier bancable.",
            "Vous vous positionnez en 'Fundraising' mais n'avez pas de business plan."
        ],
        "financement_recommande": "Microfinance / BTS",
        "cas_reference": "CAS-01",
        "cas_description": "Entrepreneur convaincu d'être prêt pour la BFPME sans structure juridique ni BP"
    }
    cas.append(cas1)

    # ── CAS 2 : J'ai de la traction marché → Ideation ──
    cas2 = {
        "entrepreneur_id": "ENT-CAS02",
        "timestamp": datetime.now().isoformat(),
        "stade_reel": "Ideation",
        "stade_percu": "Market Validation",
        "score_diagnostic": 8,
        "gap_detecte": True,
        "gap_explication": (
            "L'entrepreneur interprète l'enthousiasme de son entourage comme de la traction marché. "
            "Aucun client payant, aucune lettre d'intention, aucune validation par des experts sectoriels. "
            "Des amis intéressés ≠ demande marché réelle. Le projet est en stade idéation."
        ),
        "gaps": [
            "Aucun client payant identifié",
            "Validation uniquement par des proches — non représentative",
            "Pas de contrats ni lettres d'intention",
            "Aucune étude de marché formelle"
        ],
        "blockers": [
            {"domaine": "marché", "description": "Traction non prouvée par des clients réels", "priorite": 1},
            {"domaine": "financier", "description": "Zéro revenu généré", "priorite": 2}
        ],
        "secteur": "tech_digital",
        "localisation": "Tunis",
        "signaux_divergence": [
            "Des amis ou de la famille intéressés par votre idée ≠ traction marché réelle. Aucun client payant détecté."
        ],
        "financement_recommande": "Love money / Concours",
        "cas_reference": "CAS-02",
        "cas_description": "Entrepreneur confondant intérêt de l'entourage avec validation marché"
    }
    cas.append(cas2)

    # ── CAS 3 : Mon projet est très innovant → Innovation Score faible ──
    cas3 = {
        "entrepreneur_id": "ENT-CAS03",
        "timestamp": datetime.now().isoformat(),
        "stade_reel": "Market Validation",
        "stade_percu": "Launch Planning",
        "score_diagnostic": 28,
        "gap_detecte": True,
        "gap_explication": (
            "L'entrepreneur se perçoit comme très innovant et prêt au lancement, "
            "mais un produit identique existe sur le marché tunisien depuis plus de 3 ans. "
            "L'innovation perçue est subjective — le diagnostic objectif révèle une différenciation "
            "insuffisante et un positionnement non défendu face aux concurrents établis."
        ),
        "gaps": [
            "Produit identique existant sur le marché tunisien depuis 3+ ans",
            "Pas de barrière à l'entrée identifiée",
            "Différenciation non documentée face aux concurrents",
            "Pas de propriété intellectuelle protégée"
        ],
        "blockers": [
            {"domaine": "marché", "description": "Concurrents établis non adressés dans la stratégie", "priorite": 1},
            {"domaine": "technique", "description": "Aucune protection IP", "priorite": 2},
            {"domaine": "organisationnel", "description": "Positionnement marché flou", "priorite": 3}
        ],
        "secteur": "tech_digital",
        "localisation": "Sousse",
        "signaux_divergence": [
            "Votre solution existe déjà sur le marché tunisien depuis plusieurs années. "
            "L'innovation perçue ne se traduit pas en différenciation réelle."
        ],
        "financement_recommande": "Microfinance / BTS",
        "cas_reference": "CAS-03",
        "cas_description": "Entrepreneur surestimant l'innovation d'un produit déjà existant en Tunisie"
    }
    cas.append(cas3)

    return cas


# ─────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--cas-divergence":
        # Mode documentation des cas de divergence
        print("\n" + "═" * 60)
        print("   📋  CAS DE DIVERGENCE DOCUMENTÉS")
        print("═" * 60)

        cas = run_cas_divergence()

        for c in cas:
            print(f"\n  🔍 {c['cas_reference']} : {c['cas_description']}")
            print(f"     Stade perçu  : {c['stade_percu']}")
            print(f"     Stade réel   : {c['stade_reel']}")
            print(f"     Explication  : {c['gap_explication'][:100]}...")

            filename = f"cas_divergence_{c['cas_reference']}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(c, f, ensure_ascii=False, indent=2)
            print(f"     → Exporté : {filename}")

        print("\n  ✅ 3 cas exportés avec succès.\n")

    else:
        # Mode diagnostic interactif normal
        result = run_diagnostic()
