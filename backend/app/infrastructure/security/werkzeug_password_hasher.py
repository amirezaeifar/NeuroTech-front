from werkzeug.security import check_password_hash, generate_password_hash

from app.domain.ports.password_hasher import PasswordHasher


class WerkzeugPasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return generate_password_hash(password, method="scrypt")

    def verify(self, password_hash: str, password: str) -> bool:
        try:
            return check_password_hash(password_hash, password)
        except (TypeError, ValueError):
            return False
