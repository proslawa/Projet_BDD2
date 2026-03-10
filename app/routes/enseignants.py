from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.routes.auth import login_required
from app.models.enseignant import (
    get_enseignants, get_enseignant_by_id,
    get_enseignements_enseignant,
    create_enseignant, update_enseignant, delete_enseignant,
)

enseignants_bp = Blueprint("enseignants", __name__, url_prefix="/enseignants")


@enseignants_bp.route("/")
@login_required
def index():
    page   = request.args.get("page", 1, type=int)
    search = request.args.get("search", "")
    enseignants, total, total_pages = get_enseignants(page, search)
    return render_template(
        "enseignants/index.html",
        enseignants=enseignants, total=total,
        total_pages=total_pages, page=page, search=search,
    )


@enseignants_bp.route("/<int:enseignant_id>")
@login_required
def detail(enseignant_id):
    enseignant    = get_enseignant_by_id(enseignant_id)
    if not enseignant:
        flash("Enseignant introuvable.", "danger")
        return redirect(url_for("enseignants.index"))
    enseignements = get_enseignements_enseignant(enseignant_id)
    return render_template(
        "enseignants/detail.html",
        enseignant=enseignant, enseignements=enseignements,
    )


@enseignants_bp.route("/ajouter", methods=["GET", "POST"])
@login_required
def ajouter():
    if request.method == "POST":
        nom          = request.form.get("nom", "").strip()
        prenom       = request.form.get("prenom", "").strip()
        grade        = request.form.get("grade", "").strip()
        email        = request.form.get("email", "").strip()
        mot_de_passe = request.form.get("mot_de_passe", "").strip()

        if not all([nom, prenom, grade, email, mot_de_passe]):
            flash("Tous les champs sont obligatoires.", "danger")
            return render_template("enseignants/form.html", enseignant=None, action="Ajouter")

        try:
            create_enseignant(nom, prenom, grade, email, mot_de_passe)
            flash(f"Enseignant {nom} {prenom} ajouté.", "success")
            return redirect(url_for("enseignants.index"))
        except Exception as e:
            flash(f"Erreur : {e}", "danger")

    return render_template("enseignants/form.html", enseignant=None, action="Ajouter")


@enseignants_bp.route("/modifier/<int:enseignant_id>", methods=["GET", "POST"])
@login_required
def modifier(enseignant_id):
    enseignant = get_enseignant_by_id(enseignant_id)
    if not enseignant:
        flash("Enseignant introuvable.", "danger")
        return redirect(url_for("enseignants.index"))

    if request.method == "POST":
        nom    = request.form.get("nom", "").strip()
        prenom = request.form.get("prenom", "").strip()
        grade  = request.form.get("grade", "").strip()
        email  = request.form.get("email", "").strip()

        try:
            update_enseignant(enseignant_id, nom, prenom, grade,
                              email, enseignant["id_utilisateur"])
            flash("Enseignant mis à jour.", "success")
            return redirect(url_for("enseignants.detail", enseignant_id=enseignant_id))
        except Exception as e:
            flash(f"Erreur : {e}", "danger")

    return render_template("enseignants/form.html", enseignant=enseignant, action="Modifier")


@enseignants_bp.route("/supprimer/<int:enseignant_id>", methods=["POST"])
@login_required
def supprimer(enseignant_id):
    try:
        delete_enseignant(enseignant_id)
        flash("Enseignant supprimé.", "success")
    except Exception as e:
        flash(f"Erreur : {e}", "danger")
    return redirect(url_for("enseignants.index"))
