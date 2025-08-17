import requests
import ipaddress
import secrets
from tabulate import tabulate  # pip install tabulate si nécessaire
import shutil

BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
RESET = "\033[0m"

#===============================================================
IP = "null"
hasDomain = False
Domain = "null"
HTTPS = False
Certificate = "./none.crt"
KEY = secrets.token_hex(16)
IV = secrets.token_hex(8)
PORT_HTTP=80
PORT_HTTPS=443
#===============================================================

try:
    print(rf"""{BLUE}
    
      /\/\   _   _  _ __ ___  | |__  | |  ___  | |(_) _ __  | | __     __   __/ |
     /    \ | | | || '_ ` _ \ | '_ \ | | / _ \ | || || '_ \ | |/ /     \ \ / /| |
    / /\/\ \| |_| || | | | | || |_) || ||  __/ | || || | | ||   <       \ V / | |
    \/    \/ \__,_||_| |_| |_||_.__/ |_| \___| |_||_||_| |_||_|\_\       \_/  |_|
    
    {RESET}""")


    print(f"{CYAN}Bienvenue dans le programme d'installation, en cas de problème avec le présent script, \nmerci d'ouvrir une issue sur github.{RESET}")
    print()

    def inputWithValues(string, values):
        choix = input(string)
        while not choix in values:
            choix = input(string)
        return choix

    choixModeIP = inputWithValues(f"Veuillez choisir le mode de saisie de l'IP (manuel/auto): ", ["auto", "manuel"])

    def get_public_ip():
        try:
            response = requests.get("https://api.ipify.org?format=json", timeout=5)
            response.raise_for_status()
            ip = response.json()["ip"]
            return ip
        except requests.RequestException as e:
            print(f"Erreur: {e}")
            return None

    forceManuel = False
    if choixModeIP == "auto":
        IP = get_public_ip()
        if IP == None:
            forceManuel = True

    def saisir_ip():
        while True:
            ip_str = input("Veuillez saisir l'adresse IP de votre machine: ")
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                return ip_obj
            except ValueError:
                pass

    if choixModeIP == "manuel" or forceManuel:
        IP = saisir_ip()

    print(f"{GREEN} |--> Votre adresse IP: {IP}{RESET}")

    defaultPort = inputWithValues("Voulez vous utiliser les ports par défaut pour le serveur web (80/443) (yes, y, no, n): ", ["yes", "y", "no", "n"])
    defaultPort = (defaultPort == "yes" or defaultPort == "y")

    if not defaultPort:
        portHttp = 80
        inValidPort = True
        while inValidPort:
            inValidPort = False
            try:
                portHttp = int(input(f"Veuillez saisir le port HTTP (>1000): "))
                if portHttp < 1000 or portHttp >= 65535 or portHttp == 9080:
                    inValidPort = True
            except ValueError:
                inValidPort = True
        PORT_HTTP = portHttp
        portHttp = 443
        inValidPort = True
        while inValidPort:
            inValidPort = False
            try:
                portHttp = int(input("Veuillez saisir le port HTTPS (>1000): "))
                if portHttp < 1000 or portHttp >= 65535 or portHttp == PORT_HTTP or portHttp == 9080:
                    inValidPort = True
            except ValueError:
                inValidPort = True
        PORT_HTTPS = portHttp
        print(f"{GREEN} |--> Ports HTTP.S: {PORT_HTTP}/{PORT_HTTPS}{RESET}")
    else:
        print(f"{GREEN} |--> Ports HTTP.S: {PORT_HTTP}/{PORT_HTTPS}{RESET}")

    hasDomainInput = inputWithValues("Avez vous un nom de domaine (yes, y, no, n): ", ["yes", "y", "no", "n"])
    hasDomain = (hasDomainInput == "yes" or hasDomainInput == "y")
    if not hasDomain:
        print(f"{RED} |--> Vous n'avez pas de domaine configuré !{RESET}")
    else:
        _domain = input("Saisissez votre nom de domaine: ")
        Domain = inputWithValues(f"Confirmez votre domaine ({_domain}): ", [_domain])
        print(f"{GREEN} |--> Votre domaine: {Domain}{RESET}")

    import os
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend


    def verifier_certificat(domain: str, filePath: str):
        # Vérification existence fichier
        if not os.path.isfile(filePath):
            print(f"{YELLOW} |--> Erreur: Le fichier n'existe pas.{RESET}")
            return False

        try:
            # Charger le certificat
            with open(filePath, "rb") as f:
                cert_data = f.read()

            cert = x509.load_pem_x509_certificate(cert_data, default_backend())

            # Récupérer le CN (Common Name)
            cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value

            # Récupérer les SAN (Subject Alternative Names)
            san_list = []
            try:
                ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                san_list = ext.value.get_values_for_type(x509.DNSName)
            except x509.ExtensionNotFound:
                pass  # Pas de SAN présent

            # Vérification du domaine
            if domain == cn or domain in san_list:
                return True
            else:
                print(f" |--> CN trouvé : {cn}")
                print(f" |--> SANs trouvés : {san_list}")
                return False

        except Exception as e:
            print(f"{YELLOW} |--> Erreur lors de la lecture du certificat : {e}{GREEN}")
            return False


    if hasDomain:
        configureHttps = inputWithValues(f"Voulez vous configurer https (yes, y, no, n): ", ["yes", "y", "no", "n"])
        inputWithValues(f"Avez vous créé un fichier key.pem (avec exactement ce nom) dans le dossier courrant (yes, y): ", ["yes", "y"])
        configureHttps = (configureHttps == "yes" or configureHttps == "y")
        if configureHttps:
            filePath = input("Merci de saisir le chemin du certificat (il doit être dans ce dossier): ")
            validCertificate = verifier_certificat(Domain, filePath)
            if validCertificate:
                if os.path.isfile("key.pem"):
                    HTTPS = True
                    Certificate = filePath
                    print(f"{GREEN} |--> Le certificat {Certificate} est valide (HTTPS: On){RESET}")
                else:
                    print(f"{RED} |--> Impossible d'activer HTTPS car il n'y a pas de fichier key.pem. {RESET}")
            else:
                print(f"{RED} |--> Impossible d'activer HTTPS car le certificat n'est pas valide. {RESET}")
        else:
            print(f"{RED} |--> Vous avez choisi de ne pas utiliser HTTPS{RESET}")

    print(f"\n\n\n\n\n\n\n\n\n\n\n\n                  {MAGENTA}Récapitulatif des valeurs{RESET}\n\n")
# Données
    data = {
        "IP": IP,
        "Domaine": Domain,
        "HTTPS": HTTPS,
        "Certificat": Certificate,
        "PORT_HTTP": PORT_HTTP,
        "PORT_HTTPS": PORT_HTTPS,
        "KEY": KEY,
        "IV": IV
    }

    table = [[k, v] for k, v in data.items()]
    print(tabulate(table, headers=["Clé", "Valeur"], tablefmt="grid"))

    def ecrire_env(nouveau_env: dict, fichier=".env2"):
        # Supprimer l'ancien fichier si il existe
        if os.path.exists(fichier):
            os.remove(fichier)

        # Écriture du nouveau fichier
        with open(fichier, "w") as f:
            for key, value in nouveau_env.items():
                f.write(f"{key}={value}\n")

    env_data = {
        "APP_HOST": "127.0.0.1",
        "APP_PORT": 9080,
        "APP_DEBUG": True,
        "ENABLE_AUTH": False,
        "USERS": "admin:password,admin2:password2",
        "MURMUR_ICE_HOST": "127.0.0.1",
        "MURMUR_ICE_PORT": 6502,
        "APP_LINK_PORT": 80,
        "PORT_HTTP": PORT_HTTP,
        "PORT_HTTPS": PORT_HTTPS,
        "KEY": KEY,
        "IV": IV,
        "IP": IP,
        "Domaine": Domain,
        "HTTPS": HTTPS,
        "Certificat": Certificate

    }

    def recreate_docker_script(port_http="80", port_https="443"):
        src = "./etc/docker.sh"
        dst = "./docker.sh"

        # 1. Supprimer l'ancien fichier s'il existe
        if os.path.exists(dst):
            os.remove(dst)

        # 2. Lire le contenu du fichier source
        with open(src, "r") as f:
            content = f.read()

        # 3. Remplacer la ligne docker run
        old_line = "docker run -it --name $CONTAINER_NAME -p 80:80 -p 443:443"
        new_line = f"docker run -it --name $CONTAINER_NAME -p {port_http}:80 -p {port_https}:443"
        content = content.replace(old_line, new_line)

        # 4. Écrire le nouveau fichier
        with open(dst, "w") as f:
            f.write(content)

        # Rendre exécutable (optionnel)
        os.chmod(dst, 0o755)
    recreate_docker_script(PORT_HTTP, PORT_HTTPS)

    print()
    ecrire_env(env_data, ".env")
    print(f"{CYAN}Gardez bien ces données en tête car vous en aurez besoin pour configurer le plugin.{RESET}")
    print()


except KeyboardInterrupt:
    print("\n")
    pass