import json
from datetime import datetime

STADES = {
    1: {"nom": "Ideation", "description": "Idée sans validation ni équipe complète", "financement": "Love money / Concours"},
    2: {"nom": "Market Validation", "description": "Premiers clients / traction naissante", "financement": "Microfinance / BTS"},
    3: {"nom": "Structuration", "description": "Structure juridique / business plan", "financement": "APII / ANPE"},
    4: {"nom": "Fundraising", "description": "Dossier bancable en construction", "financement": "BFPME / Startup Act"},
    5: {"nom": "Launch Planning", "description": "Produit validé / prêt à lever", "financement": "Capital risque / ANAVA"},
    6: {"nom": "Growth", "description": "Revenus existants / expansion", "financement": "Lignes bancaires / AFD / EU"},
}


SECTEURS = {
    "agriculture_sylviculture_peche": {
        "label": "Agriculture / Sylviculture / Pêche",
        "mots_cles": [
            "agri", "agro", "agricol", "agroaliment", "food", "sylvicult","sylvi",
            "forêt","foret", "peche", "pêche", "élevage", "elevage",
            "cultures", "céréales", "cereales", "maraich", "arboricult","aqua",
            "aquaculture", "halieutique" , "argi-tech", "agri-tech", "agritech", "foodtech"
        ]
    },
    "industrie_construction": {
        "label": "Industrie / Construction",
        "mots_cles": [
            "indus", "industrie", "manufactur", "usine", "fabricat", "product","prod",
            "construct", "bâtiment", "batiment","trav", "travaux", "btp","immo",
            "immobilier", "génie civil", "genie civil", "matériaux", "materiaux",
            "mécanique", "mecanique", "metal","metallurgi", "chimie","chimique","textil",
            "plasturgi", "automobile", "aéronautique", "aeronautique", "énergie", "energie",
        ]
    },
    "commerce_transport_logistique": {
        "label": "Commerce / Transport / Logistique",
        "mots_cles": [
            "commerce", "vente", "retail", "boutique", "distribut","logistique",
            "transport", "livraison", "fret", "import","export","supply chain", "supply", "chain",
            "entrepôt", "entrepot", "transit","grossiste","detail","gros", "détaillant",
            "detaillant","e-commerce", "ecommerce", "marketplace", "transport",
            "mobilité", "mobilite", "last mile", "last-mile"
        ]
    },
    "service_tourisme": {
        "label": "Service / Tourisme",
        "mots_cles": [
            "service", "conseil", "formation", "consulting", "tourisme",
            "hôtel", "hotel", "restaurant", "café", "cafe", "restaurat",
            "hébergement", "hebergement", "voyage", "agence de voyage",
            "bien-être", "bien être", "santé", "sante", "éducation", "education",
            "immobilier service", "nettoyage", "maintenance",
        ]
    },
    "tech_services_entreprise": {
        "label": "Technologie et Services Entreprise",
        "mots_cles": [
            "tech", "digital", "logiciel", "app", "web", "ia", "ai", "saas",
            "software", "développement", "developpement", "informatique",
            "cyber","cybersecurité", "cybersécurité", "cloud", "data", "fintech",
            "edtech", "healthtech", "b2b", "erp", "crm", "automatisation",
            "robotique", "iot", "blockchain", "marketplace","platform", "plateforme"
        ]
    },
}

def detecter_secteur(desc_lower):
    scores = {}
    for cle, info in SECTEURS.items():
        score = sum(1 for mot in info["mots_cles"] if mot in desc_lower)
        if score > 0:
            scores[cle] = score

    if scores:
        return max(scores, key=scores.get)
    return None


def charger_input(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    nom_entreprise = data.get("nom_entreprise", "Non précisé")
    description_libre = data.get("description_libre", "")
    return nom_entreprise, description_libre


def run_diagnostic(input_filepath):
    profil = {}

    nom_entreprise, description_libre = charger_input(input_filepath)
    profil["nom_entreprise"] = nom_entreprise
    profil["description_libre"] = description_libre
    desc_lower = description_libre.lower()

    secteur_cle_detecte = detecter_secteur(desc_lower)
    profil["secteur"] = secteur_cle_detecte if secteur_cle_detecte else ""

    REGIONS = ["Bizerte", "Tunis", "Ariana", "Ben Arous", "Manouba", "Nabeul", "Sfax", "Zaghouan", "Beja", "Jendouba", "Siliana", "Kasserine", "Kef", "Kaireon", "Sousse", "Monastir", "Mahdia", "Sidi Bouzid", "Tozeur", "Kebili", "Gabes", "Gafsa", "Medenine", "Tataouine"]
    localisation_detectee = ""
    for region in REGIONS:
        if region.lower() in desc_lower:
            localisation_detectee = region
            break
    profil["localisation"] = localisation_detectee

    STADES_NOMS = [s["nom"] for s in STADES.values()]
    stade_percu_detecte = ""
    for nom in STADES_NOMS:
        if nom.lower() in desc_lower:
            stade_percu_detecte = nom
            break
    profil["stade_percu"] = stade_percu_detecte

    output = {
        "nom_entreprise": profil["nom_entreprise"],
        "stade_percu": profil["stade_percu"],
        "secteur": profil["secteur"],
        "localisation": profil["localisation"],
    }

    filename = f"diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    return output


if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.json"
    result = run_diagnostic(input_file)
