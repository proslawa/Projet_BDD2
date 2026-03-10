from config import get_connection, ITEMS_PER_PAGE


def get_inscriptions(page=1, search="", classe_id="", annee_id=""):
    offset = (page - 1) * ITEMS_PER_PAGE
    conn   = get_connection(); cur = conn.cursor()

    conds  = ["1=1"]
    params = []
    if search:
        conds.append("(e.nom LIKE ? OR e.prenom LIKE ? OR e.matricule LIKE ?)")
        params += [f"%{search}%"] * 3
    if classe_id:
        conds.append("i.idClasse=?"); params.append(int(classe_id))
    if annee_id:
        conds.append("i.idAnnee_academique=?"); params.append(int(annee_id))

    where = "WHERE " + " AND ".join(conds)

    cur.execute(f"""
        SELECT COUNT(*) FROM Inscription i
        JOIN Etudiant e ON i.idEtudiant=e.idEtudiant
        JOIN Classe c ON i.idClasse=c.idClasse
        {where}
    """, params)
    total = cur.fetchone()[0]

    cur.execute(f"""
        SELECT i.idInscription, e.matricule, e.nom, e.prenom,
               c.nom_classe, c.niveau, f.nom_filiere,
               a.annee_debut, a.annee_fin, i.date_inscription,
               i.idEtudiant, i.idClasse, i.idAnnee_academique
        FROM Inscription i
        JOIN Etudiant e ON i.idEtudiant=e.idEtudiant
        JOIN Classe c ON i.idClasse=c.idClasse
        JOIN Filiere f ON c.idFiliere=f.idFiliere
        JOIN Annee_academique a ON i.idAnnee_academique=a.idAnnee_academique
        {where}
        ORDER BY a.annee_debut DESC, e.nom, e.prenom
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, params + [offset, ITEMS_PER_PAGE])

    rows = cur.fetchall(); conn.close()
    return (
        [{"id": r[0], "matricule": r[1], "nom": r[2], "prenom": r[3],
          "classe": r[4], "niveau": r[5], "filiere": r[6],
          "debut": r[7], "fin": r[8], "date_insc": r[9],
          "id_etudiant": r[10], "id_classe": r[11], "id_annee": r[12]} for r in rows],
        total,
        max(1, -(-total // ITEMS_PER_PAGE)),
    )


def get_etudiants_liste():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT idEtudiant, matricule, nom, prenom FROM Etudiant ORDER BY nom, prenom")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "label": f"{r[2]} {r[3]} ({r[1]})"} for r in rows]


def get_etudiants_liste_releves():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT e.idEtudiant, e.matricule, e.nom, e.prenom, c.nom_classe
        FROM Etudiant e
        OUTER APPLY (
            SELECT TOP 1 i.idClasse
            FROM Inscription i
            WHERE i.idEtudiant = e.idEtudiant
            ORDER BY i.date_inscription DESC
        ) i
        LEFT JOIN Classe c ON c.idClasse = i.idClasse
        ORDER BY e.nom, e.prenom
    """)
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "label": f"{r[2]} {r[3]} ({r[1]})", "classe": r[4]} for r in rows]


def get_classes_liste():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT c.idClasse, c.nom_classe, c.niveau, f.nom_filiere
        FROM Classe c JOIN Filiere f ON c.idFiliere=f.idFiliere
        ORDER BY f.nom_filiere, c.niveau, c.nom_classe
    """)
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "label": f"{r[1]} — {r[2]} ({r[3]})"} for r in rows]


def get_annees_liste():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT idAnnee_academique, annee_debut, annee_fin FROM Annee_academique ORDER BY annee_debut DESC")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "label": f"{r[1]}-{r[2]}"} for r in rows]


def create_inscription(id_etudiant, id_classe, id_annee, date_inscription):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO Inscription (idEtudiant, idClasse, idAnnee_academique, date_inscription)
        VALUES (?, ?, ?, ?)
    """, id_etudiant, id_classe, id_annee, date_inscription or None)
    conn.commit(); conn.close()


def delete_inscription(inscription_id):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("DELETE FROM Inscription WHERE idInscription=?", inscription_id)
    conn.commit(); conn.close()
