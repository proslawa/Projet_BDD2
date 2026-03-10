from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app.models.auth import get_user_by_email

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Veuillez vous connecter.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Décorateur de contrôle d'accès par rôle."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                flash("Veuillez vous connecter.", "warning")
                return redirect(url_for("auth.login"))
            if session.get("user_role") not in roles:
                flash("Accès refusé. Vous n'avez pas les droits nécessaires.", "danger")
                return redirect(url_for("dashboard.index"))
            return f(*args, **kwargs)
        return decorated
    return decorator


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        pwd   = request.form.get("password", "").strip()

        if not email or not pwd:
            flash("Email et mot de passe requis.", "danger")
            return render_template("auth/login.html")

        user = get_user_by_email(email)

        if user and user["mot_de_passe"] == pwd:
            if not user["actif"]:
                flash("Compte désactivé. Contactez l'administrateur.", "danger")
                return render_template("auth/login.html")
            session["user_id"]    = user["id"]
            session["user_email"] = user["email"]
            session["user_role"]  = user["role"]
            # Stocker l'ID métier pour étudiant/enseignant
            session["user_profile_id"] = user.get("profile_id")
            flash(f"Bienvenue ! Connexion réussie.", "success")
            return redirect(url_for("dashboard.index"))

        flash("Email ou mot de passe incorrect.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Vous avez été déconnecté.", "info")
    return redirect(url_for("auth.login"))
