import json
import sys
import os

# Ajustement du path pour détecter le module f2_scoring
_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from calcul_scores import calculer_scores

def executer_calcul_direct(fichier_input, fichier_output="contrat_f2_output.json"):
    print(f"Chargement des données depuis : {fichier_input}")
    
    if not os.path.exists(fichier_input):
        print(f"[Erreur] Le fichier '{fichier_input}' est introuvable à la racine.")
        return

    try:
        # 1. Lecture du JSON pré-extrait
        with open(fichier_input, "r", encoding="utf-8") as f:
            data_extraite = json.load(f)
        
        # 2. Appel direct du moteur avec les clés du JSON
        # Utilise .get() avec des valeurs par défaut pour éviter les crashs si une clé manque
        contrat_f2 = calculer_scores(
            sub_scores=data_extraite.get("sub_scores", {}),
            anomalies=data_extraite.get("anomalies", []),
            blockers=data_extraite.get("blockers", []),
            secteur=data_extraite.get("secteur", data_extraite.get("secteur_applique", "agritech"))
        )
        
        # 3. Affichage du résultat dans la console
        print("\n================== OUTPUT CONTRAT F2 GENERE ==================")
        print(json.dumps(contrat_f2, ensure_ascii=False, indent=4))
        print("==============================================================")
        
        # 4. Sauvegarde dans un fichier d'output pour ton inspection ou tes assertions
        with open(fichier_output, "w", encoding="utf-8") as f_out:
            json.dump(contrat_f2, f_out, ensure_ascii=False, indent=4)
        print(f"\n[Succès] L'output a été sauvegardé dans '{fichier_output}'.")

    except json.JSONDecodeError:
        print("[Erreur] Le fichier fourni n'est pas un JSON valide.")
    except Exception as e:
        print(f"[Erreur lors du calcul] {e}")

if __name__ == "__main__":
    # Vu que 'output_scenario_complet.json' est dans le même dossier que ce script,
    # on utilise _ROOT_DIR pour construire un chemin absolu robuste.
    fichier_cible = os.path.join(_ROOT_DIR, "output_scenario_complet.json")
    fichier_destination = os.path.join(_ROOT_DIR, "contrat_f2_output.json")
    
    # Lancement du moteur de scoring
    executer_calcul_direct(fichier_cible, fichier_destination)