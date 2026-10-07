import os
import json

def formater_nom_joueur(nom_complet):
    """Transforme 'LOUIS M.' ou 'Louis MASON' en 'Louis M.'"""
    parts = nom_complet.strip().split()
    if len(parts) > 1:
        prenom = parts[0].capitalize()
        initiale_nom = parts[-1][0].upper()
        return f"{prenom} {initiale_nom}."
    return nom_complet.capitalize()

def generer_statistiques_joueurs(nom_equipe: str, matchs_data: dict, nom_club_cible: str = "PARMAIN"):
    fichier_stats = f"stats_joueurs_{nom_equipe}.json"
    
    total_buts_reels = 0
    joueurs_extraits = set()
    
    # 1. Extraction des joueurs depuis les matchs joués
    for match in matchs_data.get("items", []):
        texte_match = str(match.get("texte", "")).lower()
        if "forfait" in texte_match:
            continue

        if match.get("statut") == "joué" or (match.get("score_a") is not None and match.get("score_b") is not None):
            nom_a = match.get("nom_equipe_a", "")
            nom_b = match.get("nom_equipe_b", "")
            
            buts_a = match.get("score_a")
            buts_b = match.get("score_b")
            
            try:
                buts_a = int(buts_a) if buts_a is not None else 0
                buts_b = int(buts_b) if buts_b is not None else 0
            except ValueError:
                buts_a, buts_b = 0, 0

            joueurs_de_notre_equipe = []
            if nom_club_cible.lower() in nom_a.lower():
                total_buts_reels += buts_a
                joueurs_de_notre_equipe = match.get("joueurs_a", [])
            elif nom_club_cible.lower() in nom_b.lower():
                total_buts_reels += buts_b
                joueurs_de_notre_equipe = match.get("joueurs_b", [])
            
            for joueur in joueurs_de_notre_equipe:
                nom_brut = joueur.get("nom", "Anonyme")
                if "Anonyme" not in nom_brut:
                    joueurs_extraits.add(formater_nom_joueur(nom_brut))

    # 2. Récupération des stats déjà gérées par l'admin
    stats_existantes = {}
    if os.path.exists(fichier_stats):
        with open(fichier_stats, "r", encoding="utf-8") as f:
            try:
                data_admin = json.load(f)
                for j in data_admin.get("joueurs", []):
                    stats_existantes[j["nom"]] = j
            except Exception:
                pass 

    # 3. Fusion intelligente : Union des joueurs du scraper ET des joueurs déjà enregistrés
    tous_les_noms = joueurs_extraits.union(stats_existantes.keys())

    joueurs_finaux = []
    total_buts_admin = 0
    total_passes_admin = 0
    
    for nom in sorted(tous_les_noms):
        if nom in stats_existantes:
            joueur = stats_existantes[nom] # On conserve scrupuleusement les buts/passes de l'admin
        else:
            joueur = {"nom": nom, "buts": 0, "passes_d": 0} # Nouveau joueur détecté
            
        joueurs_finaux.append(joueur)
        total_buts_admin += int(joueur.get("buts", 0))
        total_passes_admin += int(joueur.get("passes_d", 0))
        
    # Contrôle d'intégrité (Vérification des ratios)
    alerte_incoherence = (total_buts_admin != total_buts_reels) or (total_passes_admin != total_buts_reels)
    
    json_final = {
        "controle_integrite": {
            "total_buts_reels": total_buts_reels,
            "total_buts_admin": total_buts_admin,
            "total_passes_admin": total_passes_admin,
            "alerte_incoherence": alerte_incoherence,
            "message": "ATTENTION : Le tableau des buteurs/passeurs n'est pas à jour par rapport aux scores réels !" if alerte_incoherence else "Tableau à jour."
        },
        "joueurs": joueurs_finaux
    }
    
    return json_final