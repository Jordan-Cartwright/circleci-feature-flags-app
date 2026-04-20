from flask import Blueprint, jsonify
from sqlalchemy.exc import SQLAlchemyError

from ...lib.exceptions import (
    APIException,
    DuplicateFeatureFlagError,
    FeatureFlagNotFoundError,
)
from ...lib.rest import APIResponse

# Create the Blueprint
api_blueprint = Blueprint(
    "api",
    __name__,
    url_prefix="/api/v1",
)


@api_blueprint.errorhandler(Exception)
def generic_error(e):
    return jsonify({"error": "unexpected error"}), 500


@api_blueprint.errorhandler(404)
def api_not_found(err):
    """Handle 404 errors for the API routes"""
    return jsonify({"error": "Resource not found", "status": 404}), 404


@api_blueprint.errorhandler(400)
def api_bad_request(error):
    """Handle 400 errors for API routes"""
    return jsonify({"error": "Bad request", "message": str(error.description), "status": 400}), 400


@api_blueprint.errorhandler(500)
def api_server_error(error):
    """Handle 500 errors for API routes"""
    return jsonify({"error": "Internal server error", "status": 500}), 500


@api_blueprint.errorhandler(SQLAlchemyError)
def db_error(e):
    return jsonify({"error": "DB failure"}), 500


@api_blueprint.errorhandler(APIException)
def handle_api_exception(err: APIException):
    return APIResponse.error(
        message=err.message,
        code=err.code,
    )


@api_blueprint.errorhandler(FeatureFlagNotFoundError)
def feature_flag_not_found_error(err: FeatureFlagNotFoundError):
    return APIResponse.error(
        message=str(err),
        code=404,
    )


@api_blueprint.errorhandler(DuplicateFeatureFlagError)
def duplicate_feature_flag_error(err):
    response = {
        "error": {
            "code": "DUPLICATE_FEATURE_FLAG_ERROR",
            "message": str(err),
            "flag_id": err.flag_id,
            "name": err.name,
        }
    }
    return response, 404


# Import all route definitions so Flask sees them
from .routes.flags import routes
from .routes.health import routes

# Prevent linters from removing them
_ = routes
