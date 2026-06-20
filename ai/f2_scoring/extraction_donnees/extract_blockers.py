def extract_blockers(profil_data):
    # Récupère la liste brute des blockers depuis le JSON
    blockers_bruts = profil_data.get("blockers", [])
    blockers_nettoyes = []
    
    # Dictionnaire de correspondance pour associer la priorité à la couleur du niveau
    mapping_niveaux = {
        "1": "rouge",
        "2": "orange",
        "3": "jaune"
    }
    
    for blk in blockers_bruts:
        # CAS 1 : Le blocker est un dictionnaire complet
        if isinstance(blk, dict):
            # ON CHERCHE "priorite" ICI (valeur par défaut "2" si absente)
            priorite_brute = str(blk.get("priorite", "2")).strip()
            
            blockers_nettoyes.append({
                "domaine": blk.get("domaine", "Général").capitalize(),
                "description": blk.get("description", ""),
                # On transforme la priorité en couleur sous la clé "niveau"
                "niveau": mapping_niveaux.get(priorite_brute, "orange")
            })
        
        # CAS 2 : Le blocker est juste une chaîne de texte brute
        elif isinstance(blk, str):
            blockers_nettoyes.append({
                "domaine": "Général",
                "description": blk,
                "niveau": "orange"  # Niveau par défaut
            })
            
    return blockers_nettoyes