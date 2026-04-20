from flask import render_template

from . import ui_blueprint


@ui_blueprint.route("/")
def dashboard():
    return render_template("index.html")
