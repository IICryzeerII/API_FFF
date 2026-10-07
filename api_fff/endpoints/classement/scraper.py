import re
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

BASE_URL = "https://epreuves.fff.fr"

def read_classement_from_page(page, club_id, club_name, equipe_id):
    url = f"{BASE_URL}/competition/club/{club_id}-{club_name}/equipe/{equipe_id}/classement"
    print(f"[classement] Lecture de la page: {url}", flush=True)
    
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        # On attend que le tableau du classement soit chargé dans le DOM
        page.locator('tr[role="row"], tr.cdk-row').first.wait_for(state="attached", timeout=5000)
    except PlaywrightTimeoutError:
        print("[classement] Aucun classement trouvé dans le délai imparti", flush=True)
        return {"items": [], "totalItems": 0}

    classement_items = []
    
    # On parcourt chaque ligne (tr) du tableau de classement
    lignes = page.locator('tr[role="row"], tr.cdk-row').all()
    
    for ligne in lignes:
        cellules = ligne.locator('td').all()
        # Une ligne de classement valide contient au moins les colonnes de stats
        if len(cellules) >= 12:
            try:
                # Extraction propre de chaque cellule selon l'ordre des colonnes de l'image
                rang = cellules[0].inner_text().strip()
                # La progression (Pr.) peut être vide, on la gère proprement
                progression = cellules[1].inner_text().strip() if len(cellules) > 12 else ""
                
                # Nom de l'équipe et lien du club
                equipe_cell = cellules[2] if len(cellules) > 12 else cellules[1]
                nom_equipe = equipe_cell.inner_text().strip()
                
                # Récupération de l'URL du club/équipe si disponible
                lien_equipe = equipe_cell.locator('a').first
                url_equipe = lien_equipe.get_attribute("href") if lien_equipe.count() > 0 else None

                # Statistiques chiffrées
                points = cellules[3].inner_text().strip() if len(cellules) > 12 else cellules[2].inner_text().strip()
                joues = cellules[4].inner_text().strip() if len(cellules) > 12 else cellules[3].inner_text().strip()
                gagnes = cellules[5].inner_text().strip() if len(cellules) > 12 else cellules[4].inner_text().strip()
                nuls = cellules[6].inner_text().strip() if len(cellules) > 12 else cellules[5].inner_text().strip()
                perdus = cellules[7].inner_text().strip() if len(cellules) > 12 else cellules[6].inner_text().strip()
                forfaits = cellules[8].inner_text().strip() if len(cellules) > 12 else cellules[7].inner_text().strip()
                penalite = cellules[9].inner_text().strip() if len(cellules) > 12 else cellules[8].inner_text().strip()
                buts_pour = cellules[10].inner_text().strip() if len(cellules) > 12 else cellules[9].inner_text().strip()
                buts_contre = cellules[11].inner_text().strip() if len(cellules) > 12 else cellules[10].inner_text().strip()
                diff = cellules[12].inner_text().strip() if len(cellules) > 12 else cellules[11].inner_text().strip()

                classement_items.append({
                    "rang": rang,
                    "progression": progression,
                    "equipe": nom_equipe,
                    "url_equipe": url_equipe,
                    "points": int(points) if points.isdigit() else points,
                    "joues": int(joues) if joues.isdigit() else joues,
                    "gagnes": int(gagnes) if gagnes.isdigit() else gagnes,
                    "nuls": int(nuls) if nuls.isdigit() else nuls,
                    "perdus": int(perdus) if perdus.isdigit() else perdus,
                    "forfaits": int(forfaits) if forfaits.isdigit() else forfaits,
                    "penalite": int(penalite) if penalite.isdigit() else penalite,
                    "buts_pour": int(buts_pour) if buts_pour.isdigit() else buts_pour,
                    "buts_contre": int(buts_contre) if buts_contre.isdigit() else buts_contre,
                    "diff": int(diff) if (diff.isdigit() or (diff.startswith('-') and diff[1:].isdigit())) else diff,
                })
            except Exception as e:
                # Ignore les lignes d'en-tête ou mal formées
                continue

    print(f"[classement] {len(classement_items)} équipes extraites du classement", flush=True)
    return {"items": classement_items, "totalItems": len(classement_items)}