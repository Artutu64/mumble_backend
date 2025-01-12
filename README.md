Ceci est une copie modifiée de: https://github.com/alfg/murmur-rest

Elle est modifiée aux titres suivants:

    1. Liberté d'utilisation : La licence MIT permet d'utiliser, copier, modifier, fusionner, publier, distribuer, sous-licencier et même vendre des copies du logiciel, sans aucune restriction, tant que les conditions de la licence sont respectées.

    2. Conditions minimales : La seule exigence est d'inclure la mention du copyright et de la licence dans toutes les copies ou parties substantielles du logiciel. Cela garantit que l'auteur original est crédité.

    3. Aucune garantie : Le logiciel est fourni "tel quel", sans garantie d'aucune sorte. Cela signifie que les auteurs ne sont pas responsables des problèmes éventuels liés à l'utilisation du code.

# Installation

Deux scripts .sh sont disponibles pour rendre plus "simple" l'installation. Néanmoins, il engage l'utilisateur de comprendre les potentielles erreurs liées au lancement du programme.

Ils s'éxecutent dans l'ordre suivant:
    1. install.sh pour installer les librairies et packages système liées au programme (ex: mumble-server, les librairies pour zeroc). (need sudo perms)
    2. dep_collector.sh pour l'installation des dépendances dans le venv

# "Protection du backend"

Pour empecher n'importe qui de faire des requetes sur votre backend et donc d'en avoir le controle vous pouvez utiliser un firewall (ex: iptables).

    1. Faites la liste des adresses ip (privées et publiques) que vous voulez autoriser (vos machines) (par défaut, VOTRE_PORT=8080)

    2. Ajoutez les règles pour autoriser la connexion au port de l'application:
        ``sudo iptables -A INPUT -p tcp --dport VOTRE_PORT -s VOTRE_IP -j ACCEPT``
    
    3. Ajoutez la règle pour interdire la connexion des autres machines:
        ``sudo iptables -A INPUT -p tcp --dport VOTRE_PORT -j DROP``


# License
The MIT License (MIT)

Copyright (c) 2016 github.com/alfg

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.