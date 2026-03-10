import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask, redirect, url_for, send_from_directory
import config as cfg


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = cfg.SECRET_KEY

    from app.routes.auth          import auth_bp
    from app.routes.dashboard     import dashboard_bp
    from app.routes.etudiants     import etudiants_bp
    from app.routes.enseignants   import enseignants_bp
    from app.routes.inscriptions  import inscriptions_bp
    from app.routes.notes         import notes_bp
    from app.routes.presences     import presences_bp
    from app.routes.seances       import seances_bp
    from app.routes.emploi_temps  import emploi_temps_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(etudiants_bp)
    app.register_blueprint(enseignants_bp)
    app.register_blueprint(inscriptions_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(presences_bp)
    app.register_blueprint(seances_bp)
    app.register_blueprint(emploi_temps_bp)

    @app.route("/image/<path:filename>")
    def image_file(filename):
        image_dir = os.path.join(os.path.dirname(__file__), "..", "image")
        return send_from_directory(image_dir, filename)

    @app.route("/")
    def root():
        return redirect(url_for("dashboard.index"))

    return app
