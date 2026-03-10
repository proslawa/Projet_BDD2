from config import get_connection


def get_user_by_email(email):
    conn = get_connection()
    cur  = conn.cursor()
    # Récupère aussi le profile_id (idEtudiant ou idEnseignant)
    cur.execute("""
        SELECT u.idUtilisateur, u.email, u.mot_de_passe, u.role, u.actif,
               COALESCE(e.idEtudiant, ens.idEnseignant) AS profile_id
        FROM Utilisateur u
        LEFT JOIN Etudiant e ON e.idUtilisateur = u.idUtilisateur
        LEFT JOIN Enseignant ens ON ens.idUtilisateur = u.idUtilisateur
        WHERE u.email = ?
    """, email)
    r = cur.fetchone()
    conn.close()
    if not r:
        return None
    return {
        "id":           r[0],
        "email":        r[1],
        "mot_de_passe": r[2],
        "role":         r[3],
        "actif":        r[4],
        "profile_id":   r[5],
    }
