import json
from pathlib import Path
# Importation de vos modules
from extract_sub_scores import extract_sub_scores
from extract_blockers import extract_blockers
from extract_anomalies_etapes_1 import extract_anomalies

def extract_all_scenario_data(data):
    """Orchestrateur d'extraction."""
    sub_scores = extract_sub_scores(data)
    blockers = extract_blockers(data)
    anomalies = extract_anomalies(data)
    
    secteur_display = data.get("secteur", "Générique").capitalize()
    ville_display = data.get("localisation", "Tunis")
    id_brut = data.get("entrepreneur_id", "001")
    id_propre = f"PROF-{id_brut.split('-')[-1]}" if "-" in id_brut else f"PROF-{id_brut}"

    return {
        "id": id_propre,
        "nom_scenario": f"Cas Démo : {secteur_display} {ville_display} - Analyse Réelle complète",
        "secteur": data.get("secteur", "autre"),
        "stade_reel": data.get("stade_reel", "Idéation"),
        "sub_scores": sub_scores,
        "anomalies": anomalies,
        "blockers": blockers,
        "attendu": "FRI calculé selon les pondérations cibles du système expert."
    }

if __name__ == "__main__":
    # 1. Définition du chemin robuste (localise le dossier du script actuel)
    script_dir = Path(__file__).resolve().parent
    fichier_cible = script_dir / "test_partie_1.json"
    fichier_sortie = script_dir / "output_scenario_complet.json"
    
    print(f"=== INITIALISATION DU PIPELINE ===")
    print(f"Recherche du fichier dans : {fichier_cible}")
    
    try:
        # 2. Lecture sécurisée
        with open(fichier_cible, "r", encoding="utf-8") as f:
            profil_data = json.load(f)
        
        # 3. Exécution
        resultat_final = extract_all_scenario_data(profil_data)
        
        # 4. Export
        with open(fichier_sortie, "w", encoding="utf-8") as f_out:
            json.dump(resultat_final, f_out, indent=4, ensure_ascii=False)
            
        print(f"\n[Succès] Traitement terminé. Résultat sauvegardé dans : {fichier_sortie}")

    except FileNotFoundError:
        print(f"\n[ERREUR] Impossible de trouver le fichier : {fichier_cible}")
        print("Vérifiez que le fichier 'test_partie_1.json' est bien dans le même dossier que ce script.")
    except json.JSONDecodeError as e:
        print(f"\n[ERREUR] Fichier JSON invalide : {e}")