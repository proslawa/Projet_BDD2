from config import get_connection, ITEMS_PER_PAGE


def get_enseignant_by_utilisateur(utilisateur_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT idEnseignant, nom, prenom FROM Enseignant WHERE idUtilisateur=?", utilisateur_id)
    r = cur.fetchone(); conn.close()
    if not r: return None
    return {"id": r[0], "nom": r[1], "prenom": r[2]}


def get_enseignants(page=1, search=""):
    offset = (page - 1) * ITEMS_PER_PAGE
    conn   = get_connection(); cur = conn.cursor()
    conds  = ["1=1"]; params = []
    if search:
        conds.append("(e.nom LIKE ? OR e.prenom LIKE ? OR e.grade LIKE ?)")
        params += [f"%{search}%"] * 3
    where = "WHERE " + " AND ".join(conds)
    cur.execute(f"SELECT COUNT(*) FROM Enseignant e {where}", params)
    total = cur.fetchone()[0]
    cur.execute(f"""
        SELECT e.idEnseignant, e.nom, e.prenom, e.grade, u.email
        FROM Enseignant e
        JOIN Utilisateur u ON e.idUtilisateur = u.idUtilisateur
        {where}
        ORDER BY e.nom, e.prenom
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, params + [offset, ITEMS_PER_PAGE])
    rows = cur.fetchall(); conn.close()
    return (
        [{"id": r[0], "nom": r[1], "prenom": r[2], "grade": r[3], "email": r[4]} for r in rows],
        total, max(1, -(-total // ITEMS_PER_PAGE)),
    )


def get_enseignant_by_id(enseignant_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT e.idEnseignant, e.nom, e.prenom, e.grade, u.email, u.idUtilisateur
        FROM Enseignant e
        JOIN Utilisateur u ON e.idUtilisateur = u.idUtilisateur
        WHERE e.idEnseignant = ?
    """, enseignant_id)
    r = cur.fetchone(); conn.close()
    if not r: return None
    return {"id": r[0], "nom": r[1], "prenom": r[2], "grade": r[3],
            "email": r[4], "id_utilisateur": r[5]}


def get_enseignements_enseignant(enseignant_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT en.idEnseignement, c.nom_classe, c.niveau,
               m.nom_matiere, m.coefficient, ue.nom_ue, f.nom_filiere
        FROM Enseignement en
        JOIN Classe c   ON en.idClasse  = c.idClasse
        JOIN Matiere m  ON en.idMatiere = m.idMatiere
        JOIN UE ue      ON m.idUE       = ue.idUE
        JOIN Filiere f  ON c.idFiliere  = f.idFiliere
        WHERE en.idEnseignant = ?
        ORDER BY f.nom_filiere, c.nom_classe, m.nom_matiere
    """, enseignant_id)
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "classe": r[1], "niveau": r[2], "matiere": r[3],
             "coeff": r[4], "ue": r[5], "filiere": r[6]} for r in rows]


def create_enseignant(nom, prenom, grade, email, mot_de_passe):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO Utilisateur (email, mot_de_passe, role, actif, date_creation)
        VALUES (?, ?, 'enseignant', 1, GETDATE())
    """, email, mot_de_passe)
    cur.execute("SELECT SCOPE_IDENTITY()")
    id_user = int(cur.fetchone()[0])
    cur.execute("""
        INSERT INTO Enseignant (idUtilisateur, nom, prenom, grade)
        VALUES (?, ?, ?, ?)
    """, id_user, nom, prenom, grade)
    conn.commit(); conn.close()


def update_enseignant(enseignant_id, nom, prenom, grade, email, id_utilisateur):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("UPDATE Utilisateur SET email=? WHERE idUtilisateur=?", email, id_utilisateur)
    cur.execute("""
        UPDATE Enseignant SET nom=?, prenom=?, grade=?
        WHERE idEnseignant=?
    """, nom, prenom, grade, enseignant_id)
    conn.commit(); conn.close()


def delete_enseignant(enseignant_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT idUtilisateur FROM Enseignant WHERE idEnseignant=?", enseignant_id)
    r = cur.fetchone()
    cur.execute("""DELETE FROM Assister WHERE idSeance_cours IN (
        SELECT sc.idSeance_cours FROM Seance_cours sc
        JOIN Enseignement en ON sc.idEnseignement = en.idEnseignement
        WHERE en.idEnseignant = ?)""", enseignant_id)
    cur.execute("""DELETE FROM Seance_cours WHERE idEnseignement IN (
        SELECT idEnseignement FROM Enseignement WHERE idEnseignant=?)""", enseignant_id)
    cur.execute("DELETE FROM Enseignement WHERE idEnseignant=?", enseignant_id)
    cur.execute("DELETE FROM Enseignant   WHERE idEnseignant=?", enseignant_id)
    if r: cur.execute("DELETE FROM Utilisateur WHERE idUtilisateur=?", r[0])
    conn.commit(); conn.close()
