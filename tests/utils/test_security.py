from utils.security import SecurityManager


def test_encryption_decryption():
    key = "BTzc1lV49sN6hmpQpUDIIKyZz-a5wwEskY_fsi6kGEDk="
    manager = SecurityManager(key)
    original_text = "secret message"
    encrypted = manager.encrypt(original_text)

    assert encrypted != original_text
    assert manager.decrypt(encrypted) == original_text


def test_decrypt_invalid_token_raises_error():
    # Example of what else we could test, but let's stick to the basics first
    pass
