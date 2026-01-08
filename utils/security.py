from cryptography.fernet import Fernet

from config import config


class SecurityManager:
    def __init__(self, key: str):
        print(key)
        self._cypher_suite = Fernet(key.encode())

    def encrypt(self, plain_text: str) -> str:
        return self._cypher_suite.encrypt(plain_text.encode()).decode()

    def decrypt(self, cipher_text: str) -> str:
        return self._cypher_suite.decrypt(cipher_text.encode()).decode()


security_manager = SecurityManager(config["security"]["secret_key"])
