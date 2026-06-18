import json
# Importation de vos modules d'extraction spécifiques
from extract_sub_scores import extract_sub_scores
from extract_blockers import extract_blockers
from extract_anomalies_etapes_1 import extract_anomalies

def extract_all_scenario_data(payload):
    """
    Fonction principale orchestrant l'extraction globale.
    Prend en entrée un dictionnaire Python ou une chaîne JSON brute.
    """
    # Base parsing : assure la conversion en dict si le payload est un string
    data = json.loads(payload) if isinstance(payload, str) else payload
    
    # 1. Extraction des sous-scores et des blockers via leurs modules respectifs
    sub_scores = extract_sub_scores(data)
    blockers = extract_blockers(data.get("blockers", []))
    
    # 2. Appel à votre fonction externe pour récupérer le tableau d'anomalies
    anomalies = extract_anomalies(data)
    
    # Meta-formatting
    secteur_display = data.get("secteur", "Générique").capitalize()
    ville_display = data.get("localisation", "Tunis")
    id_brut = data.get("entrepreneur_id", "001")
    id_propre = f"PROF-{id_brut.split('-')[-1]}" if "-" in id_brut else f"PROF-{id_brut}"

    # Récupération du stade réel depuis le JSON
    stade_reel_extrait = data.get("stade_reel", "Idéation")

    return {
        "id": id_propre,
        "nom_scenario": f"Cas Démo : {secteur_display} {ville_display} - Analyse Réelle complète",
        "secteur": data.get("secteur", "autre"),
        "stade_reel": stade_reel_extrait,  # << AJOUT : Inclusion du stade réel extrait
        "sub_scores": sub_scores,
        "anomalies": anomalies,
        "blockers": blockers,
        "attendu": "FRI calculé selon les pondérations cibles du système expert."
    }


if __name__ == "__main__":
    # Nom du fichier JSON que vous possédez déjà
    fichier_cible = "test_partie_1.json"
    fichier_sortie = "output_scenario_complet.json"
    
    print(f"=== INITIALISATION DU PIPELINE D'EXTRACTION ===")
    print(f"Source : {fichier_cible}\n")
    
    try:
        # 1. Lecture et parsing du fichier JSON existant
        with open(fichier_cible, "r", encoding="utf-8") as f:
            profil_data = json.load(f)
        
        # 2. Exécution de l'orchestration globale
        resultat_final = extract_all_scenario_data(profil_data)
        
        # 3. Affichage des statistiques d'analyse dans la console
        print("=== STATISTIQUES DU PROFIL TRAITÉ ===")
        print(f"• ID Profil Généré      : {resultat_final['id']}")
        print(f"• Stade Réel Extrait    : {resultat_final['stade_reel']}")  # << Affichage du stade réel
        print(f"• Nom du Scénario       : {resultat_final['nom_scenario']}")
        print(f"• Anomalies détectées   : {len(resultat_final['anomalies'])}")
        print(f"• Bloqueurs extraits    : {len(resultat_final['blockers'])}")
        print("\n" + "="*60 + "\n")
        
        # 4. Affichage du rendu JSON structuré attendu
        print("=== LIVRABLE JSON STRUCTURÉ ===")
        print(json.dumps(resultat_final, indent=4, ensure_ascii=False))

        # 5. Sauvegarde automatique du résultat pour les étapes suivantes
        with open(fichier_sortie, "w", encoding="utf-8") as f_out:
            json.dump(resultat_final, f_out, indent=4, ensure_ascii=False)
        print(f"\n[Succès] Résultat global exporté avec succès dans '{fichier_sortie}'")

    except FileNotFoundError:
        print(f"[Erreur] Le fichier '{fichier_cible}' est introuvable. Placez-le dans le même dossier.")
    except json.JSONDecodeError as e:
        print(f"[Erreur] Échec du parsing. Vérifiez la syntaxe JSON de '{fichier_cible}' : {e}")