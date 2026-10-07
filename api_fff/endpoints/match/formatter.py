import re
import datetime

def convertir_date_fr(date_str):
    """Convertit 'DIM 18 OCT 2026 - 15H30' en format datetime ISO."""
    if not date_str:
        return None
        
    mois_map = {
        "JAN": 1, "FEV": 2, "FÉV": 2, "MAR": 3, "AVR": 4, "MAI": 5, "JUN": 6, 
        "JUI": 7, "JUL": 7, "AOU": 8, "AOÛ": 8, "SEP": 9, "OCT": 10, "NOV": 11, 
        "DEC": 12, "DÉC": 12
    }
    
    match = re.search(r"(\d{1,2})\s+([A-ZÉÛ]+)\s+(\d{4})\s*-\s*(\d{1,2})H(\d{2})", date_str.upper())
    
    if match:
        jour = int(match.group(1))
        mois_txt = match.group(2)[:3]
        annee = int(match.group(3))
        heure = int(match.group(4))
        minute = int(match.group(5))
        
        mois = mois_map.get(mois_txt, 1)
        dt = datetime.datetime(annee, mois, jour, heure, minute)
        return dt.isoformat()
        
    return date_str

def extraire_infos_match_complet(match_data):
    """Extrait les données complètes d'un match (score, buts, événements, compositions)."""
    score_data = match_data.get("score") or {}
    domicile = match_data.get("domicile") or {}
    exterieur = match_data.get("exterieur") or {}
    
    def formater_joueurs(joueurs_bruts):
        liste = []
        for j in joueurs_bruts:
            liste.append({
                "nom": j.get("nom") or j.get("libelle"),
                "maillot": j.get("maillot") or j.get("numero"),
                "role": j.get("role", "titulaire"),
                "evenements": j.get("evenements", [])
            })
        return liste

    return {
        "nom_equipe_a": domicile.get("club"),
        "nom_equipe_b": exterieur.get("club"),
        "score_a": score_data.get("domicile") if score_data.get("domicile") is not None else domicile.get("buts"),
        "score_b": score_data.get("exterieur") if score_data.get("exterieur") is not None else exterieur.get("buts"),
        "logo_a": domicile.get("logo_url") or domicile.get("logo"),
        "logo_b": exterieur.get("logo_url") or exterieur.get("logo"),
        "statut": match_data.get("statut") or match_data.get("maStatutLib"),
        "lieu": match_data.get("stade") or match_data.get("lieu"),
        "lieu_lien_carte": match_data.get("stade_lien_carte"),
        "moments_forts": match_data.get("evenements", []),
        "joueurs_a": formater_joueurs(domicile.get("joueurs", [])),
        "joueurs_b": formater_joueurs(exterieur.get("joueurs", []))
    }

def extraire_infos_match_a_venir(match_data):
    """Extrait les données de planification pour un match non joué."""
    domicile = match_data.get("domicile") or {}
    exterieur = match_data.get("exterieur") or {}
    
    return {
        "nom_equipe_a": domicile.get("club"),
        "nom_equipe_b": exterieur.get("club"),
        "score_a": None,
        "score_b": None,
        "logo_a": domicile.get("logo_url") or domicile.get("logo"),
        "logo_b": exterieur.get("logo_url") or exterieur.get("logo"),
        "statut": match_data.get("statut"),
        "date": convertir_date_fr(match_data.get("date")),
        "lieu": match_data.get("stade"),
        "lieu_lien_carte": match_data.get("stade_lien_carte"),
        "joueurs_a": [],
        "joueurs_b": []
    }

def formater_donnees_match(match_data):
    """Détermine quelles informations renvoyer selon l'état du match."""
    statut = (match_data.get("statut") or "").lower()
    score_data = match_data.get("score") or {}
    joueurs_domicile = match_data.get("domicile", {}).get("joueurs", [])
    
    mots_cles_fin = ["joué", "arret", "arrêté", "reporté", "forfait", "annulé"]
    est_concerne = any(mot in statut for mot in mots_cles_fin) or (score_data.get("domicile") is not None) or (len(joueurs_domicile) > 0)
    
    if est_concerne:
        return extraire_infos_match_complet(match_data)
    else:
        return extraire_infos_match_a_venir(match_data)