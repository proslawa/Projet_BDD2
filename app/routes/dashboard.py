from flask import Blueprint, render_template, session
from app.routes.auth import login_required
from app.models.stats import (
    get_stats_globales, get_stats_notes_par_matiere,
    get_distribution_notes, get_taux_presence_par_classe,
    get_repartition_par_filiere, get_notes_par_type_eval,
    get_stats_etudiant, get_stats_enseignant,
)
import json
from decimal import Decimal

dashboard_bp = Blueprint("dashboard", __name__)


def _json_default(value):
    """Conversion JSON pour types SQL non sérialisables nativement."""
    if isinstance(value, Decimal):
        return float(value)
    return str(value)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    role = session.get("user_role")
    pid  = session.get("user_profile_id")

    if role == "etudiant" and pid:
        stats  = get_stats_etudiant(pid)
        distrib = get_distribution_notes()  # distribution personnelle possible
        return render_template("dashboard/etudiant.html",
                               stats=stats,
                               distrib_json=json.dumps(distrib, default=_json_default))

    elif role == "enseignant" and pid:
        stats       = get_stats_enseignant(pid)
        par_matiere = get_stats_notes_par_matiere()
        return render_template("dashboard/enseignant.html",
                               stats=stats,
                               par_matiere_json=json.dumps(par_matiere, default=_json_default))

    else:  # admin
        stats        = get_stats_globales()
        par_matiere  = get_stats_notes_par_matiere()
        distrib      = get_distribution_notes()
        par_classe   = get_taux_presence_par_classe()
        par_filiere  = get_repartition_par_filiere()
        par_type     = get_notes_par_type_eval()
        return render_template("dashboard/admin.html",
                               stats=stats,
                               par_matiere_json=json.dumps(par_matiere, default=_json_default),
                               distrib_json=json.dumps(distrib, default=_json_default),
                               par_classe_json=json.dumps(par_classe, default=_json_default),
                               par_filiere_json=json.dumps(par_filiere, default=_json_default),
                               par_type_json=json.dumps(par_type, default=_json_default))
