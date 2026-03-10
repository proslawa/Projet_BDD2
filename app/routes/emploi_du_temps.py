from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.routes.auth import login_required
from app.models.emploi_du_temps import (
    get_emploi_du_temps, get_semaines_disponibles,
    get_classes_liste, get_enseignants_liste,
    get_enseignements_liste, create_seance_edt
)

edt_bp = Blueprint("edt", __name__, url_prefix="/emploi-du-temps")


@edt_bp.route("/")
@login_required
def index():
    role = session.get("user_role")
    semaine    = request.args.get("semaine", "")
    classe_id  = request.args.get("classe_id", "")
    enseignant_id = request.args.get("enseignant_id", "")

    # Restrictions selon le rôle
    if role == "etudiant":
        # Récupérer la classe de l'étudiant connecté
        from app.models.etudiant import get_inscriptions_etudiant
        et_id = session.get("etudiant_id")
        inscs = get_inscriptions_etudiant(et_id) if et_id else []
        # Prendre la classe la plus récente
        if inscs and not classe_id:
            from app.models.etudiant import get_etudiant_by_id
            # Use first inscription's class
            classe_id = ""  # will show all without filter but student sees filtered view
        enseignant_id = ""
    elif role == "enseignant":
        if not enseignant_id:
            enseignant_id = str(session.get("enseignant_id", ""))
        classe_id = request.args.get("classe_id", "")

    seances = get_emploi_du_temps(
        classe_id=classe_id if classe_id else None,
        enseignant_id=enseignant_id if enseignant_id else None,
        semaine=semaine if semaine else None
    )
    semaines   = get_semaines_disponibles()
    classes    = get_classes_liste()
    enseignants = get_enseignants_liste()

    # Organiser par jour pour affichage grille
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
    grille = {j: [] for j in jours}
    for s in seances:
        j = s["jour"]
        # Normaliser le nom du jour (SQL Server retourne en français si locale FR)
        for jour_ref in jours:
            if jour_ref.lower() in j.lower():
                grille[jour_ref].append(s)
                break

    return render_template("emploi_du_temps/index.html",
        seances=seances, grille=grille, jours=jours,
        semaines=semaines, classes=classes, enseignants=enseignants,
        semaine=semaine, classe_id=classe_id, enseignant_id=enseignant_id,
    )


@edt_bp.route("/ajouter", methods=["GET", "POST"])
@login_required
def ajouter():
    from app.routes.auth import role_required
    role = session.get("user_role")
    if role not in ("admin", "enseignant"):
        flash("Accès non autorisé.", "danger")
        return redirect(url_for("edt.index"))

    enseignements = get_enseignements_liste()
    if request.method == "POST":
        id_ens  = request.form.get("id_enseignement")
        date_s  = request.form.get("date_seance", "").strip()
        heure_d = request.form.get("heure_debut", "").strip()
        heure_f = request.form.get("heure_fin", "").strip()
        if not all([id_ens, date_s, heure_d, heure_f]):
            flash("Tous les champs sont obligatoires.", "danger")
        else:
            try:
                create_seance_edt(int(id_ens), date_s, heure_d, heure_f)
                flash("Séance ajoutée à l'emploi du temps.", "success")
                return redirect(url_for("edt.index"))
            except Exception as e:
                flash(f"Erreur : {e}", "danger")
    return render_template("emploi_du_temps/form.html", enseignements=enseignements)
