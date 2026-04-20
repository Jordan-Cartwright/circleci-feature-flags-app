from sqlalchemy import text

from demo.extensions import get_session
from demo.lib.rest import APIResponse

from ... import api_blueprint


@api_blueprint.get("/health/live")
def liveness():
    response = {"status": "alive"}
    return APIResponse.success(data=response)


@api_blueprint.get("/health/ready")
def readiness():
    try:
        session = get_session()
        session.execute(text("SELECT 1")).scalar_one()

        response = {"status": "ready"}
        return APIResponse.success(data=response)
    except Exception:
        return APIResponse.error("Database unavailable", 503)
