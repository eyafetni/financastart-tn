# f2_scoring/pipeline.py
"""
Orchestrateur Principal — Pipeline Global.
Prend le profil brut de l'entrepreneur (JSON) et retourne le contrat F2 finalisé.
"""
import os
import json
from typing import Any

# Imports de tes modules d'extraction (Phase 1)
from extraction_donnees.extract_sub_scores import extract_sub_scores
from extraction_donnees.extract_anomalies_etapes_1 import extract_anomalies as extract_anomalies_p1
from extraction_donnees.extract_blockers import extract_blockers

# Import du moteur de calcul (Phase 2)
from calcul_scores import calculer_scores

def executer_pipeline_complet(profil_entrepreneur_json: str | dict[str, Any]) -> dict[str, Any]:
    """
    Prend le profil JSON brut de l'entrepreneur et retourne le contrat F2 finalisé
    avec les clés 'justification' correctement nommées à la place de 'description'.
    """
    # 1. Sérialisation / Désérialisation sécurisée
    if isinstance(profil_entrepreneur_json, str):
        profil_data = json.loads(profil_entrepreneur_json)
    else:
        profil_data = profil_entrepreneur_json

    # 2. Extraction Phase 1 (Indicateurs, Bloqueurs, Premières anomalies)
    # Note : Ajuste les noms de fonctions selon tes signatures exactes
    sub_scores_extraits = extract_sub_scores(profil_data)
    anomalies_p1 = extract_anomalies_p1(profil_data)
    blockers_extraits = extract_blockers(profil_data)
    
    # Récupération du secteur (clé 'sector' souvent présente à la racine du profil)
    secteur = profil_data.get("sector", "Général")

    # 3. Calcul des Scores et Enrichissement Phase 2
    contrat_f2 = calculer_scores(
        sub_scores=sub_scores_extraits,
        anomalies=anomalies_p1,
        blockers=blockers_extraits,
        secteur=secteur
    )

    # 4. Post-processing : Transformation finale pour basculer de 'description' à 'justification'
    if "anomalies_detectees" in contrat_f2:
        anomalies_modifiees = []
        for anom in contrat_f2["anomalies_detectees"]:
            # On crée un nouveau dictionnaire pour réordonner proprement les clés
            nouvelle_anomalie = {
                "id": anom.get("id", "?"),
                "justification": anom.get("description", ""),  # Le changement majeur est ici
                "penalite": anom.get("penalite", 0),
                "dimension_impactee": anom.get("dimension_impactee", ""),
                "justification_template": anom.get("justification_template", ""),
                "action_template": anom.get("action_template", ""),
                "kb_link": anom.get("kb_link", "")
            }
            anomalies_modifiees.append(nouvelle_anomalie)
            
        contrat_f2["anomalies_detectees"] = anomalies_modifiees

    return contrat_f2
def tester_conversion_fichier(fichier_entree: str, fichier_sortie: str) -> None:
    """
    Prend le chemin d'un fichier JSON d'entrée, applique le pipeline,
    et écrit le résultat mis en forme dans le fichier de sortie.
    """
    print(f"🚀 Démarrage du test de conversion...")
    print(f"📂 Lecture du profil brut : {fichier_entree}")
    
    # 1. Vérification et lecture du fichier d'entrée
    if not os.path.exists(fichier_entree):
        print(f"❌ Erreur : Le fichier d'entrée '{fichier_entree}' n'existe pas.")
        return
        
    with open(fichier_entree, "r", encoding="utf-8") as f:
        try:
            profil_brut = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Erreur : Le fichier d'entrée n'est pas un JSON valide. Details : {e}")
            return

    # 2. Exécution du pipeline complet
    try:
        print("⚙️  Exécution du pipeline global (Phase 1 + Phase 2)...")
        contrat_final = executer_pipeline_complet(profil_brut)
    except Exception as e:
        print(f"❌ Erreur critique pendant l'exécution du pipeline : {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. Création automatique du dossier de sortie s'il n'existe pas
    dossier_sortie = os.path.dirname(fichier_sortie)
    if dossier_sortie and not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie, exist_ok=True)

    # 4. Écriture du fichier de sortie
    with open(fichier_sortie, "w", encoding="utf-8") as f:
        json.dump(contrat_final, f, indent=4, ensure_ascii=False)
        
    print(f"✨ Succès ! Contrat F2 généré avec succès.")
    print(f"💾 Résultat disponible ici : {fichier_sortie}\n")
    
    # 5. Petit check visuel rapide dans la console pour l'anomalie régionale
    print("🔍 Vérification rapide de la structure des anomalies détectées :")
    anoms = contrat_final.get("anomalies_detectees", [])
    if anoms:
        for a in anoms[:2]: # Affiche les deux premières pour valider
            print(f"  - ID: {a.get('id')} | justification: {a.get('justification')[:50]}...")
    else:
        print("  ⚠️ Aucune anomalie détectée dans ce profil.")


if __name__ == "__main__":

    _THIS_DIR = os.path.dirname(os.path.abspath(__file__))  # f2_scoring/tests
    _ROOT_DIR = os.path.dirname(_THIS_DIR)                 # f2_scoring
    # Puisque test_partie_1.json est à la racine de f2_scoring (_ROOT_DIR)
    FICHIER_INPUT = os.path.join(_ROOT_DIR, "f2_scoring/test_partie_1.json")
    
    # Pour la sortie, on le génère au même endroit pour que tu le voies tout de suite
    FICHIER_OUTPUT = os.path.join(_ROOT_DIR, "f2_scoring/contrat_f2_output.json")
    
    # Lancement du test
    tester_conversion_fichier(FICHIER_INPUT, FICHIER_OUTPUT)