def extract_blockers(blockers_list):
    """Normalise et mappe la liste des blockers brute."""
    blockers_mappes = []
    
    # Correction ici : blockers_list est déjà une liste, on boucle directement dessus
    for blk in blockers_list:
        blockers_mappes.append({
            "domaine": blk.get("domaine", "").capitalize(),
            "description": blk.get("description", ""),
            "niveau": "rouge" if blk.get("priorite", 1) == 1 else "orange"
        })
    return blockers_mappes