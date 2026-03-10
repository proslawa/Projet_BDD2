from config import get_connection, ITEMS_PER_PAGE


def get_matieres():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT m.idMatiere, m.nom_matiere, m.coefficient, ue.nom_ue, s.numero
        FROM Matiere m
        JOIN UE ue ON m.idUE=ue.idUE
        JOIN Semestre s ON ue.idSemestre=s.idSemestre
        ORDER BY s.numero, ue.nom_ue, m.nom_matiere
    """)
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "nom": r[1], "coeff": r[2], "ue": r[3], "semestre": r[4]} for r in rows]


def get_evaluations(matiere_id=""):
    conn = get_connection(); cur = conn.cursor()
    if matiere_id:
        cur.execute("""
            SELECT e.idEvaluation, e.type_evaluation, e.date_evaluation,
                   m.nom_matiere, m.idMatiere
            FROM Evaluation e JOIN Matiere m ON e.idMatiere=m.idMatiere
            WHERE e.idMatiere=?
            ORDER BY e.date_evaluation DESC
        """, matiere_id)
    else:
        cur.execute("""
            SELECT e.idEvaluation, e.type_evaluation, e.date_evaluation,
                   m.nom_matiere, m.idMatiere
            FROM Evaluation e JOIN Matiere m ON e.idMatiere=m.idMatiere
            ORDER BY e.date_evaluation DESC
        """)
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "type": r[1], "date": r[2], "matiere": r[3], "matiere_id": r[4]} for r in rows]


def get_notes(page=1, search="", evaluation_id="", matiere_id=""):
    offset = (page - 1) * ITEMS_PER_PAGE
    conn   = get_connection(); cur = conn.cursor()

    conds  = ["1=1"]
    params = []
    if search:
        conds.append("(e.nom LIKE ? OR e.prenom LIKE ? OR e.matricule LIKE ?)")
        params += [f"%{search}%"] * 3
    if evaluation_id:
        conds.append("n.idEvaluation=?"); params.append(int(evaluation_id))
    if matiere_id:
        conds.append("ev.idMatiere=?"); params.append(int(matiere_id))

    where = "WHERE " + " AND ".join(conds)

    cur.execute(f"""
        SELECT COUNT(*) FROM Note n
        JOIN Etudiant e ON n.idEtudiant=e.idEtudiant
        JOIN Evaluation ev ON n.idEvaluation=ev.idEvaluation
        {where}
    """, params)
    total = cur.fetchone()[0]

    cur.execute(f"""
        SELECT e.matricule, e.nom, e.prenom,
               m.nom_matiere, ev.type_evaluation, ev.date_evaluation,
               n.note, m.coefficient, ue.nom_ue,
               n.idEtudiant, n.idEvaluation, e.idEtudiant as eid
        FROM Note n
        JOIN Etudiant e ON n.idEtudiant=e.idEtudiant
        JOIN Evaluation ev ON n.idEvaluation=ev.idEvaluation
        JOIN Matiere m ON ev.idMatiere=m.idMatiere
        JOIN UE ue ON m.idUE=ue.idUE
        {where}
        ORDER BY e.nom, e.prenom, m.nom_matiere
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, params + [offset, ITEMS_PER_PAGE])

    rows = cur.fetchall(); conn.close()
    return (
        [{"matricule": r[0], "nom": r[1], "prenom": r[2],
          "matiere": r[3], "type": r[4], "date": r[5],
          "note": float(r[6]) if r[6] is not None else None,
          "coeff": r[7], "ue": r[8],
          "id_etudiant": r[9], "id_evaluation": r[10], "eid": r[11]} for r in rows],
        total,
        max(1, -(-total // ITEMS_PER_PAGE)),
    )


def get_note(id_etudiant, id_evaluation):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT note FROM Note WHERE idEtudiant=? AND idEvaluation=?",
                id_etudiant, id_evaluation)
    r = cur.fetchone(); conn.close()
    return float(r[0]) if r and r[0] is not None else None


def upsert_note(id_etudiant, id_evaluation, note):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT 1 FROM Note WHERE idEtudiant=? AND idEvaluation=?",
                id_etudiant, id_evaluation)
    exists = cur.fetchone()
    if exists:
        cur.execute("UPDATE Note SET note=? WHERE idEtudiant=? AND idEvaluation=?",
                    note, id_etudiant, id_evaluation)
    else:
        cur.execute("INSERT INTO Note (idEtudiant,idEvaluation,note) VALUES (?,?,?)",
                    id_etudiant, id_evaluation, note)
    conn.commit(); conn.close()


def delete_note(id_etudiant, id_evaluation):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Note WHERE idEtudiant=? AND idEvaluation=?",
                id_etudiant, id_evaluation)
    conn.commit(); conn.close()


def create_evaluation(id_matiere, type_eval, date_eval):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO Evaluation (idMatiere, type_evaluation, date_evaluation)
        VALUES (?, ?, ?)
    """, id_matiere, type_eval, date_eval)
    conn.commit(); conn.close()


def get_releve_notes(etudiant_id):
    """Calcul de la moyenne pondérée par UE et globale."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT ue.nom_ue, ue.credit, m.nom_matiere, m.coefficient,
               ev.type_evaluation, n.note
        FROM Note n
        JOIN Evaluation ev ON n.idEvaluation=ev.idEvaluation
        JOIN Matiere m ON ev.idMatiere=m.idMatiere
        JOIN UE ue ON m.idUE=ue.idUE
        WHERE n.idEtudiant=? AND n.note IS NOT NULL
        ORDER BY ue.nom_ue, m.nom_matiere
    """, etudiant_id)
    rows = cur.fetchall(); conn.close()

    ues = {}
    for ue_nom, credit, mat, coeff, type_ev, note in rows:
        if ue_nom not in ues:
            ues[ue_nom] = {"credit": credit, "matieres": {}}
        if mat not in ues[ue_nom]["matieres"]:
            ues[ue_nom]["matieres"][mat] = {"coeff": coeff, "notes": []}
        ues[ue_nom]["matieres"][mat]["notes"].append(float(note))

    result = []
    for ue_nom, ue_data in ues.items():
        moy_ue_num = moy_ue_den = 0
        matieres = []
        for mat, mdata in ue_data["matieres"].items():
            moy_mat = sum(mdata["notes"]) / len(mdata["notes"])
            moy_ue_num += moy_mat * mdata["coeff"]
            moy_ue_den += mdata["coeff"]
            matieres.append({"nom": mat, "coeff": mdata["coeff"],
                              "moyenne": round(moy_mat, 2)})
        moy_ue = round(moy_ue_num / moy_ue_den, 2) if moy_ue_den else 0
        result.append({"ue": ue_nom, "credit": ue_data["credit"],
                       "moyenne": moy_ue, "matieres": matieres})
    return result
