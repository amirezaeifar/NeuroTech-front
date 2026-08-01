from __future__ import annotations

from typing import Any

from flask import jsonify


def success_response(
    data: Any = None,
    *,
    message: str | None = None,
    meta: dict[str, Any] | None = None,
    status: int = 200,
):
    return (
        jsonify({"success": True, "data": data, "message": message, "meta": meta or {}}),
        status,
    )


def error_response(
    message: str,
    *,
    errors: dict[str, Any] | None = None,
    status: int = 400,
):
    payload: dict[str, Any] = {
        "success": False,
        "data": None,
        "message": message,
        "errors": errors or {},
    }
    return jsonify(payload), status
