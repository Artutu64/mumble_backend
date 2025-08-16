#!/bin/bash

# Vérifie si le script est exécuté avec sudo
if [ "$EUID" -ne 0 ]; then
  echo "Merci d'exécuter ce script avec sudo."
  exit 1
fi

# Nom de l'image et du conteneur
IMAGE_NAME="mumble-backend"
CONTAINER_NAME="mumble"

# Vérifie le premier argument
case "$1" in
  build)
    echo "Construction de l'image Docker..."
    sudo docker build -t $IMAGE_NAME .
    ;;
  run)
    echo "Lancement du conteneur Docker..."
    sudo docker run -it --name $CONTAINER_NAME -p 80:80 -p 443:443 -p 20821:20821 \
      -p 64739-64839:64739-64839/tcp -p 64739-64839:64739-64839/udp $IMAGE_NAME
    ;;
  stop)
    echo "Arrêt du conteneur Docker..."
    sudo docker stop $CONTAINER_NAME
    ;;
  delete)
    echo "Arrêt du conteneur Docker..."
    sudo docker stop $CONTAINER_NAME
    echo "Suppression du conteneur Docker..."
    sudo docker remove $CONTAINER_NAME
    ;;
  restart)
    echo "Redémarrage du conteneur Docker..."
    sudo docker restart $CONTAINER_NAME
    ;;
  *)
    echo "Usage : sudo ./docker.sh [build|run|stop|restart]"
    ;;
esac
