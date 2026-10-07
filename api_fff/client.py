from playwright.sync_api import sync_playwright, Error as PlaywrightError
from playwright_stealth import Stealth

from .endpoints.match import read_match_from_page
from .endpoints.matchs import read_matchs_from_page
from .endpoints.classement import read_classement_from_page

class API_FFF:
    # On ne définit plus l'equipe_id dans le constructeur, mais dynamiquement
    def __init__(self, club_id="530273", club_name="parmain-a-c"):
        self.club_id = club_id
        self.club_name = club_name
        self.equipe_id = None

        try:
            self._playwright_manager = Stealth().use_sync(sync_playwright())
            self._playwright = self._playwright_manager.__enter__()
            self.browser = self._playwright.chromium.launch(headless=True)
            self.page = self.browser.new_page()
        except Exception as e:
            print("[Erreur Critique] Impossible d'initialiser le navigateur (Vérifiez l'installation de Playwright).")
            raise e

    def set_equipe(self, equipe_id):
        """Met à jour l'ID de l'équipe pour les requêtes suivantes."""
        self.equipe_id = equipe_id

    def close(self):
        """Ferme proprement la session du navigateur."""
        try:
            if hasattr(self, 'browser') and self.browser:
                self.browser.close()
            if hasattr(self, '_playwright_manager') and self._playwright_manager:
                self._playwright_manager.__exit__(None, None, None)
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def matchs(self):
        if not self.equipe_id:
            raise ValueError("Veuillez définir une equipe_id avec api.set_equipe() avant d'appeler matchs()")
            
        try:
            return read_matchs_from_page(self.page, self.club_id, self.club_name, self.equipe_id)
        except PlaywrightError:
            print("\n[Erreur de connexion] Impossible de joindre les serveurs de la FFF. Vérifiez votre connexion Internet.")
            return {"items": [], "totalItems": 0}
        except Exception as e:
            print(f"\n[Erreur inattendue lors de la récupération des matchs] {e}")
            return {"items": [], "totalItems": 0}

    def match(self, match_url):
        try:
            return read_match_from_page(self.page, match_url)
        except PlaywrightError:
            print(f"\n[Erreur de connexion] Impossible de charger la page du match: {match_url}")
            return None
        except Exception as e:
            print(f"\n[Erreur inattendue lors du chargement du match] {e}")
            return None
    
    def classement(self):  
        if not self.equipe_id:
            raise ValueError("Veuillez définir une equipe_id avec api.set_equipe() avant d'appeler classement()")
            
        try:
            return read_classement_from_page(self.page, self.club_id, self.club_name, self.equipe_id)
        except PlaywrightError:
            print("\n[Erreur de connexion] Impossible de récupérer le classement.")
            return {"items": [], "totalItems": 0}