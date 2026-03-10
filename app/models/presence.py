from config import get_connection, ITEMS_PER_PAGE


def get_seances(page=1, enseignant_id="", classe_id=""):
    offset = (page - 1) * ITEMS_PER_PAGE
    conn   = get_connection(); cur = conn.cursor()

    conds  = ["1=1"]
    params = []
    if enseignant_id:
        conds.append("en.idEnseignant=?"); params.append(int(enseignant_id))
    if classe_id:
        conds.append("en.idClasse=?"); params.append(int(classe_id))

    where = "WHERE " + " AND ".join(conds)

    cur.execute(f"""
        SELECT COUNT(*) FROM Seance_cours sc
        JOIN Enseignement en ON sc.idEnseignement=en.idEnseignement
        {where}
    """, params)
    total = cur.fetchone()[0]

    cur.execute(f"""
        SELECT sc.idSeance_cours, sc.date_seance, sc.heure_debut, sc.heure_fin,
               m.nom_matiere, c.nom_classe, c.niveau,
               ens.nom+' '+ens.prenom AS enseignant,
               (SELECT COUNT(*) FROM Assister a WHERE a.idSeance_cours=sc.idSeance_cours AND a.present=1) AS nb_presents,
               (SELECT COUNT(*) FROM Assister a WHERE a.idSeance_cours=sc.idSeance_cours) AS nb_total
        FROM Seance_cours sc
        JOIN Enseignement en ON sc.idEnseignement=en.idEnseignement
        JOIN Matiere m ON en.idMatiere=m.idMatiere
        JOIN Classe c ON en.idClasse=c.idClasse
        JOIN Enseignant ens ON en.idEnseignant=ens.idEnseignant
        {where}
        ORDER BY sc.date_seance DESC, sc.heure_debut DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, params + [offset, ITEMS_PER_PAGE])

    rows = cur.fetchall(); conn.close()
    return (
        [{"id": r[0], "date": r[1], "debut": r[2], "fin": r[3],
          "matiere": r[4], "classe": r[5], "niveau": r[6],
          "enseignant": r[7], "nb_presents": r[8], "nb_total": r[9]} for r in rows],
        total,
        max(1, -(-total // ITEMS_PER_PAGE)),
    )


def get_seance_detail(seance_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT sc.idSeance_cours, sc.date_seance, sc.heure_debut, sc.heure_fin,
               m.nom_matiere, c.nom_classe, ens.nom+' '+ens.prenom
        FROM Seance_cours sc
        JOIN Enseignement en ON sc.idEnseignement=en.idEnseignement
        JOIN Matiere m ON en.idMatiere=m.idMatiere
        JOIN Classe c ON en.idClasse=c.idClasse
        JOIN Enseignant ens ON en.idEnseignant=ens.idEnseignant
        WHERE sc.idSeance_cours=?
    """, seance_id)
    r = cur.fetchone(); conn.close()
    if not r:
        return None
    return {"id": r[0], "date": r[1], "debut": r[2], "fin": r[3],
            "matiere": r[4], "classe": r[5], "enseignant": r[6]}


def get_presences_seance(seance_id):
    """Retourne tous les étudiants de la classe avec leur présence."""
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT e.idEtudiant, e.matricule, e.nom, e.prenom,
               COALESCE(a.present, 0) AS present
        FROM Seance_cours sc
        JOIN Enseignement en ON sc.idEnseignement=en.idEnseignement
        JOIN Inscription ins ON ins.idClasse=en.idClasse
        JOIN Etudiant e ON ins.idEtudiant=e.idEtudiant
        LEFT JOIN Assister a ON a.idEtudiant=e.idEtudiant AND a.idSeance_cours=sc.idSeance_cours
        WHERE sc.idSeance_cours=?
        ORDER BY e.nom, e.prenom
    """, seance_id)
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "matricule": r[1], "nom": r[2],
             "prenom": r[3], "present": bool(r[4])} for r in rows]


def save_presences(seance_id, presences_dict):
    """presences_dict = {id_etudiant: True/False}"""
    conn = get_connection(); cur = conn.cursor()
    for id_et, present in presences_dict.items():
        cur.execute("SELECT 1 FROM Assister WHERE idEtudiant=? AND idSeance_cours=?",
                    id_et, seance_id)
        if cur.fetchone():
            cur.execute("UPDATE Assister SET present=? WHERE idEtudiant=? AND idSeance_cours=?",
                        1 if present else 0, id_et, seance_id)
        else:
            cur.execute("INSERT INTO Assister (idEtudiant, idSeance_cours, present) VALUES (?,?,?)",
                        id_et, seance_id, 1 if present else 0)
    conn.commit(); conn.close()


def get_enseignants_liste():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT idEnseignant, nom, prenom, grade FROM Enseignant ORDER BY nom")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "label": f"{r[1]} {r[2]} — {r[3]}"} for r in rows]


def get_classes_liste():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT c.idClasse, c.nom_classe, c.niveau, f.nom_filiere
        FROM Classe c JOIN Filiere f ON c.idFiliere=f.idFiliere
        ORDER BY f.nom_filiere, c.niveau, c.nom_classe
    """)
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "label": f"{r[1]} ({r[2]}) — {r[3]}"} for r in rows]


def get_enseignements_liste():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT en.idEnseignement,
               ens.nom+' '+ens.prenom+' | '+m.nom_matiere+' | '+c.nom_classe AS label
        FROM Enseignement en
        JOIN Enseignant ens ON en.idEnseignant=ens.idEnseignant
        JOIN Matiere m ON en.idMatiere=m.idMatiere
        JOIN Classe c ON en.idClasse=c.idClasse
        ORDER BY ens.nom, m.nom_matiere
    """)
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "label": r[1]} for r in rows]


def create_seance(id_enseignement, date_seance, heure_debut, heure_fin):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO Seance_cours (idEnseignement, date_seance, heure_debut, heure_fin)
        VALUES (?, ?, ?, ?)
    """, id_enseignement, date_seance, heure_debut, heure_fin)
    conn.commit(); conn.close()


def delete_seance(seance_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Assister WHERE idSeance_cours=?", seance_id)
    cur.execute("DELETE FROM Seance_cours WHERE idSeance_cours=?", seance_id)
    conn.commit(); conn.close()
