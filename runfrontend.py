from flask import Flask, request, Response
import os
import json

app = Flask(__name__)

def get_json_content(uuid):
    """
    Ouvre un fichier JSON situé dans 'uuids/<uuid>.json' et retourne son contenu en tant que dictionnaire.
    Retourne None si le fichier n'existe pas.
    """
    file_path = os.path.join('uuids', f'{uuid}.json')  # Chemin du fichier JSON

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data
    else:
        return None

@app.route('/')
def home():
    """
    Modifie dynamiquement le contenu de la page HTML avant de la retourner.
    """
    error_content = "error"
    uuid = request.args.get('uuid')

    file_path = os.path.join(os.getcwd(), 'error.html')  # Chemin absolu du fichier
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as html_file:
            error_content = html_file.read()

    if not uuid:
        return Response(error_content, mimetype='text/html')

    values = get_json_content(uuid)
    if values == None:
        return Response(error_content, mimetype='text/html')
    


    file_path = os.path.join(os.getcwd(), 'index.html')  # Chemin absolu du fichier
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()
        
        modified_content = html_content.replace("{MUMBLE_HOST}", values.get("host", "0.0.0.0"))
        modified_content = modified_content.replace("{MUMBLE_PORT}", values.get("port", "64738"))
        modified_content = modified_content.replace("{MUMBLE_PLAYER}", values.get("pseudo", "Unknown"))
        
        return Response(modified_content, mimetype='text/html')
    else:
        return Response(error_content, mimetype='text/html')

if __name__ == '__main__':
    APP_LINK_PORT = os.environ.get("APP_LINK_PORT", "80")
    app.run(debug=True, host='0.0.0.0', port=APP_LINK_PORT)
