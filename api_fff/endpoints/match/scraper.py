import re
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from .html_parser import parse_match_html

BASE_URL = "https://epreuves.fff.fr"

def read_match_from_page(page, url_match):
    full_url = f"{BASE_URL}{url_match}"
    print(f"[match] Lecture de la feuille de match: {full_url}", flush=True)

    try:
        page.goto(full_url, wait_until="domcontentloaded", timeout=30000)
        
        # Extraction de l'ID du match depuis l'URL pour l'envoyer au parseur
        match_id_search = re.search(r'/match/(\d+)', url_match)
        match_id = match_id_search.group(1) if match_id_search else "inconnu"
        
        # On utilise votre parseur HTML existant qui fait déjà tout le travail de formatage
        # et on lui passe la page, l'URL complète et l'ID du match
        donnees_formatees = parse_match_html(page, full_url, match_id)

        return donnees_formatees

    except PlaywrightTimeoutError:
        print(f"[match] ❌ Timeout lors du chargement de la page : {full_url}")
        return {}
    except Exception as e:
        print(f"[match] ❌ Erreur lors de l'extraction : {e}")
        return {}