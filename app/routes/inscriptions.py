from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.routes.auth import login_required
from app.models.inscription import (
    get_inscriptions, get_etudiants_liste,
    get_classes_liste, get_annees_liste,
    create_inscription, delete_inscription,
)

inscriptions_bp = Blueprint("inscriptions", __name__, url_prefix="/inscriptions")


@inscriptions_bp.route("/")
@login_required
def index():
    page      = request.args.get("page", 1, type=int)
    search    = request.args.get("search", "")
    classe_id = request.args.get("classe_id", "")
    annee_id  = request.args.get("annee_id", "")
    classes   = get_classes_liste()
    annees    = get_annees_liste()
    inscriptions, total, total_pages = get_inscriptions(page, search, classe_id, annee_id)
    return render_template(
        "inscriptions/index.html",
        inscriptions=inscriptions, total=total,
        total_pages=total_pages, page=page,
        search=search, classe_id=classe_id, annee_id=annee_id,
        classes=classes, annees=annees,
    )


@inscriptions_bp.route("/ajouter", methods=["GET", "POST"])
@login_required
def ajouter():
    etudiants = get_etudiants_liste()
    classes   = get_classes_liste()
    annees    = get_annees_liste()

    if request.method == "POST":
        id_etudiant = request.form.get("id_etudiant")
        id_classe   = request.form.get("id_classe")
        id_annee    = request.form.get("id_annee")
        date_insc   = request.form.get("date_inscription", "").strip() or None

        if not all([id_etudiant, id_classe, id_annee]):
            flash("Étudiant, classe et année académique sont obligatoires.", "danger")
            return render_template("inscriptions/form.html",
                                   etudiants=etudiants, classes=classes, annees=annees)
        try:
            create_inscription(int(id_etudiant), int(id_classe), int(id_annee), date_insc)
            flash("Inscription créée avec succès.", "success")
            return redirect(url_for("inscriptions.index"))
        except Exception as e:
            flash(f"Erreur : {e}", "danger")

    return render_template("inscriptions/form.html",
                           etudiants=etudiants, classes=classes, annees=annees)


@inscriptions_bp.route("/supprimer/<int:inscription_id>", methods=["POST"])
@login_required
def supprimer(inscription_id):
    try:
        delete_inscription(inscription_id)
        flash("Inscription supprimée.", "success")
    except Exception as e:
        flash(f"Erreur : {e}", "danger")
    return redirect(url_for("inscriptions.index"))
