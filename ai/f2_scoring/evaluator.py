# f2_scoring/evaluator.py
"""
Module d'encapsulation de l'évaluation d'un profil entrepreneur.
"""

from __future__ import annotations
import os
import sys

# Résolution des chemins
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_PARENT_DIR = os.path.dirname(_THIS_DIR)
if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)

from f2_scoring.calcul_scores import calculer_scores

def evaluer_profil_complet(profile: dict) -> dict:
    """
    Fonction unique d'encapsulation.
    Prend un profil en entrée (dictionnaire avec sub_scores, anomalies, blockers, secteur)
    et appelle calculer_scores pour retourner le contrat F2 au format JSON.
    """
    sub_scores = profile.get("sub_scores", {})
    anomalies = profile.get("anomalies", [])
    blockers = profile.get("blockers", [])
    secteur = profile.get("secteur", "")
    
    return calculer_scores(
        sub_scores=sub_scores,
        anomalies=anomalies,
        blockers=blockers,
        secteur=secteur
    )
