# Projet BDD2 - Portail academique (Flask + SQL Server)

Application web de gestion academique developpee dans le cadre du projet BDD2.
Le projet couvre l'authentification, la gestion des etudiants/enseignants, les inscriptions,
les notes, les presences et l'emploi du temps.
Application en ligne : https://projet-bdd2.onrender.com/auth/login

## Technologies utilisees
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-CC2927?style=for-the-badge&logo=microsoftsqlserver&logoColor=white)
![Azure SQL](https://img.shields.io/badge/Azure%20SQL-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=000000)
![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)
![Jinja](https://img.shields.io/badge/Jinja-B41717?style=for-the-badge&logo=jinja&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

## Auteur
- Lawa FOUMSOU 
- Ameth FAYE
- Tamsir NDONG
- Bashir COMPAORE
- Haba FROMO

## Superviseur
- Prof. Saliou THIAW

## Objectifs
- Centraliser la gestion academique dans une seule application.
- Exploiter une base SQL Server relationnelle pour les operations metier.
- Fournir une interface web simple pour les profils admin, enseignant et etudiant.

## Fonctions principales
- Authentification par email/mot de passe.
- Tableau de bord par role.
- Gestion des etudiants (liste, detail, CRUD, export Excel).
- Gestion des enseignants (liste, detail, CRUD).
- Gestion des inscriptions.
- Saisie, consultation et releves de notes.
- Export PDF des releves de notes (admin).
- Gestion des seances et feuilles de presence.
- Consultation de l'emploi du temps.

## Dossiers et fichiers du projet
- `app/` : coeur de l'application Flask.
- `app/models/` : acces donnees et logique metier (auth, etudiants, enseignants, notes, presences, stats, etc.).
- `app/routes/` : routes Flask par domaine fonctionnel.
- `app/templates/` : vues HTML (auth, dashboard, etudiants, enseignants, notes, presences, emploi du temps, etc.).
- `image/` : ressources d'images utilisees dans l'interface.
- `app.py` : point d'entree local.
- `wsgi.py` : point d'entree WSGI pour deploiement (Gunicorn).
- `config.py` : configuration via variables d'environnement + connexion SQL Server.
- `config.example.py` : exemple de configuration.
- `requirements.txt` : dependances Python.
- `Dockerfile` : conteneur de deploiement (Render).
- `render.yaml` : configuration Render.
- `DEPLOY_RENDER.md` : guide de deploiement Render + Azure SQL.
- `.env.example` : exemple de variables d'environnement.

## Prerequis
- Python 3.10+
- SQL Server (local ou Azure SQL)
- ODBC Driver 18 for SQL Server

## Installation locale
```bash
pip install -r requirements.txt
```

## Configuration
Creer un fichier `.env` (ou definir les variables dans l'environnement systeme) :

```env
SECRET_KEY=replace-with-a-strong-secret
ITEMS_PER_PAGE=10
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_SERVER=your-server.database.windows.net
DB_PORT=1433
DB_DATABASE=PROJET_BDD2
DB_USER=your_user
DB_PASSWORD=your_password
DB_ENCRYPT=yes
DB_TRUST_CERT=no
DB_TIMEOUT=30
```

## Lancement en local
```bash
python app.py
```

Application accessible sur `http://127.0.0.1:5000`.

## API interne de verification
- `GET /health` : verifie que le service web est operationnel.

## Deploiement
Le projet est prepare pour un deploiement Docker sur Render avec base Azure SQL.

- URL de l'application : https://projet-bdd2.onrender.com/auth/login
- Guide complet : `DEPLOY_RENDER.md`
- Build/Run : `Dockerfile`
- Config service Render : `render.yaml`

## Qualite et securite
- Requetes SQL parametrees via `pyodbc`.
- Separation claire models/routes/templates.
- Variables sensibles externalisees via environnement.

## Licence
Projet academique BDD2.
