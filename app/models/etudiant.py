from config import get_connection, ITEMS_PER_PAGE


def get_filieres():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT idFiliere, nom_filiere FROM Filiere ORDER BY nom_filiere")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "nom": r[1]} for r in rows]


def get_stats():
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
    # Distribution notes
    cur.execute("""
        SELECT
          SUM(CASE WHEN note < 10 THEN 1 ELSE 0 END),
          SUM(CASE WHEN note >= 10 AND note < 12 THEN 1 ELSE 0 END),
          SUM(CASE WHEN note >= 12 AND note < 14 THEN 1 ELSE 0 END),
          SUM(CASE WHEN note >= 14 AND note < 16 THEN 1 ELSE 0 END),
          SUM(CASE WHEN note >= 16 THEN 1 ELSE 0 END)
        FROM Note WHERE note IS NOT NULL
    """)
    dist = cur.fetchone()
    # Moyennes par filiere
    cur.execute("""
        SELECT f.nom_filiere, AVG(CAST(n.note AS FLOAT))
        FROM Note n
        JOIN Evaluation ev ON n.idEvaluation=ev.idEvaluation
        JOIN Matiere m ON ev.idMatiere=m.idMatiere
        JOIN UE ue ON m.idUE=ue.idUE
        JOIN Semestre s ON ue.idSemestre=s.idSemestre
        JOIN Enseignement en2 ON en2.idMatiere=m.idMatiere
        JOIN Classe c ON en2.idClasse=c.idClasse
        JOIN Filiere f ON c.idFiliere=f.idFiliere
        WHERE n.note IS NOT NULL
        GROUP BY f.nom_filiere
    """)
    moy_filieres = cur.fetchall()
    # Taux présence global
    cur.execute("SELECT COUNT(*) FROM Assister WHERE present=1")
    nb_presents = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM Assister")
    nb_total_ass = cur.fetchone()[0]
    conn.close()
    return {
        "etudiants":   nb_et,
        "enseignants": nb_en,
        "filieres":    nb_fi,
        "classes":     nb_cl,
        "inscriptions": nb_ins,
        "notes":       nb_no,
        "seances":     nb_se,
        "moyenne":     round(avg_r, 2) if avg_r else 0,
        "dist_notes":  [int(x or 0) for x in dist] if dist else [0,0,0,0,0],
        "moy_filieres_labels": [r[0] for r in moy_filieres],
        "moy_filieres_vals":   [round(float(r[1]),2) for r in moy_filieres],
        "taux_presence": round(nb_presents/nb_total_ass*100,1) if nb_total_ass else 0,
    }


def get_stats_etudiant(etudiant_id):
    """Stats personnalisées pour le dashboard étudiant."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM Note WHERE idEtudiant=?", etudiant_id)
    nb_notes = cur.fetchone()[0]
    cur.execute("SELECT AVG(CAST(note AS FLOAT)) FROM Note WHERE idEtudiant=? AND note IS NOT NULL", etudiant_id)
    r = cur.fetchone(); avg = round(float(r[0]),2) if r[0] else 0
    cur.execute("""
        SELECT COUNT(*) FROM Assister a
        JOIN Seance_cours sc ON a.idSeance_cours=sc.idSeance_cours
        WHERE a.idEtudiant=? AND a.present=1
    """, etudiant_id)
    nb_pres = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM Assister a WHERE a.idEtudiant=?
    """, etudiant_id)
    nb_tot = cur.fetchone()[0]
    # Notes par matière pour radar/bar
    cur.execute("""
        SELECT m.nom_matiere, AVG(CAST(n.note AS FLOAT))
        FROM Note n
        JOIN Evaluation ev ON n.idEvaluation=ev.idEvaluation
        JOIN Matiere m ON ev.idMatiere=m.idMatiere
        WHERE n.idEtudiant=? AND n.note IS NOT NULL
        GROUP BY m.nom_matiere
        ORDER BY m.nom_matiere
    """, etudiant_id)
    rows = cur.fetchall()
    conn.close()
    return {
        "nb_notes": nb_notes,
        "moyenne": avg,
        "nb_presences": nb_pres,
        "nb_seances": nb_tot,
        "taux_presence": round(nb_pres/nb_tot*100,1) if nb_tot else 0,
        "notes_labels": [r[0] for r in rows],
        "notes_vals":   [round(float(r[1]),2) for r in rows],
    }


def get_stats_enseignant(enseignant_id):
    """Stats pour le dashboard enseignant."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(DISTINCT en.idClasse) FROM Enseignement en
        WHERE en.idEnseignant=?
    """, enseignant_id)
    nb_classes = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(*) FROM Seance_cours sc
        JOIN Enseignement en ON sc.idEnseignement=en.idEnseignement
        WHERE en.idEnseignant=?
    """, enseignant_id)
    nb_seances = cur.fetchone()[0]
    cur.execute("""
        SELECT COUNT(DISTINCT en.idMatiere) FROM Enseignement en
        WHERE en.idEnseignant=?
    """, enseignant_id)
    nb_matieres = cur.fetchone()[0]
    # Moyenne par matière enseignée
    cur.execute("""
        SELECT m.nom_matiere, AVG(CAST(n.note AS FLOAT))
        FROM Note n
        JOIN Evaluation ev ON n.idEvaluation=ev.idEvaluation
        JOIN Matiere m ON ev.idMatiere=m.idMatiere
        JOIN Enseignement en ON en.idMatiere=m.idMatiere
        WHERE en.idEnseignant=? AND n.note IS NOT NULL
        GROUP BY m.nom_matiere
    """, enseignant_id)
    rows = cur.fetchall()
    conn.close()
    return {
        "nb_classes": nb_classes,
        "nb_seances": nb_seances,
        "nb_matieres": nb_matieres,
        "matieres_labels": [r[0] for r in rows],
        "matieres_moyennes": [round(float(r[1]),2) for r in rows],
    }


def get_etudiants(page=1, search="", filiere_id=""):
    offset = (page - 1) * ITEMS_PER_PAGE
    conn   = get_connection(); cur = conn.cursor()
    conds  = ["1=1"]; params = []
    if search:
        conds.append("(e.nom LIKE ? OR e.prenom LIKE ? OR e.matricule LIKE ?)")
        params += [f"%{search}%"] * 3
    if filiere_id:
        conds.append("EXISTS(SELECT 1 FROM Inscription i2 JOIN Classe c2 ON i2.idClasse=c2.idClasse WHERE i2.idEtudiant=e.idEtudiant AND c2.idFiliere=?)")
        params.append(int(filiere_id))
    where = "WHERE " + " AND ".join(conds)
    cur.execute(f"SELECT COUNT(*) FROM Etudiant e {where}", params)
    total = cur.fetchone()[0]
    cur.execute(f"""
        SELECT e.idEtudiant, e.matricule, e.nom, e.prenom,
               e.date_naissance, u.email,
               (SELECT TOP 1 c2.nom_classe FROM Inscription i2
                JOIN Classe c2 ON i2.idClasse=c2.idClasse
                WHERE i2.idEtudiant=e.idEtudiant
                ORDER BY i2.date_inscription DESC) AS classe
        FROM Etudiant e
        JOIN Utilisateur u ON e.idUtilisateur = u.idUtilisateur
        {where}
        ORDER BY e.nom, e.prenom
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, params + [offset, ITEMS_PER_PAGE])
    rows = cur.fetchall(); conn.close()
    return (
        [{"id": r[0], "matricule": r[1], "nom": r[2], "prenom": r[3],
          "date_naissance": r[4], "email": r[5], "classe": r[6] or "—"} for r in rows],
        total, max(1, -(-total // ITEMS_PER_PAGE)),
    )


def get_etudiant_by_id(etudiant_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT e.idEtudiant, e.matricule, e.nom, e.prenom,
               e.date_naissance, u.email, u.idUtilisateur, u.role
        FROM Etudiant e
        JOIN Utilisateur u ON e.idUtilisateur = u.idUtilisateur
        WHERE e.idEtudiant = ?
    """, etudiant_id)
    r = cur.fetchone(); conn.close()
    if not r: return None
    return {"id": r[0], "matricule": r[1], "nom": r[2], "prenom": r[3],
            "date_naissance": r[4], "email": r[5], "id_utilisateur": r[6], "role": r[7]}


def get_etudiant_by_utilisateur(utilisateur_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT idEtudiant, nom, prenom FROM Etudiant WHERE idUtilisateur=?", utilisateur_id)
    r = cur.fetchone(); conn.close()
    if not r: return None
    return {"id": r[0], "nom": r[1], "prenom": r[2]}


def get_inscriptions_etudiant(etudiant_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT i.idInscription, c.nom_classe, c.niveau,
               f.nom_filiere, a.annee_debut, a.annee_fin, i.date_inscription
        FROM Inscription i
        JOIN Classe c ON i.idClasse = c.idClasse
        JOIN Filiere f ON c.idFiliere = f.idFiliere
        JOIN Annee_academique a ON i.idAnnee_academique = a.idAnnee_academique
        WHERE i.idEtudiant = ?
        ORDER BY a.annee_debut DESC
    """, etudiant_id)
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "classe": r[1], "niveau": r[2], "filiere": r[3],
             "debut": r[4], "fin": r[5], "date_insc": r[6]} for r in rows]


def get_notes_etudiant(etudiant_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT m.nom_matiere, ev.type_evaluation, ev.date_evaluation,
               n.note, m.coefficient, ue.nom_ue
        FROM Note n
        JOIN Evaluation ev ON n.idEvaluation = ev.idEvaluation
        JOIN Matiere m ON ev.idMatiere = m.idMatiere
        JOIN UE ue ON m.idUE = ue.idUE
        WHERE n.idEtudiant = ?
        ORDER BY ue.nom_ue, m.nom_matiere, ev.date_evaluation DESC
    """, etudiant_id)
    rows = cur.fetchall(); conn.close()
    return [{"matiere": r[0], "type": r[1], "date": r[2],
             "note": float(r[3]) if r[3] is not None else None,
             "coeff": r[4], "ue": r[5]} for r in rows]


def create_etudiant(matricule, nom, prenom, date_naissance, email, mot_de_passe):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO Utilisateur (email, mot_de_passe, role, actif, date_creation)
        VALUES (?, ?, 'etudiant', 1, GETDATE())
    """, email, mot_de_passe)
    cur.execute("SELECT SCOPE_IDENTITY()")
    id_user = int(cur.fetchone()[0])
    cur.execute("""
        INSERT INTO Etudiant (idUtilisateur, matricule, nom, prenom, date_naissance)
        VALUES (?, ?, ?, ?, ?)
    """, id_user, matricule, nom, prenom, date_naissance)
    conn.commit(); conn.close()


def update_etudiant(etudiant_id, matricule, nom, prenom, date_naissance, email, id_utilisateur):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("UPDATE Utilisateur SET email=? WHERE idUtilisateur=?", email, id_utilisateur)
    cur.execute("""
        UPDATE Etudiant SET matricule=?, nom=?, prenom=?, date_naissance=?
        WHERE idEtudiant=?
    """, matricule, nom, prenom, date_naissance, etudiant_id)
    conn.commit(); conn.close()


def delete_etudiant(etudiant_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT idUtilisateur FROM Etudiant WHERE idEtudiant=?", etudiant_id)
    r = cur.fetchone()
    cur.execute("DELETE FROM Note        WHERE idEtudiant=?", etudiant_id)
    cur.execute("DELETE FROM Assister    WHERE idEtudiant=?", etudiant_id)
    cur.execute("DELETE FROM Inscription WHERE idEtudiant=?", etudiant_id)
    cur.execute("DELETE FROM Etudiant    WHERE idEtudiant=?", etudiant_id)
    if r: cur.execute("DELETE FROM Utilisateur WHERE idUtilisateur=?", r[0])
    conn.commit(); conn.close()


def get_all_etudiants_export():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT e.matricule, e.nom, e.prenom, e.date_naissance, u.email,
               (SELECT TOP 1 c2.nom_classe FROM Inscription i2
                JOIN Classe c2 ON i2.idClasse=c2.idClasse
                WHERE i2.idEtudiant=e.idEtudiant
                ORDER BY i2.date_inscription DESC)
        FROM Etudiant e
        JOIN Utilisateur u ON e.idUtilisateur=u.idUtilisateur
        ORDER BY e.nom, e.prenom
    """)
    rows = cur.fetchall(); conn.close()
    return rows
