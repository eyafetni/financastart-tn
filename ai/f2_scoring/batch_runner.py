"""
Batch Runner — Pipeline Complète avec Source JSON
1. Charge les 10 profils depuis test_data.json
2. Extrait la structure propre (extract_all_scenario_data)
3. Chaîne le résultat comme entrée de l'évaluateur (evaluer_profil_complet)
4. Génère les 20 fichiers JSON correspondants dans output_jsons/
"""

import os
import sys
import json

# Résolution des chemins pour le bon fonctionnement des imports
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_THIS_DIR)
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

# Import de tes briques de pipeline réelles
from f2_scoring.extract_all_scenarios_data import extract_all_scenario_data
from f2_scoring.evaluator import evaluer_profil_complet

def run_all_tests():
    # 1. Chemins des répertoires et fichiers
    output_dir = os.path.join(_PARENT_DIR, "output_jsons")
    os.makedirs(output_dir, exist_ok=True)
    
    json_path = os.path.join(_THIS_DIR, "test_data.json")
    
    # 2. Chargement sécurisé du fichier test_data.json
    if not os.path.exists(json_path):
        print(f"[ERREUR] Le fichier de données est introuvable ici : {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        profils_test = json.load(f)

    print(f"[INFO] 🚀 Lancement de la pipeline sur {len(profils_test)} profils (Source JSON)...")
    
    # 3. Boucle d'exécution sur chaque profil
    for i, raw_profile in enumerate(profils_test, 1):
        prof_id = raw_profile.get("entrepreneur_id", f"ENT-{i:03d}")
        
        try:
            # -----------------------------------------------------------------
            # ÉTAPE 1 : Extraction & Normalisation Structurelle
            # -----------------------------------------------------------------
            payload_extrait = extract_all_scenario_data(raw_profile)
            final_id = payload_extrait.get("id", f"PROF-{i:03d}")
            
            # Sauvegarde de l'extraction brute
            extract_filename = f"contrat_f2_{final_id}_extracted.json"
            extract_filepath = os.path.join(output_dir, extract_filename)
            with open(extract_filepath, "w", encoding="utf-8") as f:
                json.dump(payload_extrait, f, ensure_ascii=False, indent=2)
                
            # -----------------------------------------------------------------
            # ÉTAPE 2 : Évaluation Métier (Chaînage d'Input direct)
            # -----------------------------------------------------------------
            payload_final = evaluer_profil_complet(payload_extrait)
            
            # Sauvegarde du rapport métier final
            final_filename = f"contrat_f2_{final_id}_final.json"
            final_filepath = os.path.join(output_dir, final_filename)
            with open(final_filepath, "w", encoding="utf-8") as f:
                json.dump(payload_final, f, ensure_ascii=False, indent=2)
                
            print(f"  -> [{final_id}] ✅ Pipeline franchie complète :")
            print(f"     📄 [1/2] Extrait : {extract_filename}")
            print(f"     🏆 [2/2] Évalué  : {final_filename}")
            
        except Exception as e:
            print(f"  ❌ [{prof_id}] Erreur critique dans la pipeline : {str(e)}")
            
    print(f"\n[INFO] 🎉 Exécution terminée. Les fichiers d'extraction et finaux sont dans : {output_dir}")

if __name__ == "__main__":
    run_all_tests()