<div align="center">
    <br/>
    <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/8f/Icons_mumble.svg/1200px-Icons_mumble.svg.png" alt="Mumble Logo" width="200"/>
    <h1>Mumble Link v1</h1>
</div>

<p align="center">
	🌐 <a href="https://github.com/Artutu64/MumbleLink">Spigot-MC</a>
	 &#124;
	📓 <a href="https://github.com/Artutu64/MumbleLink">Github</a>
	 &#124;
	🔎 <a href="https://github.com/Artutu64/MumbleLink/issues">Issue</a>
</p>

> 💬️ MumbleLink-Backend est le code qui gère la partie logique (création de serveur, création de lien) lié au plugin spigot MumbleLink.

# Issues et Report-bug
Merci de report les bugs dans l'onglet Issues du projet suivant (en précisant que l'erreur vient du backend): https://github.com/Artutu64/MumbleLink 

# Installation
*Depuis les dernières versions, Mumblelink-Backend n'est installable que via **_Docker_**.*

1. **Clônage:** Commencer par cloner le projet actuel 
```
git clone https://github.com/Artutu64/mumble_backend.git
```
2. **Installation des dépendances:** L'installation du projet nécessite: python3, venv et pip (pour le script de configuration) et le code fonctionne sur Docker.

3. **Configuration:** Utiliser les commandes suivantes et suivre le flot de questions
```
python3 -m venv venv
source venv/bin/activate
pip install requests
pip install ipaddress
pip install secrets
pip install tabulate
pip install pyopenssl
pip install cryptography
python3 scripts/install.py
deactivate
```
4. **Build:** Il faut ensuite build conteneur 
```
sudo ./docker.sh build
```
5. **Démarrage:** Puis démarrer le conteneur 
```
sudo ./docker.sh start
```

*Le ./docker.sh possède aussi les commandes [run|stop|restart|delete] afin d'executer les commandes Docker associées.*

# Modification web

Vous pouvez modifier le contenu des fichiers: error.html et index.html afin de customiser vos pages de connexion.
Néanmoins la page index.html doit inclure les textes suivants qui sont modifiés lors de l'affichage de la page au client:

    - {MUMBLE_HOST} : pour afficher le host de connexion au serveur mumble
    
    - {MUMBLE_PORT} : pour afficher le port du serveur mumble

    - {MUMBLE_PLAYER} : pour afficher le pseudo que doit utiliser le joueur sur mumble

# License
The MIT License (MIT)

Copyright (c) 2016 github.com/alfg

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
