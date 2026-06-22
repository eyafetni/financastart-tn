# run_backend_test.py
import os
import json
import traceback

# On importe la fonction pure depuis ton module fonction_principale
from fonction_principale import process_entrepreneur_profile

def exécuter_test_local():
    print("🚀 BASE DE TEST BACKEND — FEATURE 2")
    
    # 1. Détermination dynamique des chemins absolus basés sur l'emplacement de ce script
    _THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    
    fichier_input = os.path.join(_THIS_DIR, "test_partie_1.json")
    fichier_output = os.path.join(_THIS_DIR, "contrat_f2_output.json")
    
    print(f"📂 Lecture du fichier de test : {fichier_input}")
    if not os.path.exists(fichier_input):
        print(f"❌ Erreur : Le fichier '{fichier_input}' est introuvable.")
        print("Vérifiez que 'test_partie_1.json' est bien dans le même dossier que ce script.")
        return

    # 2. Chargement du JSON d'entrée
    with open(fichier_input, "r", encoding="utf-8") as f:
        try:
            profil_brut = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ Erreur de décodage JSON sur le fichier d'entrée : {e}")
            return

    # 3. Appel de la fonction de ton pipeline
    print("⚙️  Passage des données dans 'process_entrepreneur_profile'...")
    try:
        contrat_final = process_entrepreneur_profile(profil_brut)
        print("🟢 Pipeline exécuté avec succès (aucune exception levée).")
    except Exception as e:
        print(f"❌ Le pipeline a crashé pendant l'exécution : {e}")
        traceback.print_exc()
        return

    # 4. Sauvegarde du résultat final dans le fichier de sortie
    print(f"💾 Écriture du contrat F2 dans : {fichier_output}")
    try:
        with open(fichier_output, "w", encoding="utf-8") as f_out:
            json.dump(contrat_final, f_out, indent=4, ensure_ascii=False)
        print("✨ Fichier output généré proprement.")
    except Exception as e:
        print(f"❌ Impossible d'écrire le fichier de sortie : {e}")
        return

    # 5. Assertions et vérifications visuelles rapides dans la console
    print("\n📊 --- VÉRIFICATION DES RÉSULTATS ---")
    print(f"• Secteur appliqué : {contrat_final.get('secteur_applique')}")
    print(f"• Score FRI Global : {contrat_final.get('financing_readiness_index')}/100")
    print(f"• Éligible (is_financeable) : {contrat_final.get('is_financeable')}")
    
    anomalies = contrat_final.get("anomalies_detectees", [])
    print(f"• Nombre d'anomalies : {len(anomalies)}")
    if anomalies:
        print("🔍 Top anomalie (Vérification de la clé 'justification') :")
        top_anom = anomalies[0]
        print(f"  - ID : {top_anom.get('id')}")
        print(f"  - Justification : {top_anom.get('justification', '')[:90]}...")
        if "description" in top_anom:
            print("  ⚠️ Attention : l'ancienne clé 'description' est encore présente !")
        else:
            print("  ✅ Clé 'description' supprimée et mappée avec succès.")

if __name__ == "__main__":
    exécuter_test_local()