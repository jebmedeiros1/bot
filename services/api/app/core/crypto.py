import os
from base64 import b64decode, b64encode
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.core.config import settings


def _build_key() -> bytes:
    key = settings.secret_key.encode()
    if len(key) < 32:
        key = key.ljust(32, b"0")
    return key[:32]


def encrypt_secret(value: str) -> str:
    key = _build_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, value.encode(), None)
    return b64encode(nonce + ciphertext).decode()


def decrypt_secret(value: str) -> str:
    key = _build_key()
    raw = b64decode(value.encode())
    nonce, ciphertext = raw[:12], raw[12:]
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode()


def mask_secret(value: str) -> str:
    visible = 4
    if len(value) <= visible:
        return "*" * len(value)
    return f"{'*' * (len(value) - visible)}{value[-visible:]}"
