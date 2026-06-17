import json

def extract_sub_scores(payload):
    data = json.loads(payload) if isinstance(payload, str) else payload
    reponses = data.get("reponses_questionnaire", {})
    
    # Échelle de conversion brute de l'index (0-4) vers la note sur 100
    scale = [20, 40, 60, 80, 100]
    
    return {
        # Market & Traction (MKT)
        "MS1": scale[reponses["potentiel_financier_marche"]["index"]] if "potentiel_financier_marche" in reponses else 60,
        "MS2": scale[reponses["intensite_concurrence"]["index"]] if "intensite_concurrence" in reponses else 60,
        "MS3": scale[reponses["niveau_traction"]["index"]] if "niveau_traction" in reponses else 60,
        "MS4": scale[reponses["modele_revenu"]["index"]] if "modele_revenu" in reponses else 60,
        
        # Offre Commerciale (COM)
        "CO1": scale[reponses["business_plan_maturite"]["index"]] if "business_plan_maturite" in reponses else 60,
        "CO2": scale[reponses["maturite_produit"]["index"]] if "maturite_produit" in reponses else 60,
        "CO3": scale[reponses["strategie_prix"]["index"]] if "strategie_prix" in reponses else 60,
        "CO4": scale[reponses["alignement_besoins"]["index"]] if "alignement_besoins" in reponses else 60,
        
        # Innovation & Différenciation (INO)
        "IN1": scale[reponses["nouveaute_locale"]["index"]] if "nouveaute_locale" in reponses else 60,
        "IN2": scale[reponses["intensite_tech"]["index"]] if "intensite_tech" in reponses else 60,
        "IN3": scale[reponses["barrieres_entree"]["index"]] if "barrieres_entree" in reponses else 60,
        "IN4": scale[reponses["degre_rupture"]["index"]] if "degre_rupture" in reponses else 60,
        
        # Scalabilité & Croissance (SCA)
        "SC1": scale[reponses["replicabilite"]["index"]] if "replicabilite" in reponses else 60,
        "SC2": scale[reponses["independance_manuelle"]["index"]] if "independance_manuelle" in reponses else 60,
        "SC3": scale[reponses["couts_deploiement"]["index"]] if "couts_deploiement" in reponses else 60,
        "SC4": scale[reponses["potentiel_geo"]["index"]] if "potentiel_geo" in reponses else 60,
        
        # Impact & Environnement (ESG)
        "GS1": scale[reponses["climat_air"]["index"]] if "climat_air" in reponses else 60,
        "GS2": scale[reponses["donnees_eau_fournies"]["index"]] if "donnees_eau_fournies" in reponses else 60,
        "GS3": scale[reponses["sols_biodiversite"]["index"]] if "sols_biodiversite" in reponses else 60,
        "GS4": scale[reponses["ressources_dechets"]["index"]] if "ressources_dechets" in reponses else 60,
    }