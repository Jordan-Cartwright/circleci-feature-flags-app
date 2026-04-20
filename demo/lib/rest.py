from __future__ import annotations

from typing import Any, Dict, Optional

from flask import Response, jsonify


class APIResponse:
    """
    Standardized JSON API response builder.
    """

    @staticmethod
    def success(
        data: Optional[Any] = None,
        message: Optional[str] = None,
        status_code: int = 200,
    ) -> Response:
        payload: Dict[str, Any] = {
            "status": "success",
            "data": data if data is not None else {},
        }

        if message:
            payload["message"] = message

        return respond(status_code, payload)

    @staticmethod
    def error(
        message: str,
        code: int = 400,
        status_code: Optional[int] = None,
    ) -> Response:
        """
        code: logical error code returned in JSON body
        status_code: actual HTTP status code (defaults to same as code)
        """
        status_code = status_code or code

        payload = {
            "status": "error",
            "error": {
                "code": code,
                "message": message,
            },
        }

        return respond(status_code, payload)


def respond(status_code: Any, payload: dict) -> Response:
    response = jsonify(payload)
    response.status_code = status_code
    return response
