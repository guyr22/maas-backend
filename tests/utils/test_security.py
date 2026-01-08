import pytest
from cryptography.fernet import InvalidToken

from utils.security import SecurityManager


def test_encryption_decryption():
    key = "Tl9K-DqB_FvT_Hw-yQoyZzJz_ZzJz_ZzJz_ZzJz_ZzI="
    manager = SecurityManager(key)
    original_text = "secret message"
    encrypted = manager.encrypt(original_text)

    assert encrypted != original_text
    assert manager.decrypt(encrypted) == original_text


def test_decrypt_invalid_token_raises_error():
    key = "Tl9K-DqB_FvT_Hw-yQoyZzJz_ZzJz_ZzJz_ZzJz_ZzI="
    manager = SecurityManager(key)

    with pytest.raises(InvalidToken):
        manager.decrypt("invalid-token-data")
