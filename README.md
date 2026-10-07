# ⚽ FFF Scraper API (Générateur JSON pour App Mobile)

Ce projet est un scraper Python automatisé utilisant Playwright pour extraire les données officielles du site de la Fédération Française de Football (FFF) (https://epreuves.fff.fr/). 
Il génère des fichiers JSON légers, propres et structurés (matchs, classements, compositions, événements) prêts à être consommés par une application mobile (Flutter, React Native, Swift, etc.).

## ✨ Fonctionnalités

* Multi-équipes dynamique : Scrape simultanément les données de plusieurs équipes d'un même club (Seniors A, Seniors B, U16, etc.).
* Calendrier complet : Gère le défilement infini (infinite scroll) pour récupérer toute la saison.
* Détails poussés des matchs : Extraction du score, de la date, du lieu, des compositions (titulaires/remplaçants) et des logos des clubs.
* Ligne du temps (Timeline) : Croisement intelligent des données pour associer les événements (buts, cartons, changements) à la fois au fil du match global et à chaque joueur individuellement.
* Bypass Anti-Bot : Utilisation de playwright-stealth pour éviter les blocages de la FFF.

---

## 🛠️ Prérequis et Installation

1. Cloner le projet et accéder au dossier.
2. Installer les dépendances Python :
   pip install playwright playwright-stealth
3. Installer les navigateurs Playwright :
   playwright install chromium

---

## 🚀 Utilisation et Configuration

Toute la configuration se fait au début du fichier main.py. Vous pouvez y ajouter toutes les équipes de votre club que vous souhaitez suivre :

# Dans main.py
EQUIPES = {
    "seniors_a": "2026_13474_SEM_1",
    "seniors_b": "2026_13474_SEM_2",
    # Ajoutez d'autres équipes ici...
}

Astuce : Vous trouverez l'ID d'une équipe (2026_XXXXXX_SEM_X) directement dans l'URL de sa page sur le site de la FFF.

Lancer le scraper :
python main.py

Le script va générer automatiquement deux fichiers par équipe à la racine du projet : matchs_nom_equipe.json et classement_nom_equipe.json.

---

## 📂 Architecture du Projet

📁 projet/
├── main.py
└── 📁 api_fff/
    ├── client.py
    └── 📁 endpoints/
        ├── classement.py
        ├── matchs.py
        ├── match.py
        ├── html_parser.py
        └── formatter.py
## 🧪 Apparté : Tester une feuille de match complète

L'extraction d'une feuille de match est complexe car la structure HTML de la FFF change selon l'état du match (à venir, joué, arrêté). 

Si vous modifiez le code du parseur (html_parser.py) et que vous souhaitez tester sa robustesse sans avoir à lancer tout le script main.py (qui peut être long), utilisez ce lien de match de référence :

👉 "/competition/match/56532822-entente-sportive-herblay-garges-les-gonesse-f-c-m"

Pourquoi ce match est parfait pour vos tests ?
C'est un "stress-test" idéal car il contient presque tous les cas de figure du football amateur :
* Un score validé (6-0).
* Des compositions d'équipes complètes (titulaires et remplaçants).
* Des joueurs notés "Anonyme".
* De multiples événements dans la timeline : des changements (substitution) et des cartons (yellow-card).

Comment le tester rapidement ?
Créez un petit fichier test_match.py à la racine du projet avec ce code :

import json
from api_fff.client import API_FFF

def tester_match_complet():
    # URL de test idéale (Herblay vs Garges)
    url_test = "/competition/match/56532822-entente-sportive-herblay-garges-les-gonesse-f-c-m"
    
    with API_FFF() as api:
        print(f"Lancement du test sur : {url_test}")
        details = api.match(url_test)
        
        with open("test_resultat.json", "w", encoding="utf-8") as f:
            json.dump(details, f, ensure_ascii=False, indent=4)
            
        print("✅ Test terminé ! Vérifiez le fichier test_resultat.json")

if __name__ == "__main__":
    tester_match_complet()

Exécutez python test_match.py. Si le fichier test_resultat.json généré a une belle structure avec les moments_forts remplis et les événements bien assignés aux joueurs, c'est que votre parseur fonctionne parfaitement !
