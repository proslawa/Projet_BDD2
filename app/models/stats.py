from config import get_connection


def get_stats_globales():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Etudiant");         nb_et  = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Enseignant");       nb_en  = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Filiere");          nb_fi  = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Classe");           nb_cl  = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Inscription");      nb_ins = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Note");             nb_no  = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Seance_cours");     nb_se  = cur.fetchone()[0]
    cur.execute("SELECT AVG(CAST(note AS FLOAT)) FROM Note WHERE note IS NOT NULL")
    avg_r = cur.fetchone()[0]
    conn.close()
    return {
        "etudiants":    nb_et,
        "enseignants":  nb_en,
        "filieres":     nb_fi,
        "classes":      nb_cl,
        "inscriptions": nb_ins,
        "notes":        nb_no,
        "seances":      nb_se,
        "moyenne":      round(avg_r, 2) if avg_r else 0,
    }


def get_stats_notes_par_matiere():
    """Moyenne des notes par matière (pour graphique bar)."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT m.nom_matiere,
               AVG(CAST(n.note AS FLOAT)) AS moy,
               COUNT(n.note) AS nb
        FROM Note n
        JOIN Evaluation ev ON n.idEvaluation = ev.idEvaluation
        JOIN Matiere m ON ev.idMatiere = m.idMatiere
        WHERE n.note IS NOT NULL
        GROUP BY m.nom_matiere
        ORDER BY moy DESC
    """)
    rows = cur.fetchall(); conn.close()
    return [{"matiere": r[0], "moyenne": round(r[1], 2), "nb": r[2]} for r in rows]


def get_distribution_notes():
    """Distribution des notes en tranches (pour histogramme)."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT
            SUM(CASE WHEN note < 5  THEN 1 ELSE 0 END) AS tr1,
            SUM(CASE WHEN note >= 5  AND note < 8  THEN 1 ELSE 0 END) AS tr2,
            SUM(CASE WHEN note >= 8  AND note < 10 THEN 1 ELSE 0 END) AS tr3,
            SUM(CASE WHEN note >= 10 AND note < 12 THEN 1 ELSE 0 END) AS tr4,
            SUM(CASE WHEN note >= 12 AND note < 15 THEN 1 ELSE 0 END) AS tr5,
            SUM(CASE WHEN note >= 15 AND note < 18 THEN 1 ELSE 0 END) AS tr6,
            SUM(CASE WHEN note >= 18 THEN 1 ELSE 0 END) AS tr7
        FROM Note WHERE note IS NOT NULL
    """)
    r = cur.fetchone(); conn.close()
    return {
        "labels": ["< 5", "5-8", "8-10", "10-12", "12-15", "15-18", "≥ 18"],
        "data":   [r[0], r[1], r[2], r[3], r[4], r[5], r[6]]
    }


def get_taux_presence_par_classe():
    """Taux de présence moyen par classe (pour graphique)."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT c.nom_classe,
               COUNT(CASE WHEN a.present=1 THEN 1 END) * 100.0 / NULLIF(COUNT(a.present),0) AS taux
        FROM Classe c
        JOIN Enseignement en ON en.idClasse = c.idClasse
        JOIN Seance_cours sc ON sc.idEnseignement = en.idEnseignement
        JOIN Assister a ON a.idSeance_cours = sc.idSeance_cours
        GROUP BY c.nom_classe
        ORDER BY taux DESC
    """)
    rows = cur.fetchall(); conn.close()
    return [{"classe": r[0], "taux": round(r[1], 1) if r[1] else 0} for r in rows]


def get_repartition_par_filiere():
    """Répartition des étudiants par filière."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT f.nom_filiere, COUNT(DISTINCT e.idEtudiant) AS nb
        FROM Filiere f
        JOIN Classe c ON c.idFiliere = f.idFiliere
        JOIN Inscription i ON i.idClasse = c.idClasse
        JOIN Etudiant e ON e.idEtudiant = i.idEtudiant
        GROUP BY f.nom_filiere
        ORDER BY nb DESC
    """)
    rows = cur.fetchall(); conn.close()
    return [{"filiere": r[0], "nb": r[1]} for r in rows]


def get_notes_par_type_eval():
    """Moyenne par type d'évaluation."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT ev.type_evaluation, AVG(CAST(n.note AS FLOAT)) AS moy, COUNT(*) AS nb
        FROM Note n
        JOIN Evaluation ev ON n.idEvaluation = ev.idEvaluation
        WHERE n.note IS NOT NULL
        GROUP BY ev.type_evaluation
        ORDER BY moy DESC
    """)
    rows = cur.fetchall(); conn.close()
    return [{"type": r[0], "moyenne": round(r[1], 2), "nb": r[2]} for r in rows]


def get_stats_etudiant(etudiant_id):
    """Stats personnelles pour un étudiant connecté."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT AVG(CAST(note AS FLOAT)) FROM Note WHERE idEtudiant=? AND note IS NOT NULL", etudiant_id)
    avg = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Note WHERE idEtudiant=?", etudiant_id)
    nb_notes = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(CASE WHEN a.present=1 THEN 1 END) * 100.0 / NULLIF(COUNT(*),0)
        FROM Assister a WHERE a.idEtudiant=?
    """, etudiant_id)
    taux_p = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM Inscription WHERE idEtudiant=?
    """, etudiant_id)
    nb_insc = cur.fetchone()[0]
    conn.close()
    return {
        "moyenne": round(avg, 2) if avg else 0,
        "nb_notes": nb_notes,
        "taux_presence": round(taux_p, 1) if taux_p else 0,
        "nb_inscriptions": nb_insc,
    }


def get_stats_enseignant(enseignant_id):
    """Stats personnelles pour un enseignant connecté."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Enseignement WHERE idEnseignant=?", enseignant_id)
    nb_cours = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM Seance_cours sc
        JOIN Enseignement en ON sc.idEnseignement = en.idEnseignement
        WHERE en.idEnseignant=?
    """, enseignant_id)
    nb_seances = cur.fetchone()[0]
    cur.execute("""
        SELECT AVG(CAST(n.note AS FLOAT))
        FROM Note n
        JOIN Evaluation ev ON n.idEvaluation = ev.idEvaluation
        JOIN Matiere m ON ev.idMatiere = m.idMatiere
        JOIN Enseignement en ON en.idMatiere = m.idMatiere
        WHERE en.idEnseignant=? AND n.note IS NOT NULL
    """, enseignant_id)
    avg = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(DISTINCT en.idClasse) FROM Enseignement en WHERE en.idEnseignant=?
    """, enseignant_id)
    nb_classes = cur.fetchone()[0]
    conn.close()
    return {
        "nb_cours": nb_cours,
        "nb_seances": nb_seances,
        "moyenne_classe": round(avg, 2) if avg else 0,
        "nb_classes": nb_classes,
    }
