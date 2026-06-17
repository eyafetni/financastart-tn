"""
Script de test simple pour executer calculer_scores() sur les 10 profils
du jeu de donnees et afficher les sorties principales.
"""

from __future__ import annotations

import json
import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_THIS_DIR)
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

from f2_scoring.calcul_scores import calculer_scores
from f2_scoring.test_data import PROFILS_TEST_10


def _format_scores(resultat: dict) -> dict[str, float]:
    return {nom: bloc["valeur"] for nom, bloc in resultat["scores"].items()}


def main() -> None:
    for profil in PROFILS_TEST_10:
        resultat = calculer_scores(
            sub_scores=profil["sub_scores"],
            anomalies=profil["anomalies"],
            blockers=profil["blockers"],
            secteur=profil["secteur"],
        )

        print("=" * 80)
        print(f"{profil['id']} - {profil['nom_scenario']}")
        print(f"Secteur applique : {resultat['secteur_applique']}")
        print(
            f"FRI : {resultat['financing_readiness_index']} | "
            f"Financeable : {resultat['is_financeable']}"
        )
        print(f"Interpretation : {resultat['fri_interpretation']}")
        print(f"Scores : {json.dumps(_format_scores(resultat), ensure_ascii=False, indent=2)}")
        print(f"Anomalies detectees : {json.dumps(resultat['anomalies_detectees'], ensure_ascii=False, indent=2)}")
        print(f"Blockers actifs : {json.dumps(resultat['blockers_actifs'], ensure_ascii=False, indent=2)}")
        print(f"Resume executif : {resultat['resume_executif']}")
        print()


if __name__ == "__main__":
    main()