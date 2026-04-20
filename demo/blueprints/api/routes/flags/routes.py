from flask import request

from .....extensions import get_session
from .....lib.exceptions import APIException
from .....lib.rest import APIResponse
from .....services.feature_flag import FeatureFlagService
from ... import api_blueprint


@api_blueprint.post("/flags")
def create_flag():
    service = FeatureFlagService(get_session())
    data = request.get_json()

    flag = service.create_flag(
        name=data["name"],
        environment=data.get("environment", "dev"),
        description=data.get("description"),
    )

    response = {
        "id": flag.id,
        "name": flag.name,
        "enabled": flag.enabled,
        "environment": flag.environment,
    }
    return APIResponse.success(data=response, status_code=201)


@api_blueprint.get("/flags")
def list_flags():
    service = FeatureFlagService(get_session())
    environment = request.args.get("environment", "")
    flags = service.list_flags(environment)

    response = [f.to_dict() for f in flags]

    return APIResponse.success(data=response)


@api_blueprint.get("/flags/<int:flag_id>")
def get_flag(flag_id):
    service = FeatureFlagService(get_session())
    flag = service.get_flag(flag_id)

    if not flag:
        raise APIException(f"Flag with id '{flag_id}' not found", 404)

    response = {
        "id": flag.id,
        "name": flag.name,
        "enabled": flag.enabled,
    }
    return APIResponse.success(data=response)


@api_blueprint.post("/flags/<int:flag_id>/toggle")
def toggle_flag(flag_id):
    service = FeatureFlagService(get_session())
    flag = service.toggle_flag(flag_id)

    response = {"enabled": flag.enabled}
    return APIResponse.success(data=response)


@api_blueprint.patch("/flags/<int:flag_id>")
def update_flag(flag_id: int):
    service = FeatureFlagService(get_session())

    data = request.get_json()

    if not data:
        raise APIException("No data provided", 400)

    flag = service.update_flag(flag_id, data)

    return APIResponse.success(
        data=flag.to_dict(),
        message="Data updated successfully",
    )


@api_blueprint.delete("/flags/<int:flag_id>")
def delete_flag(flag_id: int):
    service = FeatureFlagService(get_session())

    service.delete_flag(flag_id)

    return APIResponse.success(status_code=204)


@api_blueprint.get("/flags/public")
def list_public_flags():
    service = FeatureFlagService(get_session())
    flags = service.list_public_flags()

    response = [f.to_dict() for f in flags]
    return APIResponse.success(data=response)
