import re
import urllib.parse
from .formatter import formater_donnees_match

def parse_match_html(page, page_url, match_id):
    """Extrait les données directement depuis le HTML (DOM)."""

    # --- 1. SCORE ET STATUT ---
    score_block = page.locator("app-match-score").first
    texte_complet = ""
    score_div_text = ""
    chiffres_score = []
    
    if score_block.count():
        texte_complet = score_block.inner_text().upper()
        
        digits = score_block.locator(".score .digit, .score-value").all_inner_texts()
        chiffres_score = [d.strip() for d in digits if d.strip().isdigit()]
        
        if len(chiffres_score) < 2:
            score_element = score_block.locator(".score").first
            if score_element.count():
                score_div_text = score_element.inner_text().strip().upper()
                score_clean = re.sub(r'\d{1,2}[:hH]\d{2}', '', score_div_text)
                trouvailles = re.findall(r'\b\d+\b', score_clean)
                if len(trouvailles) >= 2:
                    chiffres_score = trouvailles[:2]

    est_horaire = re.search(r'\d{1,2}[:hH]\d{2}', score_div_text) is not None or re.search(r'\d{1,2}[:hH]\d{2}', texte_complet) is not None
    joue = False
    statut = "à venir"

    if "ARRÊTÉ" in texte_complet or "ARRETE" in texte_complet:
        statut = "ARRÊTÉ"
        joue = True
    elif len(chiffres_score) >= 2:
        statut = "joué"
        joue = True
    elif est_horaire:
        statut = "à venir"

    # --- 2. ÉQUIPES ET LOGOS ---
    equipes_base = []
    logos_urls = []
    
    if score_block.count():
        for img in score_block.locator("img").all():
            src = img.get_attribute("src")
            if src and "instances" not in src:
                if src.startswith('/'):
                    src = f"https://epreuves.fff.fr{src}"
                if src not in logos_urls:
                    logos_urls.append(src)

        noms_equipes = score_block.locator(".equipe-name").all_inner_texts()
        for i in range(min(2, len(noms_equipes))):
            nom_club = " ".join(noms_equipes[i].split())
            logo_url = logos_urls[i] if i < len(logos_urls) else None
            equipes_base.append({"club": nom_club, "joueurs": [], "logo_url": logo_url})
            
    if not equipes_base:
        for entete in page.locator(".accordion-header .flex-row").all()[:2]:
             nom = " ".join(entete.locator("span.fw-bold").inner_text().split())
             if nom:
                equipes_base.append({"club": nom, "joueurs": [], "logo_url": None})
                
    if not equipes_base:
        equipes_base = [{"club": None, "joueurs": [], "logo_url": None}, {"club": None, "joueurs": [], "logo_url": None}]
    elif len(equipes_base) == 1:
        equipes_base.append({"club": None, "joueurs": [], "logo_url": None})

    domicile = equipes_base[0]
    exterieur = equipes_base[1]

    # --- 3. COMPOSITIONS DES ÉQUIPES ---
    blocs_equipes = page.locator("app-match-composition .team-container, app-match-compo .team, .compo-wrapper .team").all()
    if not blocs_equipes:
         blocs_equipes = page.locator(".compo-team").all()

    for i, bloc in enumerate(blocs_equipes[:2]):
        joueurs_liste = []
        tables = bloc.locator("table.players").all()
        if tables:
            for table in tables:
                role = "remplacant" if "sub" in (table.get_attribute("class") or "") else "titulaire"
                for ligne in table.locator("tr.player").all():
                    cellules = ligne.locator("td").all()
                    if len(cellules) >= 2:
                        maillot = " ".join(cellules[0].inner_text().split())
                        nom = " ".join(cellules[1].inner_text().split())
                        joueurs_liste.append({"nom": nom, "maillot": maillot, "role": role, "evenements": []})
        else:
             lignes_joueurs = bloc.locator(".player-row, mat-list-item, .d-flex.align-items-center").all()
             role_actuel = "titulaire"
             for ligne in lignes_joueurs:
                 texte_ligne = ligne.inner_text().strip()
                 if "REMPLAÇANTS" in texte_ligne.upper():
                     role_actuel = "remplacant"
                     continue
                 if "TITULAIRES" in texte_ligne.upper():
                     role_actuel = "titulaire"
                     continue
                 match_joueur = re.match(r"^(\d+)\s+(.+)$", texte_ligne)
                 if match_joueur:
                     joueurs_liste.append({
                         "nom": match_joueur.group(2).strip(), 
                         "maillot": match_joueur.group(1), 
                         "role": role_actuel, 
                         "evenements": []
                     })
                     
        if i == 0:
            domicile["joueurs"] = joueurs_liste
        elif i == 1:
            exterieur["joueurs"] = joueurs_liste

    # --- 4. ÉVÉNEMENTS GLOBAUX (MOMENTS FORTS) ---
    evenements = []
    lignes_timeline = page.locator("app-moment-fort.match").all()
    
    for ligne in lignes_timeline:
        minute_elem = ligne.locator(".timer").first
        minute = minute_elem.inner_text().strip() if minute_elem.count() else None
        
        action_div = ligne.locator(".action").first
        if action_div.count():
            texte_ligne = action_div.inner_text().replace('\n', ' ').strip()
            equipe_type = action_div.get_attribute("club-type")
            equipe_concernee = "domicile" if equipe_type == "recevant" else "exterieur"
            
            club_nom = domicile["club"] if equipe_concernee == "domicile" else exterieur["club"]
            type_evt = "autre"
            joueur = ""
            
            if "Changement" in texte_ligne:
                type_evt = "changement"
                changement_match = re.search(r'(.+)\s+remplace\s+(.+)', texte_ligne, re.IGNORECASE)
                if changement_match:
                    entrant_brut = changement_match.group(1).replace("Changement pour", "").replace(club_nom or "", "").strip()
                    sortant_brut = changement_match.group(2).strip()
                    joueur = f"Entrant: {entrant_brut}, Sortant: {sortant_brut}"
                    
            elif "Avertissement" in texte_ligne:
                type_evt = "carton_jaune"
                averti_match = re.search(r'(.+)\s+est averti', texte_ligne, re.IGNORECASE)
                if averti_match:
                    joueur = averti_match.group(1).replace("Avertissement pour", "").replace(club_nom or "", "").strip()
                    
            elif "Expulsion" in texte_ligne or "rouge" in texte_ligne.lower():
                type_evt = "carton_rouge"
                expulse_match = re.search(r'(.+)\s+est expulsé', texte_ligne, re.IGNORECASE)
                if expulse_match:
                     joueur = expulse_match.group(1).replace("Expulsion pour", "").replace("Carton rouge pour", "").replace(club_nom or "", "").strip()
                     
            elif "But" in texte_ligne or "goal" in texte_ligne.lower():
                type_evt = "but"
                joueur = texte_ligne.replace("But pour", "").replace("But de", "").replace(club_nom or "", "").replace("par", "").strip()

            evenements.append({
                "type": type_evt,
                "minute": minute,
                "joueur": joueur,
                "equipe": equipe_concernee,
                "description": texte_ligne
            })

    # --- 4.5. DISTRIBUTION DES ÉVÉNEMENTS AUX JOUEURS ---
    for equipe_data in [domicile, exterieur]:
        for j in equipe_data["joueurs"]:
            nom_j = j["nom"].strip().upper()
            if not nom_j:
                continue
                
            for evt in evenements:
                if not evt["minute"]: 
                    continue
                min_str = evt["minute"]
                evt_joueur_upper = evt["joueur"].upper()
                
                if evt["type"] == "changement":
                    if f"ENTRANT: {nom_j}" in evt_joueur_upper:
                        j["evenements"].append(f"Entrée ({min_str})")
                    elif f"SORTANT: {nom_j}" in evt_joueur_upper:
                        j["evenements"].append(f"Sortie ({min_str})")
                else:
                    if nom_j in evt_joueur_upper:
                        j["evenements"].append(f"{evt['type']} ({min_str})")

    # --- 5. EXTRACTION DE LA DATE ---
    date_match = None
    try:
        bandeau_date = page.locator(".date-time, .match-date, .top-bar-date, app-match-score .date").first
        if bandeau_date.count():
            date_match = bandeau_date.inner_text().strip()
        if not date_match and score_block.count():
            texte_score_date = score_block.inner_text()
            regex_date = re.search(r"([A-Z]{3}\s\d{1,2}\s[A-Z]{3,4}\s\d{4}\s*-\s*\d{1,2}H\d{2})", texte_score_date, re.IGNORECASE)
            if regex_date:
                date_match = regex_date.group(1).strip()
    except:
        pass

    # --- 6. EXTRACTION DU STADE ET DU LIEN DE CARTE (AVEC ENCODAGE URL PROPRE) ---
    stade_match = None
    stade_lien_carte = None
    try:
        titre_lieu = page.get_by_text("LIEU DE LA RENCONTRE").first
        if titre_lieu.count():
            bloc_parent = titre_lieu.locator("..").first
            lignes = [ligne.strip() for ligne in bloc_parent.inner_text().splitlines() if ligne.strip()]
            for idx, ligne in enumerate(lignes):
                if "LIEU DE LA RENCONTRE" in ligne.upper() and idx + 1 < len(lignes):
                    stade_match = lignes[idx + 1]
                    break
        if not stade_match:
            stade_fallback = page.locator("app-match-installation .fw-bold, .installation-name").first
            if stade_fallback.count():
                stade_match = stade_fallback.inner_text().strip()

        lieu_container = page.locator("app-resume, .lieu-match, .installations-container").first
        if lieu_container.count():
            lien_elem = lieu_container.locator("a[href*='address='], a[href*='maps']").first
            if lien_elem.count():
                raw_href = lien_elem.get_attribute("href")
                if raw_href:
                    # Sécurisation et encodage correct des espaces pour que le lien soit 100% cliquable
                    if "?" in raw_href:
                        base_url, query_str = raw_href.split("?", 1)
                        # On ré-encode proprement les paramètres pour éviter les espaces non gérés
                        parsed_params = urllib.parse.parse_qsl(query_str, keep_blank_values=True)
                        stade_lien_carte = f"{base_url}?" + urllib.parse.urlencode(parsed_params)
                    else:
                        stade_lien_carte = raw_href
    except:
        pass

    # --- 7. FORMATAGE FINAL ET INJECTION DES NOMS D'ÉQUIPES ---
    score_dict = None
    if len(chiffres_score) >= 2:
        score_dict = {
            "domicile": int(chiffres_score[0]),
            "exterieur": int(chiffres_score[1])
        }

    result = {
        "id": match_id,
        "url": page_url,
        "titre": page.title(),
        "statut": statut,
        "ma_statut_lib": statut,
        "joue": joue,
        "match_fait": joue,
        "date": date_match,
        "stade": stade_match,
        "stade_lien_carte": stade_lien_carte,
        "score": score_dict,
        "domicile": domicile,
        "exterieur": exterieur,
        "evenements": evenements,
        "buteurs": [e for e in evenements if e["type"] == "but"],
    }
    
    donnees_formatees = formater_donnees_match(result)
    
    print(f"[match] statut={statut} | Stade: {stade_match} | Lien carte encodé: {bool(stade_lien_carte)}", flush=True)
    return donnees_formatees