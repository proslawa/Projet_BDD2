from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.routes.auth import login_required
from app.models.note import (
    get_notes, get_matieres, get_evaluations,
    upsert_note, delete_note,
    create_evaluation, get_releve_notes,
)
from app.models.inscription import get_etudiants_liste

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")


@notes_bp.route("/")
@login_required
def index():
    page          = request.args.get("page", 1, type=int)
    search        = request.args.get("search", "")
    evaluation_id = request.args.get("evaluation_id", "")
    matiere_id    = request.args.get("matiere_id", "")
    matieres      = get_matieres()
    evaluations   = get_evaluations(matiere_id)
    notes, total, total_pages = get_notes(page, search, evaluation_id, matiere_id)
    return render_template(
        "notes/index.html",
        notes=notes, total=total, total_pages=total_pages, page=page,
        search=search, evaluation_id=evaluation_id, matiere_id=matiere_id,
        matieres=matieres, evaluations=evaluations,
    )


@notes_bp.route("/saisir", methods=["GET", "POST"])
@login_required
def saisir():
    matieres    = get_matieres()
    evaluations = get_evaluations()
    etudiants   = get_etudiants_liste()

    if request.method == "POST":
        id_etudiant   = request.form.get("id_etudiant")
        id_evaluation = request.form.get("id_evaluation")
        note_val      = request.form.get("note", "").strip()

        if not all([id_etudiant, id_evaluation, note_val]):
            flash("Tous les champs sont requis.", "danger")
        else:
            try:
                note_float = float(note_val)
                if not (0 <= note_float <= 20):
                    raise ValueError("Note hors de [0, 20]")
                upsert_note(int(id_etudiant), int(id_evaluation), note_float)
                flash("Note enregistrée.", "success")
                return redirect(url_for("notes.index"))
            except ValueError as e:
                flash(f"Note invalide : {e}", "danger")
            except Exception as e:
                flash(f"Erreur : {e}", "danger")

    return render_template("notes/form.html",
                           matieres=matieres, evaluations=evaluations, etudiants=etudiants)


@notes_bp.route("/supprimer/<int:id_etudiant>/<int:id_evaluation>", methods=["POST"])
@login_required
def supprimer(id_etudiant, id_evaluation):
    try:
        delete_note(id_etudiant, id_evaluation)
        flash("Note supprimée.", "success")
    except Exception as e:
        flash(f"Erreur : {e}", "danger")
    return redirect(url_for("notes.index"))


@notes_bp.route("/evaluation/ajouter", methods=["GET", "POST"])
@login_required
def ajouter_evaluation():
    matieres = get_matieres()
    if request.method == "POST":
        id_matiere  = request.form.get("id_matiere")
        type_eval   = request.form.get("type_evaluation", "").strip()
        date_eval   = request.form.get("date_evaluation", "").strip()
        if not all([id_matiere, type_eval, date_eval]):
            flash("Tous les champs sont requis.", "danger")
        else:
            try:
                create_evaluation(int(id_matiere), type_eval, date_eval)
                flash("Évaluation créée.", "success")
                return redirect(url_for("notes.index"))
            except Exception as e:
                flash(f"Erreur : {e}", "danger")
    return render_template("notes/evaluation_form.html", matieres=matieres)


@notes_bp.route("/releve/<int:etudiant_id>")
@login_required
def releve(etudiant_id):
    from app.models.etudiant import get_etudiant_by_id
    etudiant = get_etudiant_by_id(etudiant_id)
    if not etudiant:
        flash("Étudiant introuvable.", "danger")
        return redirect(url_for("notes.index"))
    releve_data = get_releve_notes(etudiant_id)
    return render_template("notes/releve.html", etudiant=etudiant, releve=releve_data)
