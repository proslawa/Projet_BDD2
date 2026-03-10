from config import get_connection


def get_emploi_temps_classe(classe_id=None):
    """Récupère les séances pour affichage emploi du temps (toutes classes ou une classe)."""
    conn = get_connection(); cur = conn.cursor()
    sql = """
        SELECT sc.idSeance_cours, sc.date_seance,
               CONVERT(VARCHAR(5), sc.heure_debut, 108) AS debut,
               CONVERT(VARCHAR(5), sc.heure_fin, 108) AS fin,
               m.nom_matiere, c.nom_classe, c.idClasse,
               ens.nom + ' ' + ens.prenom AS enseignant,
               f.nom_filiere,
               DATEPART(WEEKDAY, sc.date_seance) AS jour_num,
               DATENAME(WEEKDAY, sc.date_seance) AS jour_nom
        FROM Seance_cours sc
        JOIN Enseignement en ON sc.idEnseignement = en.idEnseignement
        JOIN Matiere m ON en.idMatiere = m.idMatiere
        JOIN Classe c ON en.idClasse = c.idClasse
        JOIN Filiere f ON c.idFiliere = f.idFiliere
        JOIN Enseignant ens ON en.idEnseignant = ens.idEnseignant
    """
    params = []
    if classe_id:
        sql += " WHERE c.idClasse = ?"
        params.append(int(classe_id))
    sql += " ORDER BY sc.date_seance, sc.heure_debut"
    cur.execute(sql, params)
    rows = cur.fetchall(); conn.close()
    return [{
        "id": r[0], "date": r[1], "debut": r[2], "fin": r[3],
        "matiere": r[4], "classe": r[5], "classe_id": r[6],
        "enseignant": r[7], "filiere": r[8],
        "jour_num": r[9], "jour_nom": r[10],
    } for r in rows]


def get_emploi_temps_enseignant(enseignant_id):
    """Emploi du temps personnel d'un enseignant."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT sc.idSeance_cours, sc.date_seance,
               CONVERT(VARCHAR(5), sc.heure_debut, 108) AS debut,
               CONVERT(VARCHAR(5), sc.heure_fin, 108) AS fin,
               m.nom_matiere, c.nom_classe,
               DATEPART(WEEKDAY, sc.date_seance) AS jour_num,
               DATENAME(WEEKDAY, sc.date_seance) AS jour_nom,
               f.nom_filiere
        FROM Seance_cours sc
        JOIN Enseignement en ON sc.idEnseignement = en.idEnseignement
        JOIN Matiere m ON en.idMatiere = m.idMatiere
        JOIN Classe c ON en.idClasse = c.idClasse
        JOIN Filiere f ON c.idFiliere = f.idFiliere
        WHERE en.idEnseignant = ?
        ORDER BY sc.date_seance, sc.heure_debut
    """, enseignant_id)
    rows = cur.fetchall(); conn.close()
    return [{
        "id": r[0], "date": r[1], "debut": r[2], "fin": r[3],
        "matiere": r[4], "classe": r[5],
        "jour_num": r[6], "jour_nom": r[7], "filiere": r[8],
    } for r in rows]


def get_emploi_temps_etudiant(etudiant_id):
    """Emploi du temps personnel d'un étudiant (via sa classe)."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT sc.idSeance_cours, sc.date_seance,
               CONVERT(VARCHAR(5), sc.heure_debut, 108) AS debut,
               CONVERT(VARCHAR(5), sc.heure_fin, 108) AS fin,
               m.nom_matiere, c.nom_classe,
               ens.nom + ' ' + ens.prenom AS enseignant,
               DATEPART(WEEKDAY, sc.date_seance) AS jour_num,
               DATENAME(WEEKDAY, sc.date_seance) AS jour_nom
        FROM Inscription i
        JOIN Seance_cours sc ON 1=1
        JOIN Enseignement en ON sc.idEnseignement = en.idEnseignement AND en.idClasse = i.idClasse
        JOIN Matiere m ON en.idMatiere = m.idMatiere
        JOIN Classe c ON en.idClasse = c.idClasse
        JOIN Enseignant ens ON en.idEnseignant = ens.idEnseignant
        WHERE i.idEtudiant = ?
        ORDER BY sc.date_seance, sc.heure_debut
    """, etudiant_id)
    rows = cur.fetchall(); conn.close()
    return [{
        "id": r[0], "date": r[1], "debut": r[2], "fin": r[3],
        "matiere": r[4], "classe": r[5], "enseignant": r[6],
        "jour_num": r[7], "jour_nom": r[8],
    } for r in rows]


def get_classes_liste():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT c.idClasse, c.nom_classe, c.niveau, f.nom_filiere
        FROM Classe c JOIN Filiere f ON c.idFiliere = f.idFiliere
        ORDER BY f.nom_filiere, c.niveau, c.nom_classe
    """)
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "label": f"{r[1]} ({r[2]}) — {r[3]}"} for r in rows]
