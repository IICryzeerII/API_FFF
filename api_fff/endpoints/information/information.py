import json
from playwright.sync_api import Page, Error as PlaywrightError

BASE_URL = "https://epreuves.fff.fr"

def read_information_from_page(page: Page, club_id: str, club_name: str):
    url = f"{BASE_URL}/competition/club/{club_id}-{club_name}/informations"
    print(f"[information] Lecture de la page: {url}", flush=True)

    # Squelette JSON final sans le champ "fondation"
    infos_club_data = {
        "identite": {
            "nom": "", 
            "numero_affiliation": "", 
            "ligue": "", 
            "district": ""
        },
        "contact_club": {
            "email": "", 
            "telephone": ""
        },
        "installation": {
            "nom": "Jacques Hunaut 1",
            "description": "Stade d'entraînement"
        },
        "staff": {
            "bureau": {
                "president": {
                    "nom": "Non renseigné",
                    "email": "",
                    "telephone": ""
                },
                "vice_president": "Non renseigné"
            },
            "seniors": [
                {
                    "role": "Coach",
                    "nom": "Jerome",
                    "telephone": "06 10 58 28 63"
                },
                {
                    "role": "2nd Coach",
                    "nom": "Lucas",
                    "telephone": "07 83 61 26 05"
                }
            ]
        }
    }

    try:
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        # Extraction du payload JSON interne d'Angular
        state_locator = page.locator('#ng-state')
        
        if state_locator.count() > 0:
            state_text = state_locator.inner_text()
            state_data = json.loads(state_text)
            
            # On cherche la bonne requête API dans l'état Angular
            club_api_data = {}
            for key, value in state_data.items():
                if key.startswith(f'analog_GET|/api/data/clubs/clCod/{club_id}'):
                    club_api_data = value.get('body', {})
                    break
            
            if club_api_data:
                # --- IDENTITE ---
                infos_club_data["identite"]["nom"] = club_api_data.get("nom", "")
                infos_club_data["identite"]["numero_affiliation"] = str(club_api_data.get("clCod", ""))
                
                district_obj = club_api_data.get("parent", {})
                ligue_obj = district_obj.get("parent", {})
                infos_club_data["identite"]["district"] = district_obj.get("nomAbr", "")
                infos_club_data["identite"]["ligue"] = ligue_obj.get("nomAbr", "")
                
                # --- CONTACT CLUB ---
                contact_obj = club_api_data.get("contact", {})
                infos_club_data["contact_club"]["email"] = contact_obj.get("valeur", "")
                
                contacts_diff = club_api_data.get("contactsDiffusables", [])
                for c in contacts_diff:
                    # On cherche le téléphone dans les contacts diffusables
                    if "Téléphone" in c.get("type", "") or c.get("code") == "TA":
                        infos_club_data["contact_club"]["telephone"] = c.get("valeur", "")
                
                # --- STAFF (BUREAU) ---
                membres = club_api_data.get("membres", [])
                for membre in membres:
                    titre = membre.get("titre", "")
                    nom_complet = f"{membre.get('prenom', '')} {membre.get('nom', '')}".strip()
                    
                    if titre == "PRESIDENT":
                        infos_club_data["staff"]["bureau"]["president"]["nom"] = nom_complet
                        # Récupération spécifique des contacts du président (Alain)
                        for contact in membre.get("contacts", []):
                            type_contact = contact.get("type", "")
                            valeur = contact.get("valeur", "")
                            
                            if "Email" in type_contact:
                                infos_club_data["staff"]["bureau"]["president"]["email"] = valeur
                            elif "Téléphone" in type_contact:
                                infos_club_data["staff"]["bureau"]["president"]["telephone"] = valeur
                                
                    elif titre == "VICE PRESIDENT":
                        # Pour le vice-président on garde une simple string selon ton exemple
                        infos_club_data["staff"]["bureau"]["vice_president"] = nom_complet

    except PlaywrightError as e:
        print(f"[information] Erreur Playwright : {e}")
    except json.JSONDecodeError:
        print("[information] Impossible de lire l'état Angular de la FFF.")
    except Exception as e:
        print(f"[information] Erreur inattendue : {e}")

    return infos_club_data