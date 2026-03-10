# 🎓 Portail Étudiant — Flask + SQL Server

Application web Flask connectée à la base `PROJET_BDD2` sur MS SQL Server.

## 📦 Installation

### 1. Prérequis
- Python 3.x
- MS SQL Server 2025 Developer + SSMS
- ODBC Driver 18 for SQL Server
- La base `PROJET_BDD2` déjà créée avec tes données

### 2. Configurer la connexion (recommandé pour GitHub)
Définir les variables d'environnement :
```bash
SECRET_KEY="change-me"
DB_DRIVER="ODBC Driver 18 for SQL Server"
DB_SERVER=".\\PROJET_BDD2"
DB_DATABASE="PROJET_BDD2"
DB_USER="sa"                 # optionnel si Trusted_Connection
DB_PASSWORD="TonMotDePasse!" # optionnel si Trusted_Connection
DB_TRUST_CERT="yes"
```

> Tu peux utiliser `config.example.py` comme modèle.

### 3. Installer les dépendances
```bash
pip install flask pyodbc openpyxl
```

### 4. Lancer l'application
```bash
python app.py
```

### 5. Ouvrir dans le navigateur
```
http://127.0.0.1:5000
```

### 6. Se connecter
Utilise un **email + mot_de_passe** présent dans la table `Utilisateur` de ta base.

---

## 🗂️ Structure du projet

```
PORTAIL_BDD2/
├── app.py                      ← Point d'entrée
├── config.py                   ← ⚠️ À configurer
├── requirements.txt
└── app/
    ├── __init__.py             ← Factory Flask
    ├── models/
    │   ├── auth.py             ← Authentification
    │   ├── etudiant.py         ← CRUD étudiants
    │   ├── enseignant.py       ← CRUD enseignants
    │   ├── inscription.py      ← Inscriptions
    │   ├── note.py             ← Notes & évaluations
    │   └── presence.py         ← Séances & présences
    ├── routes/
    │   ├── auth.py             ← /auth/login, /auth/logout
    │   ├── dashboard.py        ← /dashboard
    │   ├── etudiants.py        ← /etudiants/*
    │   ├── enseignants.py      ← /enseignants/*
    │   ├── inscriptions.py     ← /inscriptions/*
    │   ├── notes.py            ← /notes/*
    │   ├── presences.py        ← /presences/*
    │   └── seances.py          ← /seances/*
    └── templates/
        ├── base.html           ← Layout sombre (sidebar)
        ├── auth/
        ├── dashboard/
        ├── etudiants/
        ├── enseignants/
        ├── inscriptions/
        ├── notes/
        ├── presences/
        └── seances/
```

## ✨ Fonctionnalités

| Module | Fonctionnalités |
|--------|----------------|
| **Étudiants** | Liste paginée, recherche, filtre filière, détail, CRUD, export Excel |
| **Enseignants** | Liste paginée, recherche, détail (enseignements assignés), CRUD |
| **Inscriptions** | Liste filtrée par classe/année, nouvelle inscription, suppression |
| **Notes** | Liste filtrée, saisie note, suppression, relevé par étudiant avec moyenne/UE |
| **Évaluations** | Créer une évaluation par matière et type |
| **Présences** | Tableau des séances, feuille d'appel interactive, taux de présence |
| **Séances** | Créer/supprimer une séance de cours |

## 🔒 Sécurité
- Sessions Flask chiffrées
- Toutes les routes protégées par `@login_required`
- Requêtes SQL paramétrées (protection injection SQL)

## Deployment Render (Docker)
- Files added:
  - Dockerfile
  - .dockerignore
  - render.yaml
  - .env.example
  - DEPLOY_RENDER.md
- Full guide: DEPLOY_RENDER.md
