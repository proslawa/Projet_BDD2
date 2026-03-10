"""
PORTAIL ETUDIANT - Application Flask
====================================
Lancer   : python app.py
URL      : http://127.0.0.1:5000
Login    : utilise un email/mot_de_passe de la table Utilisateur
"""
import os

from app import create_app

flask_app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    flask_app.run(debug=True, host="0.0.0.0", port=port)
