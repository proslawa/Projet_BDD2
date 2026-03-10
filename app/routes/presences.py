from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.routes.auth import login_required
from app.models.presence import (
    get_seances, get_seance_detail,
    get_presences_seance, save_presences,
    get_enseignants_liste, get_classes_liste,
)

presences_bp = Blueprint("presences", __name__, url_prefix="/presences")


@presences_bp.route("/")
@login_required
def index():
    page          = request.args.get("page", 1, type=int)
    enseignant_id = request.args.get("enseignant_id", "")
    classe_id     = request.args.get("classe_id", "")
    enseignants   = get_enseignants_liste()
    classes       = get_classes_liste()
    seances, total, total_pages = get_seances(page, enseignant_id, classe_id)
    return render_template(
        "presences/index.html",
        seances=seances, total=total, total_pages=total_pages, page=page,
        enseignant_id=enseignant_id, classe_id=classe_id,
        enseignants=enseignants, classes=classes,
    )


@presences_bp.route("/<int:seance_id>", methods=["GET", "POST"])
@login_required
def feuille(seance_id):
    seance   = get_seance_detail(seance_id)
    if not seance:
        flash("Séance introuvable.", "danger")
        return redirect(url_for("presences.index"))

    if request.method == "POST":
        etudiants = get_presences_seance(seance_id)
        presences = {}
        for et in etudiants:
            val = request.form.get(f"present_{et['id']}")
            presences[et["id"]] = val == "1"
        try:
            save_presences(seance_id, presences)
            flash("Présences enregistrées.", "success")
            return redirect(url_for("presences.index"))
        except Exception as e:
            flash(f"Erreur : {e}", "danger")

    presences = get_presences_seance(seance_id)
    return render_template("presences/feuille.html", seance=seance, presences=presences)
# role check done in template
