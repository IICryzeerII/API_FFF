#!/bin/bash

VENV_NAME="venv"

# 1. Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "$VENV_NAME" ]; then
    echo "Création de l'environnement virtuel '$VENV_NAME'..."
    python3 -m venv $VENV_NAME
fi

# 2. Activer l'environnement virtuel
echo "Activation de l'environnement..."
source $VENV_NAME/bin/activate

# 3. Installer les dépendances
if [ -f "requirements.txt" ]; then
    echo "Mise à jour de pip..."
    pip install --upgrade pip
    echo "Installation des dépendances depuis requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ Aucun fichier requirements.txt trouvé dans le dossier actuel."
fi

echo "✅ Terminé ! Vous êtes maintenant dans l'environnement virtuel."