import json
from api_fff.client import API_FFF

# Configuration des équipes avec leurs identifiants FFF d'après le README
EQUIPES = {
    "seniors_a": "2026_13474_SEM_1",
    "seniors_b": "2026_13474_SEM_2",
    "U15-U14": "2026_13474_U15_4"
}

def main():
    print("🚀 Lancement du scraper multi-équipes de la FFF...")
    
    # Utilisation du client FFF avec gestion du contexte (fermeture auto du navigateur)
    with API_FFF() as api:
        print(f"\n==============================================")
        print(f"🏟️  RÉCUPÉRATION DES INFOS DU CLUB")
        print(f"==============================================")
        
        infos_data = api.information()
        filename_infos = "infos_club.json"
        with open(filename_infos, "w", encoding="utf-8") as f:
            json.dump(infos_data, f, ensure_ascii=False, indent=4)
        print(f"✅ {filename_infos} généré avec succès.")

        for nom_equipe, equipe_id in EQUIPES.items():
            print(f"\n==============================================")
            print(f"⚽ TRAITEMENT DE LA ÉQUIPE : {nom_equipe.upper()}")
            print(f"==============================================")
            
            # Définition de l'équipe active
            api.set_equipe(equipe_id)
            
            # 1. Récupération et sauvegarde du classement
            print(f"[1/3] Récupération du classement...")
            classement_data = api.classement()
            
            filename_classement = f"classement_{nom_equipe}.json"
            with open(filename_classement, "w", encoding="utf-8") as f:
                json.dump(classement_data, f, ensure_ascii=False, indent=4)
            print(f"✅ {filename_classement} généré avec succès.")
            
            # 2. Récupération de la liste des matchs
            print(f"[2/3] Récupération de la liste des matchs...")
            matchs_data = api.matchs()
            
            # 3. Récupération des feuilles de match détaillées via api.match()
            print(f"[3/3] Récupération des feuilles de match détaillées...")
            if "items" in matchs_data:
                for match_item in matchs_data["items"]:
                    match_url = match_item.get("url")
                    if match_url:
                        print(f"  -> Analyse du match : {match_url}")
                        match_details = api.match(match_url)
                        if match_details:
                            # Met à jour les informations du match avec les détails de la feuille de match
                            match_item.update(match_details)
            
            filename_matchs = f"matchs_{nom_equipe}.json"
            total_matchs = len(matchs_data.get("items", []))
            with open(filename_matchs, "w", encoding="utf-8") as f:
                json.dump(matchs_data, f, ensure_ascii=False, indent=4)
            print(f"✅ {filename_matchs} généré avec succès ({total_matchs} matchs enregistrés).")

    print("\n🎉 Toutes les équipes ont été traitées ! L'application mobile est à jour.")

if __name__ == "__main__":
    main()