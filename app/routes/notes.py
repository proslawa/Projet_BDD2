from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from app.routes.auth import login_required, role_required
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


@notes_bp.route("/releves")
@role_required("admin")
def releves():
    etudiants = get_etudiants_liste()
    return render_template("notes/releves.html", etudiants=etudiants)


@notes_bp.route("/releve/<int:etudiant_id>/pdf")
@role_required("admin")
def releve_pdf(etudiant_id):
    from app.models.etudiant import get_etudiant_by_id
    etudiant = get_etudiant_by_id(etudiant_id)
    if not etudiant:
        flash("Étudiant introuvable.", "danger")
        return redirect(url_for("notes.releves"))

    releve_data = get_releve_notes(etudiant_id)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    story = []

    logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "image", "ensae.png")
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=80, height=80))
        story.append(Spacer(1, 8))

    story.append(Paragraph("Releves ENSAE", styles["Title"]))
    story.append(Paragraph(f"Etudiant : {etudiant['nom']} {etudiant['prenom']}", styles["Normal"]))
    story.append(Paragraph(f"Matricule : {etudiant['matricule']}", styles["Normal"]))
    story.append(Spacer(1, 12))

    if not releve_data:
        story.append(Paragraph("Aucune note enregistrée pour cet étudiant.", styles["Normal"]))
    else:
        for ue in releve_data:
            story.append(Paragraph(f"UE : {ue['ue']} — {ue['credit']} crédit(s)", styles["Heading3"]))

            data = [["Matière", "Coeff.", "Moyenne matière", "Appréciation"]]
            for m in ue["matieres"]:
                moyenne = m["moyenne"]
                if moyenne >= 16:
                    appr = "Très Bien"
                elif moyenne >= 14:
                    appr = "Bien"
                elif moyenne >= 12:
                    appr = "Assez Bien"
                elif moyenne >= 10:
                    appr = "Passable"
                else:
                    appr = "Insuffisant"

                data.append([m["nom"], str(m["coeff"]), f"{moyenne:.2f}", appr])

            table = Table(data, hAlign="LEFT", colWidths=[220, 60, 90, 120])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 1), (2, -1), "CENTER"),
            ]))
            story.append(table)
            story.append(Spacer(1, 12))

    date_str = datetime.now().strftime("%d/%m/%Y")
    story.append(Spacer(1, 18))
    story.append(Paragraph(f"Dakar, {date_str}", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    filename = f"releve_{etudiant['matricule']}.pdf"
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)
