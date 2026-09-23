from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import InventoryItem as InventoryModel

app = FastAPI(
    title="FailSafe Inventory Service",
    version="0.1.0",
)


# --------------------------------------------------
# PYDANTIC SCHEMAS
# --------------------------------------------------


class InventoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: int

    available: int = Field(ge=0)

    reserved: int = Field(ge=0)


class ReservationRequest(BaseModel):
    product_id: int = Field(gt=0)

    quantity: int = Field(
        gt=0,
        le=100,
    )


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------


@app.get("/health")
def health() -> dict:
    return {
        "status": "healthy",
        "service": "inventory-service",
    }


# --------------------------------------------------
# READINESS CHECK
# --------------------------------------------------


@app.get("/ready")
def ready(
    db: Session = Depends(get_db),
) -> dict:

    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "service": "inventory-service",
            "database": "connected",
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )


# --------------------------------------------------
# GET INVENTORY
# --------------------------------------------------


@app.get(
    "/inventory/{product_id}",
    response_model=InventoryItem,
)
def get_inventory(
    product_id: int,
    db: Session = Depends(get_db),
) -> InventoryModel:

    item = db.scalar(select(InventoryModel).where(InventoryModel.product_id == product_id))

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found",
        )

    return item


# --------------------------------------------------
# RESERVE INVENTORY
# --------------------------------------------------


@app.post(
    "/inventory/reserve",
    response_model=InventoryItem,
)
def reserve_stock(
    payload: ReservationRequest,
    db: Session = Depends(get_db),
) -> InventoryModel:

    item = db.scalar(select(InventoryModel).where(InventoryModel.product_id == payload.product_id))

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found",
        )

    if item.available < payload.quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Insufficient stock",
        )

    item.available -= payload.quantity
    item.reserved += payload.quantity

    db.commit()
    db.refresh(item)

    return item
