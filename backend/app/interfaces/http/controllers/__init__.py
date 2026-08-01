from app.interfaces.http.controllers.auth_controller import create_auth_blueprint
from app.interfaces.http.controllers.health_controller import create_health_blueprint

__all__ = ["create_auth_blueprint", "create_health_blueprint"]
