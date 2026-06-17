import json
from extract_sub_scores import extract_sub_scores
from extract_blockers import extract_blockers
from extract_anomalies_etapes_1 import extract_anomalies  # Import de ta fonction existante

def extract_all_scenario_data(payload):
    """Fonction principale orchestrant l'extraction globale."""
    # Base parsing : convertit en dict si c'est une chaîne JSON, sinon garde le dict
    data = json.loads(payload) if isinstance(payload, str) else payload
    
    # 1. Extraction des sous-scores et des blockers via leurs modules respectifs
    sub_scores = extract_sub_scores(data)
    blockers = extract_blockers(data.get("blockers", []))
    
    # 2. Appel direct à ta fonction externe pour récupérer le tableau d'anomalies
    anomalies = extract_anomalies(data)
    
    # Meta-formatting
    secteur_display = data.get("secteur", "Générique").capitalize()
    ville_display = data.get("localisation", "Tunis")
    id_brut = data.get("entrepreneur_id", "001")
    id_propre = f"PROF-{id_brut.split('-')[-1]}" if "-" in id_brut else f"PROF-{id_brut}"

    return {
        "id": id_propre,
        "nom_scenario": f"Cas Démo : {secteur_display} {ville_display} - Analyse Réelle complète",
        "secteur": data.get("secteur", "autre"),
        "sub_scores": sub_scores,
        "anomalies": anomalies,
        "blockers": blockers,
        "attendu": "FRI calculé selon les pondérations cibles du système expert."
    }


if __name__ == "__main__":
    # Nom du fichier JSON externe à charger (généré à l'étape précédente)
    fichier_cible = "test_partie_1.json"
    
    print(f"=== CHARGEMENT ET ANALYSE DU FICHIER : {fichier_cible} ===")
    
    try:
        # 1. Lecture et parsing du fichier JSON
        with open(fichier_cible, "r", encoding="utf-8") as f:
            profil_data = json.load(f)
        
        # 2. Exécution de l'orchestration globale
        resultat_final = extract_all_scenario_data(profil_data)
        
        # 3. Affichage des statistiques et du rapport final
        print(f"\nID Profil Traité : {resultat_final['id']}")
        print(f"Nom du Scénario : {resultat_final['nom_scenario']}")
        print(f"Nombre d'anomalies détectées : {len(resultat_final['anomalies'])}")
        print(f"Nombre de blockers extraits    : {len(resultat_final['blockers'])}")
        print("\n" + "="*60 + "\n")
        
        # Affichage du rendu JSON attendu par ton système expert
        print(json.dumps(resultat_final, indent=4, ensure_ascii=False))

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{fichier_cible}' est introuvable. Vérifiez son emplacement.")
    except json.JSONDecodeError as e:
        print(f"Erreur de syntaxe JSON dans '{fichier_cible}' : {e}")