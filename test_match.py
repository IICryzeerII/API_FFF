import json
from api_fff.client import API_FFF

def tester_un_match():
    # L'URL doit être relative car votre read_match_from_page ajoute déjà le BASE_URL
    url_cible = "/competition/match/56532822-entente-sportive-herblay-garges-les-gonesse-f-c-m"
    
    with API_FFF() as api:
        print(f"🚀 Lancement du test sur le match : {url_cible}")
        
        # On attaque directement la fonction match() sans passer par la liste de la saison
        details = api.match(url_cible)
        
        # Sauvegarde du résultat dans un fichier JSON pour l'analyser facilement
        with open("test_resultat_match.json", "w", encoding="utf-8") as f:
            json.dump(details, f, ensure_ascii=False, indent=4)
            
        print("✅ Extraction terminée ! Regardez le fichier test_resultat_match.json")

if __name__ == "__main__":
    tester_un_match()