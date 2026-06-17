import json
# Import de tes fonctions depuis ton fichier d'extraction
from extract_all_scenarios_data import extract_all_scenario_data

# 1. Le Payload brut de test à injecter
json_payload_test = """
{
    "entrepreneur_id": "ENT-F9FD5C",
    "secteur": "agritech",
    "localisation": "Sfax",
    "blockers": [
        {
            "domaine": "organisationnel",
            "description": "Absence d'équipe fondatrice",
            "priorite": 2
        },
        {
            "domaine": "légal",
            "description": "Entreprise non enregistrée",
            "priorite": 1
        }
    ],
    "profil_complet": {
        "chiffre_affaires": 55500000.0,
        "rne": false
    },
    "reponses_questionnaire": {
        "potentiel_financier_marche": {"index": 0},
        "intensite_concurrence": {"index": 1},
        "niveau_traction": {"index": 2},
        "modele_revenu": {"index": 3},
        "business_plan_maturite": {"index": 4},
        "maturite_produit": {"index": 1},
        "strategie_prix": {"index": 2},
        "alignement_besoins": {"index": 3},
        "nouveaute_locale": {"index": 4},
        "intensite_tech": {"index": 0},
        "barrieres_entree": {"index": 1},
        "degre_rupture": {"index": 2},
        "replicabilite": {"index": 3},
        "independance_manuelle": {"index": 4},
        "couts_deploiement": {"index": 0},
        "potentiel_geo": {"index": 1},
        "climat_air": {"index": 2},
        "donnees_eau_fournies": {"index": 3},
        "sols_biodiversite": {"index": 4},
        "ressources_dechets": {"index": 2}
    }
}
"""

# 2. Exécution du test d'intégration
if __name__ == "__main__":
    print("🚀 Lancement du test d'extraction global (Fichier Séparé)...")
    
    # Appel de la fonction principale
    resultat = extract_all_scenario_data(json_payload_test)
    
    # Validation visuelle du format de sortie
    print("\n📊 RÉSULTAT OBTENU :")
    print(json.dumps(resultat, indent=4, ensure_ascii=False))