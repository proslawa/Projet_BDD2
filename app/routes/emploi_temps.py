from flask import Blueprint, render_template, request, session
from app.routes.auth import login_required
from app.models.emploi_temps import (
    get_emploi_temps_classe, get_emploi_temps_enseignant,
    get_emploi_temps_etudiant, get_classes_liste,
)
import json

emploi_temps_bp = Blueprint("emploi_temps", __name__, url_prefix="/emploi-temps")


@emploi_temps_bp.route("/")
@login_required
def index():
    role     = session.get("user_role")
    pid      = session.get("user_profile_id")
    classes  = get_classes_liste()
    classe_id = request.args.get("classe_id", "")

    if role == "etudiant" and pid:
        seances = get_emploi_temps_etudiant(pid)
    elif role == "enseignant" and pid:
        seances = get_emploi_temps_enseignant(pid)
    else:
        seances = get_emploi_temps_classe(classe_id if classe_id else None)

    # Organiser par semaine
    semaines = organiser_par_semaine(seances)

    return render_template("emploi_temps/index.html",
                           seances=seances,
                           semaines_json=json.dumps(semaines, default=str),
                           classes=classes,
                           classe_id=classe_id,
                           role=role)


def organiser_par_semaine(seances):
    """Organise les séances pour l'affichage calendrier."""
    from collections import defaultdict
    semaines = defaultdict(lambda: {
        "Lundi": [], "Mardi": [], "Mercredi": [],
        "Jeudi": [], "Vendredi": [], "Samedi": []
    })
    jours_fr = {
        "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
        "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi",
        "Sunday": "Dimanche"
    }
    for s in seances:
        if s["date"]:
            from datetime import date, timedelta
            d = s["date"] if hasattr(s["date"], "isocalendar") else s["date"]
            if hasattr(d, "isocalendar"):
                iso = d.isocalendar()
                semaine_key = f"{iso[0]}-S{iso[1]:02d}"
                # Debut de semaine (lundi)
                lundi = d - timedelta(days=d.weekday())
                semaine_label = f"Semaine du {lundi.strftime('%d/%m/%Y')}"
                jour_fr = jours_fr.get(d.strftime("%A"), d.strftime("%A"))
                if semaine_key not in semaines:
                    semaines[semaine_key] = {
                        "label": semaine_label,
                        "jours": {j: [] for j in ["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"]}
                    }
                if jour_fr in semaines[semaine_key]["jours"]:
                    semaines[semaine_key]["jours"][jour_fr].append({
                        "id": s["id"],
                        "debut": s["debut"],
                        "fin": s["fin"],
                        "matiere": s["matiere"],
                        "classe": s.get("classe", ""),
                        "enseignant": s.get("enseignant", ""),
                    })
    return dict(semaines)
