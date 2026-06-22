import json
from pathlib import Path
from datetime import datetime

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
        "timestamp": data.get("timestamp", datetime.now().isoformat()),
        "nom_scenario": f"Cas Démo : {secteur_display} {ville_display} - Analyse Réelle complète",

        # ── Contexte de diagnostic (stade perçu vs réel) ──
        "secteur": data.get("secteur", "autre"),
        "secteur_label": data.get("secteur_label"),
        "localisation": data.get("localisation"),
        "stade_reel": data.get("stade_reel", "Idéation"),
        "stade_percu": data.get("stade_percu"),
        "score_diagnostic": data.get("score_diagnostic"),
        "gap_detecte": data.get("gap_detecte", False),
        "gap_explication": data.get("gap_explication"),
        "gaps": data.get("gaps", []),
        "signaux_divergence": data.get("signaux_divergence", []),
        "financement_recommande": data.get("financement_recommande"),

        # ── Profil complet exposé tel quel (tout le détail entrepreneur) ──
        "profil_complet": data.get("profil_complet", {}),

        # ── Scores et anomalies calculés ──
        "sub_scores": sub_scores,
        "anomalies": anomalies,
        "blockers": blockers,

        "attendu": "FRI calculé selon les pondérations cibles du système expert."
    }


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    fichier_cible = script_dir / "test_partie_1.json"
    fichier_sortie = script_dir / "output_scenario_complet.json"

    print(f"=== INITIALISATION DU PIPELINE ===")
    print(f"Recherche du fichier dans : {fichier_cible}")

    try:
        with open(fichier_cible, "r", encoding="utf-8") as f:
            profil_data = json.load(f)

        resultat_final = extract_all_scenario_data(profil_data)

        with open(fichier_sortie, "w", encoding="utf-8") as f_out:
            json.dump(resultat_final, f_out, indent=4, ensure_ascii=False)

        print(f"\n[Succès] Traitement terminé. Résultat sauvegardé dans : {fichier_sortie}")

    except FileNotFoundError:
        print(f"\n[ERREUR] Impossible de trouver le fichier : {fichier_cible}")
        print("Vérifiez que le fichier 'test_partie_1.json' est bien dans le même dossier que ce script.")
    except json.JSONDecodeError as e:
        print(f"\n[ERREUR] Fichier JSON invalide : {e}")