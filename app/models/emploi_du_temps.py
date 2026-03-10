from config import get_connection


def get_emploi_du_temps(classe_id=None, enseignant_id=None, semaine=None):
    """
    Retourne les séances pour l'emploi du temps.
    semaine = "YYYY-Www" (ex: "2025-W12")
    """
    conn = get_connection(); cur = conn.cursor()
    conds = ["1=1"]; params = []
    if classe_id:
        conds.append("en.idClasse=?"); params.append(int(classe_id))
    if enseignant_id:
        conds.append("en.idEnseignant=?"); params.append(int(enseignant_id))
    if semaine:
        conds.append("DATEPART(ISO_WEEK, sc.date_seance)=? AND YEAR(sc.date_seance)=?")
        parts = semaine.split("-W")
        params += [int(parts[1]), int(parts[0])]
    where = "WHERE " + " AND ".join(conds)
    cur.execute(f"""
        SELECT sc.idSeance_cours, sc.date_seance,
               DATENAME(WEEKDAY, sc.date_seance) AS jour,
               DATEPART(WEEKDAY, sc.date_seance) AS num_jour,
               sc.heure_debut, sc.heure_fin,
               m.nom_matiere, c.nom_classe, c.niveau,
               ens.nom+' '+ens.prenom AS enseignant,
               f.nom_filiere, en.idClasse, en.idEnseignant,
               ue.nom_ue
        FROM Seance_cours sc
        JOIN Enseignement en ON sc.idEnseignement=en.idEnseignement
        JOIN Matiere m ON en.idMatiere=m.idMatiere
        JOIN UE ue ON m.idUE=ue.idUE
        JOIN Classe c ON en.idClasse=c.idClasse
        JOIN Filiere f ON c.idFiliere=f.idFiliere
        JOIN Enseignant ens ON en.idEnseignant=ens.idEnseignant
        {where}
        ORDER BY sc.date_seance, sc.heure_debut
    """, params)
    rows = cur.fetchall(); conn.close()
    return [{
        "id": r[0], "date": r[1], "jour": r[2], "num_jour": r[3],
        "debut": str(r[4])[:5] if r[4] else "", "fin": str(r[5])[:5] if r[5] else "",
        "matiere": r[6], "classe": r[7], "niveau": r[8],
        "enseignant": r[9], "filiere": r[10],
        "id_classe": r[11], "id_enseignant": r[12], "ue": r[13]
    } for r in rows]


def get_semaines_disponibles():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT
            CAST(YEAR(date_seance) AS VARCHAR)+'-W'+
            RIGHT('0'+CAST(DATEPART(ISO_WEEK,date_seance) AS VARCHAR),2) AS semaine,
            MIN(date_seance) AS debut_sem
        FROM Seance_cours
        GROUP BY YEAR(date_seance), DATEPART(ISO_WEEK, date_seance)
        ORDER BY debut_sem DESC
    """)
    rows = cur.fetchall(); conn.close()
    return [{"value": r[0], "label": f"Semaine {r[0]}"} for r in rows]


def get_classes_liste():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        SELECT c.idClasse, c.nom_classe, c.niveau, f.nom_filiere
        FROM Classe c JOIN Filiere f ON c.idFiliere=f.idFiliere
        ORDER BY f.nom_filiere, c.niveau
    """)
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "label": f"{r[1]} ({r[2]}) — {r[3]}"} for r in rows]


def get_enseignants_liste():
    conn = get_connection(); cur = conn.cursor()
    cur.execute("SELECT idEnseignant, nom, prenom, grade FROM Enseignant ORDER BY nom")
    rows = cur.fetchall(); conn.close()
    return [{"id": r[0], "label": f"{r[1]} {r[2]} — {r[3]}"} for r in rows]


def create_seance_edt(id_enseignement, date_seance, heure_debut, heure_fin):
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO Seance_cours (idEnseignement, date_seance, heure_debut, heure_fin)
        VALUES (?, ?, ?, ?)
    """, id_enseignement, date_seance, heure_debut, heure_fin)
    conn.commit(); conn.close()


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
