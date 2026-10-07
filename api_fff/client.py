from playwright.sync_api import sync_playwright, Error as PlaywrightError
from playwright_stealth import Stealth

from .endpoints.match import read_match_from_page
from .endpoints.matchs import read_matchs_from_page
from .endpoints.classement import read_classement_from_page
from .endpoints.information.information import read_information_from_page
from .endpoints.stats import generer_statistiques_joueurs

class API_FFF:
    def __init__(self, club_id="530273", club_name="parmain-a-c"):
        self.club_id = club_id
        self.club_name = club_name
        self.equipe_id = None

        try:
            # Initialisation Stealth v2 compatible
            self._playwright_manager = Stealth().use_sync(sync_playwright())
            self._playwright = self._playwright_manager.__enter__()
            
            # Lancement du navigateur avec arguments anti-bot pour GitHub Actions
            self.browser = self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-infobars",
                    "--window-size=1920,1080",
                    "--disable-dev-shm-usage",
                ]
            )
            
            self.context = self.browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="fr-FR"
            )
            
            self.page = self.context.new_page()
            
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
    
    def information(self):
        try:
            return read_information_from_page(self.page, self.club_id, self.club_name)
        except PlaywrightError:
            print("\n[Erreur de connexion] Impossible de récupérer les informations du club.")
            return {}
        except Exception as e:
            print(f"\n[Erreur inattendue lors de la récupération des infos] {e}")
            return {}
    
    def statistiques_joueurs(self, nom_equipe, matchs_data, nom_club_cible="PARMAIN"):
        """Génère les statistiques des joueurs basées sur les matchs récupérés."""
        try:
            return generer_statistiques_joueurs(nom_equipe, matchs_data, nom_club_cible)
        except Exception as e:
            print(f"\n[Erreur inattendue lors de la génération des statistiques] {e}")
            return {}