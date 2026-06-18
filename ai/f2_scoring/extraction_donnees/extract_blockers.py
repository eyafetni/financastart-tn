def extract_blockers(profil_data):
    # Récupère la liste brute des blockers depuis le JSON
    blockers_bruts = profil_data.get("blockers", [])
    blockers_nettoyes = []
    
    for blk in blockers_bruts:
        # CAS 1 : Le blocker est un dictionnaire complet (ex: {"domaine": "Légal", "description": "..."})
        if isinstance(blk, dict):
            blockers_nettoyes.append({
                "domaine": blk.get("domaine", "Général").capitalize(),
                "description": blk.get("description", ""),
                "niveau": blk.get("niveau", "orange")
            })
        
        # CAS 2 : Le blocker est juste une chaîne de texte brute (ton cas actuel dans test_partie_1)
        elif isinstance(blk, str):
            blockers_nettoyes.append({
                "domaine": "Général",  # Valeur par défaut
                "description": blk,    # Le texte de la chaîne devient la description
                "niveau": "orange"     # Niveau par défaut
            })
            
    return blockers_nettoyes