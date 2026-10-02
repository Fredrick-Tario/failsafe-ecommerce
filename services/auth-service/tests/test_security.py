import os

os.environ.setdefault("AUTH_SECRET_KEY", "test-secret-key")

from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    password = "FailSafe123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True


def test_wrong_password_is_rejected():
    hashed = hash_password("CorrectPass")

    assert verify_password("WrongPass", hashed) is False


def test_access_token_contains_subject():
    token = create_access_token("fred-test")
    payload = decode_access_token(token)

    assert payload["sub"] == "fred-test"