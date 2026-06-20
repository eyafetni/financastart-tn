import json 

def extract_sub_scores(payload):
    data = json.loads(payload) if isinstance(payload, str) else payload
    # Correction : "reponses" au lieu de "reponses_questionnaire"
    reponses = data.get("reponses", {})
    
    scale = [10, 40, 60, 75,90 ]
    
    # Helper pour éviter les répétitions et gérer les erreurs de clés
    def get_score(key):
        if key in reponses and "index" in reponses[key]:
            return scale[reponses[key]["index"]]
        return 60 # Valeur par défaut
    return {
        "MS1": get_score("potentiel_financier_marche"),
        "MS2": get_score("intensite_concurrence"),
        "MS3": get_score("niveau_traction"),
        "MS4": get_score("modele_revenu"),
        
        # Correction : business_plan_f2 au lieu de business_plan_maturite
        "CO1": get_score("business_plan_f2"), 
        "CO2": get_score("maturite_produit"),
        "CO3": get_score("strategie_prix"),
        "CO4": get_score("alignement_besoins"),
        
        "IN1": get_score("nouveaute_locale"),
        "IN2": get_score("intensite_tech"),
        "IN3": get_score("barrieres_entree"),
        "IN4": get_score("degre_rupture"),
        
        "SC1": get_score("replicabilite"),
        "SC2": get_score("independance_manuelle"),
        "SC3": get_score("couts_deploiement"),
        "SC4": get_score("potentiel_geo"),
        
        "GS1": get_score("climat_air"),
        "GS2": get_score("donnees_eau_fournies"),
        "GS3": get_score("sols_biodiversite"),
        "GS4": get_score("ressources_dechets"),
    }