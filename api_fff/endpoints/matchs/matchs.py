import re
import datetime

BASE_URL = "https://epreuves.fff.fr"

def extraire_date_pour_tri(texte):
    """Extrait une date d'une chaîne pour permettre un tri chronologique fiable."""
    mois_map = {
        "JAN": 1, "FEV": 2, "FÉV": 2, "MAR": 3, "AVR": 4, "MAI": 5, "JUN": 6, 
        "JUI": 7, "JUL": 7, "AOU": 8, "AOÛ": 8, "SEP": 9, "OCT": 10, "NOV": 11, 
        "DEC": 12, "DÉC": 12
    }
    
    match = re.search(r"(\d{1,2})\s+([A-ZÉÛ]+)\s+(\d{4})", texte.upper())
    if match:
        jour = int(match.group(1))
        mois_txt = match.group(2)[:3]
        annee = int(match.group(3))
        mois = mois_map.get(mois_txt, 1)
        return datetime.datetime(annee, mois, jour)
    
    return datetime.datetime(2099, 12, 31)

def read_matchs_from_page(page, club_id, club_name, equipe_id):
    url = f"{BASE_URL}/competition/club/{club_id}-{club_name}/equipe/{equipe_id}/saison"
    print(f"[matchs] Lecture de la page saison: {url}", flush=True)

    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    print("[matchs] Descente approfondie (Recherche de tous les blocs)...", flush=True)

    essais_sans_nouveaux = 0
    nb_blocs_precedents = 0
    max_essais = 6  # On augmente légèrement la persistance pour être sûr de tout charger
    
    # --- PHASE 1 : SCROLL ROBUSTE JUSQU'EN BAS ---
    while essais_sans_nouveaux < max_essais:
        # Forcer un scroll fluide vers le bas de la fenêtre
        page.evaluate("window.scrollBy(0, 1000);")
        page.wait_for_timeout(1000) # Laisser le temps au réseau d'injecter les blocs
        
        nb_blocs_actuels = page.locator('app-match-score').count()
        
        if nb_blocs_actuels > nb_blocs_precedents:
            essais_sans_nouveaux = 0
            nb_blocs_precedents = nb_blocs_actuels
            # Scroller le dernier élément visible pour déclencher l'affichage du suivant
            try:
                page.locator('app-match-score').nth(nb_blocs_actuels - 1).scroll_into_view_if_needed()
            except:
                pass
        else:
            essais_sans_nouveaux += 1
            # Secousse supplémentaire pour débloquer les lazy-loads récalcitrants
            page.keyboard.press("PageDown")

    print("[matchs] Fin du calendrier atteinte. Extraction, dédoublonnage et tri...", flush=True)

    # --- PHASE 2 : EXTRACTION & DÉDOUBLONNAGE ---
    matchs_uniques = {}
    
    for bloc in page.locator('app-match-score').all():
        html_interne = bloc.inner_html().upper()
        
        if "EXEMPT" in html_interne:
            continue

        lien = bloc.locator('a[href*="/competition/match/"]').first
        if lien.count():
            lien_url = lien.get_attribute("href")
            if lien_url:
                lien_url = re.sub(r"\s+", "", lien_url)
                texte_brut = " ".join(bloc.inner_text().split())
                
                if lien_url not in matchs_uniques:
                    matchs_uniques[lien_url] = {
                        "url": lien_url,
                        "texte": texte_brut,
                        "_date_tri": extraire_date_pour_tri(texte_brut)
                    }

    # --- PHASE 3 : TRI CHRONOLOGIQUE STRICT ---
    matchs_bruts = list(matchs_uniques.values())
    matchs_bruts.sort(key=lambda x: x["_date_tri"])

    matchs_propres = []
    for m in matchs_bruts:
        matchs_propres.append({
            "url": m["url"],
            "texte": m["texte"]
        })

    print(f"[matchs] ✅ {len(matchs_propres)} matchs uniques extraits et triés chronologiquement.", flush=True)

    return {"items": matchs_propres, "totalItems": len(matchs_propres)}