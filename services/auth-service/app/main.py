from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User as UserModel
from app.schemas import Token, UserCreate, UserPublic
from app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

app = FastAPI(
    title="FailSafe Auth Service",
    version="0.1.0",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------


@app.get("/health")
def health() -> dict:
    """
    Checks whether the application process itself is running.

    This does NOT check PostgreSQL.
    """
    return {
        "status": "healthy",
        "service": "auth-service",
    }


# --------------------------------------------------
# READINESS CHECK
# --------------------------------------------------


@app.get("/ready")
def ready(db: Session = Depends(get_db)) -> dict:
    """
    Checks whether the Auth Service can communicate
    with PostgreSQL.
    """
    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "service": "auth-service",
            "database": "connected",
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )


# --------------------------------------------------
# REGISTER
# --------------------------------------------------


@app.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db),
) -> UserPublic:

    existing_user = db.scalar(select(UserModel).where(UserModel.username == user.username))

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    new_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserPublic(
        username=new_user.username,
        email=new_user.email,
    )


# --------------------------------------------------
# LOGIN / TOKEN
# --------------------------------------------------


@app.post("/token", response_model=Token)
def login(
    form: Annotated[
        OAuth2PasswordRequestForm,
        Depends(),
    ],
    db: Session = Depends(get_db),
) -> Token:

    user = db.scalar(select(UserModel).where(UserModel.username == form.username))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(
        form.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.username)

    return Token(access_token=access_token)


# --------------------------------------------------
# CURRENT USER
# --------------------------------------------------


@app.get(
    "/users/me",
    response_model=UserPublic,
)
def current_user(
    token: Annotated[
        str,
        Depends(oauth2_scheme),
    ],
    db: Session = Depends(get_db),
) -> UserPublic:

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)

        username = payload.get("sub")

        if not username:
            raise credentials_error

    except InvalidTokenError:
        raise credentials_error

    user = db.scalar(select(UserModel).where(UserModel.username == username))

    if not user:
        raise credentials_error

    return UserPublic(
        username=user.username,
        email=user.email,
    )
