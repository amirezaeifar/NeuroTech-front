from flask import Blueprint

from app.core.config import Settings
from app.core.responses import success_response
from app.domain.services.health_service import HealthService


def create_health_blueprint(health_service: HealthService, settings: Settings) -> Blueprint:
    blueprint = Blueprint("health", __name__)

    @blueprint.get("/health")
    def health():
        dependencies = health_service.check()
        healthy = all(value == "ok" for value in dependencies.values())
        payload = {
            "app": settings.app_name,
            "status": "ok" if healthy else "degraded",
            "environment": settings.environment,
            "dependencies": dependencies,
        }
        return success_response(payload, status=200 if healthy else 503)

    return blueprint
