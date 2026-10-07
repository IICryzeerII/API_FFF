#!/bin/bash

VENV_NAME="venv"

# Si le venv existe mais pointe vers un mauvais chemin ou est cassé, on le supprime sans pitié
if [ -d "$VENV_NAME" ]; then
    echo "Nettoyage de l'ancien environnement virtuel..."
    rm -rf $VENV_NAME
fi

# 1. Créer un environnement virtuel tout neuf et propre
echo "Création de l'environnement virtuel '$VENV_NAME'..."
python3 -m venv $VENV_NAME

# 2. Activer l'environnement
echo "Activation de l'environnement..."
source $VENV_NAME/bin/activate

# 3. Utiliser le pip du venv nouvellement créé
VENV_PIP="./$VENV_NAME/bin/pip"

# S'assurer que pip existe dans ce venv frais
if [ ! -f "$VENV_PIP" ]; then
    echo "Installation de pip dans le venv..."
    python3 -m ensurepip --default-pip
fi

# 4. Installer les dépendances
if [ -f "requirements.txt" ]; then
    echo "Mise à jour de pip..."
    $VENV_PIP install --upgrade pip
    echo "Installation des dépendances depuis requirements.txt..."
    $VENV_PIP install -r requirements.txt
else
    echo "⚠️ Aucun fichier requirements.txt trouvé dans le dossier actuel."
fi

echo "✅ Terminé ! Tout est installé proprement dans le venv."