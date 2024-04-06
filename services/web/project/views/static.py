# static.py
from flask import Blueprint, send_from_directory
from flask_login import login_required
from project import app


bp = Blueprint("static", __name__)


@bp.route("/static/<path:filename>")
@login_required
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@bp.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)
