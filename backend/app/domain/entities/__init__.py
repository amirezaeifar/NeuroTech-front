"""Import every mapped class so Alembic receives complete metadata."""

from app.domain.entities.academy import *
from app.domain.entities.base import Base
from app.domain.entities.commerce import *
from app.domain.entities.content import *
from app.domain.entities.event import *
from app.domain.entities.media import *
from app.domain.entities.moderation import *
from app.domain.entities.partner import *
from app.domain.entities.product import *
from app.domain.entities.refresh_token import RefreshToken
from app.domain.entities.role import Role
from app.domain.entities.trade import *
from app.domain.entities.user import User
from app.domain.entities.user_role import UserRole

__all__ = ["Base", "User", "Role", "UserRole", "RefreshToken"]
