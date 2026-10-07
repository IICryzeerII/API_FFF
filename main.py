import json
from api_fff.client import API_FFF

# Configuration de toutes les équipes du club à scrapper
# Format -> "nom_du_fichier_souhaité": "ID_de_l_equipe_sur_la_FFF"
EQUIPES = {
    "seniors_a": "2026_13474_SEM_1",
     "seniors_b": "2026_13474_SEM_2",
    "U15-U14": "2026_13474_U15_4"
}

def main():
    # L'API est initialisée une seule fois pour tout le club
    with API_FFF(club_id="530273", club_name="parmain-a-c") as api:
        print("🚀 Lancement du scraper multi-équipes de la FFF...", flush=True)

        for nom_equipe, equipe_id in EQUIPES.items():
            print(f"\n==============================================")
            print(f"⚽ TRAITEMENT DE L'ÉQUIPE : {nom_equipe.upper()}")
            print(f"==============================================")
            
            # On indique à l'API quelle équipe on souhaite scrapper maintenant
            api.set_equipe(equipe_id)

            # 1. Récupération et sauvegarde du classement
            print("[1/3] Récupération du classement...", flush=True)
            classement_data = api.classement()
            with open(f"classement_{nom_equipe}.json", "w", encoding="utf-8") as f:
                json.dump(classement_data, f, ensure_ascii=False, indent=4)
            print(f"✅ classement_{nom_equipe}.json généré avec succès.")

            # 2. Récupération de la liste des matchs
            print("[2/3] Récupération de la liste des matchs...", flush=True)
            matchs_base = api.matchs()
            
            matchs_complets = []
            
            # 3. Boucle sur chaque match pour enrichir
            print("[3/3] Récupération des feuilles de match détaillées...", flush=True)
            for match in matchs_base.get("items", []):
                url = match["url"]
                print(f"  -> Analyse du match : {url}", flush=True)
                
                details = api.match(url)
                
                if details:
                    # On met à jour l'objet match existant avec les logos et détails trouvés
                    match.update(details)
                
                matchs_complets.append(match)

            donnees_finales = {
                "totalItems": len(matchs_complets),
                "items": matchs_complets
            }

            # Sauvegarde finale pour l'équipe en cours
            with open(f"matchs_{nom_equipe}.json", "w", encoding="utf-8") as f:
                json.dump(donnees_finales, f, ensure_ascii=False, indent=4)
            
            print(f"✅ matchs_{nom_equipe}.json généré avec succès ({len(matchs_complets)} matchs enregistrés).")

        print("\n🎉 Toutes les équipes ont été traitées ! L'application mobile est à jour.")

if __name__ == "__main__":
    main()