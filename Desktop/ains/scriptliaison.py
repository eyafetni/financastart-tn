"""
scriptliaison.py
================
Reçoit : contrat_f2_output.json  (JSON fusionné F1+F2)
Produit : output_f3_ENT-DBD323.json  (ressources + roadmap + perception gap)

Usage:
    python scriptliaison.py
    python scriptliaison.py mon_fichier.json
"""

import json
import sys
import os
from bridgef1f2f3 import pipeline_complet

# ── 1. Détecter le fichier input ─────────────────────────────────
if len(sys.argv) > 1:
    fichier_input = sys.argv[1]
else:
    # Chercher automatiquement dans le dossier courant
    fichier_input = None
    for f in os.listdir("."):
        if "contrat_f2" in f and f.endswith(".json"):
            fichier_input = f
            break
    if not fichier_input:
        print("❌ Fichier contrat_f2_output.json non trouvé.")
        print("   Usage: python scriptliaison.py contrat_f2_output.json")
        sys.exit(1)

print(f"Input : {fichier_input}")

# ── 2. Lancer le pipeline ─────────────────────────────────────────
output = pipeline_complet(fichier_input)

# ── 3. Sauvegarder le JSON output ────────────────────────────────
nom_fichier_output = f"output_f3_{output['entrepreneur_id']}.json"
with open(nom_fichier_output, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# ── 4. Affichage terminal ─────────────────────────────────────────
print("=" * 65)
print("OUTPUT F3 — RÉSUMÉ")
print("=" * 65)

# Identité
print(f"\n  Entrepreneur : {output['nom_entreprise']} ({output['entrepreneur_id']})")
print(f"  Localisation : {output['localisation']}")
print(f"  Secteur      : {output['secteur_label']}")

# Perception gap
print(f"\n{'─'*65}")
print(f"  PERCEPTION GAP")
print(f"  Stade perçu  : {output['stade_percu']}")
print(f"  Stade réel   : {output['stade_reel']}")
print(f"  Divergence   : {'✅ OUI' if output['divergence_detectee'] else '❌ NON'}")
print(f"  Message      : {output['message_perception_gap'][:120]}")
if output["signaux_divergence"]:
    print(f"  Signaux:")
    for s in output["signaux_divergence"]:
        print(f"    → {s}")

# Scores F2
print(f"\n{'─'*65}")
print(f"  SCORES F2   (FRI: {output['fri']}/100 — Bancable: {'✅' if output['is_financeable'] else '❌ NON'})")
for k, v in output["scores_f2"].items():
    bar  = "█" * (int(v) // 10) + "░" * (10 - int(v) // 10)
    flag = " ⚠️" if v < 65 else " ✅"
    print(f"    {k:<20} {int(v):>3}% {bar}{flag}")
print(f"  Scores faibles : {output['scores_faibles']}")

# Anomalies
if output["anomalies_f2"]:
    print(f"\n{'─'*65}")
    print(f"  ANOMALIES F2 ({len(output['anomalies_f2'])})")
    for a in output["anomalies_f2"]:
        if a.get("action_template"):
            print(f"  🚨 {a['action_template']}")

# Ressources
print(f"\n{'─'*65}")
print(f"  RESSOURCES RAG — {output['nombre_ressources']} ressources")
print(f"  ({output['secteur_rag']} | {output['stade_reel']})\n")
for r in output["ressources_recommandees"]:
    print(f"  ✅ [{r['id']}] {r['nom']}")
    print(f"     Organisme  : {r['organisme']}")
    print(f"     Pertinence : {r['pertinence']}%")
    print(f"     Taux       : {r['taux'] or 'Voir site officiel'}")
    print(f"     URL        : {r['url_source']}")
    if r.get("gaps_matches"):
        print(f"     Gaps       : {r['gaps_matches']}")
    print(f"     Pourquoi   : {r['justification']}")
    print()

# Roadmap
print(f"{'─'*65}")
rm = output["roadmap"]
print(f"  ROADMAP — {rm['secteur']} | {rm['stade']} | FRI: {rm['fri']}/100\n")
print(f"  📍 0-30 jours (URGENT):")
for a in rm["immediat_0_30j"]:
    print(f"    → {a}")
print(f"\n  📍 1-3 mois:")
for a in rm["court_terme_1_3m"]:
    print(f"    → {a}")
print(f"\n  📍 3-12 mois:")
for a in rm["moyen_terme_3_12m"]:
    print(f"    → {a}")

# Sources
print(f"\n{'─'*65}")
print(f"  SOURCES TRACÉES ({len(output['sources_tracees'])})")
for url in output["sources_tracees"]:
    print(f"    🔗 {url}")

print(f"\n{'='*65}")
print(f"✅ Output sauvegardé : {nom_fichier_output}")
print(f"✅ Ressources trouvées : {output['nombre_ressources']}")
print(f"✅ Divergence détectée : {output['divergence_detectee']}")
