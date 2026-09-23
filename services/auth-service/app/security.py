import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

SECRET_KEY = os.environ["AUTH_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
password_hash = PasswordHash.recommended()


# Converts a plain-text password into a secure hash for storage.
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# Checks whether a plain-text password matches its stored password hash.
def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


# Creates a signed JWT access token for a user with a configured expiration time.
def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {"sub": subject, "exp": expire}

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# Validates and decodes a JWT access token into its payload.
def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
