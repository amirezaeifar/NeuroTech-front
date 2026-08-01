from cryptography.fernet import Fernet, InvalidToken

from app.domain.ports.secret_encryptor import SecretEncryptor


class FernetSecretEncryptor(SecretEncryptor):
    def __init__(self, key: str) -> None:
        self._fernet = Fernet(key.encode("ascii"))

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("ascii")

    def decrypt(self, ciphertext: str) -> str:
        try:
            return self._fernet.decrypt(ciphertext.encode("ascii")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Encrypted value could not be decrypted.") from exc
