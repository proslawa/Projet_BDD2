"""
PORTAIL ÉTUDIANT — Application Flask
=====================================
Lancer   : python app.py
URL      : http://127.0.0.1:5000
Login    : utilise un email/mot_de_passe de la table Utilisateur
"""
from app import create_app

flask_app = create_app()

if __name__ == "__main__":
    flask_app.run(debug=True, host="127.0.0.1", port=5000)
