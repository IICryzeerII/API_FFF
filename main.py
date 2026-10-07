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
            
            api.set_equipe(equipe_id)
            
            print(f"[1/3] Récupération du classement...")
            classement_data = api.classement()
            
            filename_classement = f"classement_{nom_equipe}.json"
            with open(filename_classement, "w", encoding="utf-8") as f:
                json.dump(classement_data, f, ensure_ascii=False, indent=4)
            print(f"✅ {filename_classement} généré avec succès.")
            
            print(f"[2/3] Récupération de la liste des matchs...")
            matchs_data = api.matchs()
            
            print(f"[3/3] Récupération des feuilles de match détaillées...")
            if "items" in matchs_data:
                for match_item in matchs_data["items"]:
                    match_url = match_item.get("url")
                    if match_url:
                        print(f"  -> Analyse du match : {match_url}")
                        match_details = api.match(match_url)
                        if match_details:
                            match_item.update(match_details)
            
            filename_matchs = f"matchs_{nom_equipe}.json"
            total_matchs = len(matchs_data.get("items", []))
            with open(filename_matchs, "w", encoding="utf-8") as f:
                json.dump(matchs_data, f, ensure_ascii=False, indent=4)
            print(f"✅ {filename_matchs} généré avec succès ({total_matchs} matchs enregistrés).")

            # --- GÉNÉRATION DES STATISTIQUES DES JOUEURS ---
            print(f"📊 Génération des statistiques des joueurs pour {nom_equipe.upper()}...")
            stats_data = api.statistiques_joueurs(nom_equipe, matchs_data, nom_club_cible="PARMAIN")
            
            filename_stats = f"stats_joueurs_{nom_equipe}.json"
            with open(filename_stats, "w", encoding="utf-8") as f:
                json.dump(stats_data, f, ensure_ascii=False, indent=4)
            
            alerte = stats_data.get("controle_integrite", {}).get("alerte_incoherence", False)
            print(f"✅ {filename_stats} généré avec succès. (Alerte Admin : {alerte})")

    print("\n🎉 Toutes les équipes ont été traitées ! L'application mobile est à jour.")

if __name__ == "__main__":
    main()