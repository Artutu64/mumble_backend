#!/bin/bash
set -e

echo "[*] Création du virtual environnement..."
cd /app
source venv/bin/activate
echo "[+] Fin de la création de l'environnement !"


echo "[*] Export des variables d'environment..."
if [ -f /app/.env ]; then
    export $(grep -v '^#' /app/.env | tr -d '\r' | xargs)
fi
echo "[+] Fin de l'export des variables d'environnement !"


echo "[?] Variables d'environnement chargées :"
env | grep -E 'APP_|MURMUR_|ICE_'


echo "[*] Reconfiguration de mumble..."
PW=$(openssl rand -base64 16)
echo "Mot de passe généré pour les superUser: $PW"
SCREEN_NAME="MUMBLE_SETUP"
screen -dmS "$SCREEN_NAME" bash -c "
    echo 'mumble-server mumble-server/password password $PW' | debconf-set-selections
    dpkg-reconfigure -f noninteractive mumble-server || true'
"
screen -dmS mumble /usr/sbin/murmurd -ini /etc/mumble-server.ini
echo "[+] Fin de la configuration de mumble !"


echo "[*] Compilation du relai Go..."
cd /app || { echo "Erreur: impossible d'accéder à /app"; exit 1; }

if go build -o tcpProxy tcpProxy.go; then
    echo "[+] Compilation réussie"
    chmod +x /app/tcpProxy
    echo "[*] Lancement du relai Go..."
    screen -dmS SERVEUR_RELAI_GO bash -c "cd /app && ./tcpProxy"
    echo "[+] Relai Go lancé !"
else
    echo "[-] Erreur de compilation du serveur relai Go"
    exit 1
fi


echo "[*] Lancement du frontend..."
screen -dmS SERVER_FRONTEND bash -c "cd /app && gunicorn -w 10 -b 0.0.0.0:9000 runfrontend:app"
echo "[*] Compilation du reverseProxy Go..."
if go build -o reverseProxy reverseProxy.go; then
    echo "[+] Compilation réussie"
    chmod +x /app/reverseProxy
    echo "[*] Lancement du reverseProxy Go..."
    screen -dmS REVERSE_PROXY_GO bash -c "cd /app && ./reverseProxy"
    echo "[+] reverseProxy Go lancé !"
else
    echo "[-] Erreur de compilation du serveur relai Go"
    exit 1
fi
echo "[+] Frontend lancé !"


echo "[*] Attente de Mumble (ICE sur 127.0.0.1:6502)..."
for i in {1..30}; do
    if nc -z 127.0.0.1 6502; then
        echo "[+] Mumble est prêt !"
        break
    fi
    sleep 1
done

echo "[*] Lancement de l'API REST murmur-rest..."
screen -dmS SERVER_API bash -c "cd /app && gunicorn -w 10 -b 0.0.0.0:8080 runserver:app"

exec /bin/sh
