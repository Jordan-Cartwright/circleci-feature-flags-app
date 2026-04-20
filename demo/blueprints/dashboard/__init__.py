from flask import Blueprint

# Create the Blueprint
ui_blueprint = Blueprint(
    "ui",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/dashboard/static",
)

# Import all route definitions so Flask sees them
from . import routes

# Prevent linters from removing them
_ = routes
