#!/bin/bash

screen -dmS mumble-server mumble-server -ini /etc/mumble-server.ini
screen -dmS SERVER_FRONTEND bash -c "cd /app && python3 runfrontend.py"

echo "[*] En attente de la compilation du relai Go..."

cd /app || { echo "Erreur: impossible d'accéder à /app"; exit 1; }

if go build -o tcpProxy tcpProxy.go; then
    echo "[+] Compilation du serveur relai Go réussie !"
    chmod +x /app/tcpProxy
    screen -dmS SERVEUR_RELAI_GO bash -c "cd /app && ./tcpProxy"
else
    echo "[-] Erreur lors de la compilation du serveur relai Go"
    exit 1
fi

echo "[*] En attente du démarrage de MUMBLE..."

sleep 10

echo "[+] MUMBLE vient de démarrer !"


screen -dmS SERVER_API bash -c "cd /app && python3 runserver.py"

/bin/sh
