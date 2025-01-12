#!/bin/bash

# Vérifier si le script est exécuté en tant que root
if [ "$EUID" -ne 0 ]; then
  echo "Erreur : Ce script doit être exécuté en tant que root." >&2
  exit 1
fi
sudo apt update && sudo apt install -y mumble-server

sudo touch /var/lib/mumble-server/murmur.sqlite
sudo chown mumble-server:mumble-server /var/lib/mumble-server/murmur.sqlite

sudo cp ./etc/murmur.ini /etc/mumble-server.ini

sudo dpkg-reconfigure mumble-server

echo ""
echo "Installation de mumble-server effectuée avec succès !"
echo ""

sudo apt install -y build-essential gcc g++ python3-dev
sudo apt install -y libssl-dev libbz2-dev
python3 -m pip install --upgrade pip setuptools wheel

sudo rm -rf venv

echo "Fin de l'installation des dépendances (packages). Pour finir l'installation, veuillez procéder comme suit:"

echo "1. Créer un venv: python3 -m venv venv"
echo "2. Activez votre environnement python: source venv/bin/activate"
echo "3. Lancez l'installation des dépendances python: sh dep_collector.sh"
echo ""
echo "A noter: Vous etes obligés de vous mettre dans l'environnement créé à chaque lancement du backend !"
exit 0