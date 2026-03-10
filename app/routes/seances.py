from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.routes.auth import login_required
from app.models.presence import (
    get_enseignements_liste, create_seance, delete_seance,
)

seances_bp = Blueprint("seances", __name__, url_prefix="/seances")


@seances_bp.route("/ajouter", methods=["GET", "POST"])
@login_required
def ajouter():
    enseignements = get_enseignements_liste()
    if request.method == "POST":
        id_ens    = request.form.get("id_enseignement")
        date_s    = request.form.get("date_seance", "").strip()
        heure_d   = request.form.get("heure_debut", "").strip()
        heure_f   = request.form.get("heure_fin", "").strip()
        if not all([id_ens, date_s, heure_d, heure_f]):
            flash("Tous les champs sont obligatoires.", "danger")
        else:
            try:
                create_seance(int(id_ens), date_s, heure_d, heure_f)
                flash("Séance créée.", "success")
                return redirect(url_for("presences.index"))
            except Exception as e:
                flash(f"Erreur : {e}", "danger")
    return render_template("seances/form.html", enseignements=enseignements)


@seances_bp.route("/supprimer/<int:seance_id>", methods=["POST"])
@login_required
def supprimer(seance_id):
    try:
        delete_seance(seance_id)
        flash("Séance supprimée.", "success")
    except Exception as e:
        flash(f"Erreur : {e}", "danger")
    return redirect(url_for("presences.index"))
