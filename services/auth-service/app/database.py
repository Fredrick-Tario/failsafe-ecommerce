import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Load the .env file belonging to this service.
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(ENV_FILE)

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


# Creates and safely closes a database session for each API request.
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
        
# for dir in services/inventory-service/app services/order-service/app services/payment-service/app services/product-service/app; do
#     cp services/auth-service/app/database.py "$dir/"
# done
