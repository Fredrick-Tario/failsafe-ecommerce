import os
import time

from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import httpx

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    Request,
    status,
)

from fastapi.responses import JSONResponse

from pydantic import BaseModel, Field

from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db

from app.models import (
    Order as OrderModel,
    OrderItem as OrderItemModel,
)

from app.errors import ServiceError
from app.logging_config import configure_logging


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logger = configure_logging()


# --------------------------------------------------
# APPLICATION
# --------------------------------------------------

app = FastAPI(
    title="FailSafe Order Service",
    version="0.1.0",
)


# --------------------------------------------------
# DOWNSTREAM SERVICE CONFIGURATION
# --------------------------------------------------

INVENTORY_URL = os.getenv(
    "INVENTORY_URL",
    "http://127.0.0.1:8003",
)

PAYMENT_URL = os.getenv(
    "PAYMENT_URL",
    "http://127.0.0.1:8005",
)

DOWNSTREAM_TIMEOUT_SECONDS = 2.0


# --------------------------------------------------
# PYDANTIC SCHEMAS
# --------------------------------------------------

class OrderItemRequest(BaseModel):
    product_id: int

    quantity: int = Field(
        gt=0,
        le=20,
    )

    unit_price: Decimal = Field(
        gt=0,
        decimal_places=2,
    )


class OrderCreate(BaseModel):
    customer_id: str = Field(
        min_length=1,
        max_length=64,
    )

    items: list[OrderItemRequest] = Field(
        min_length=1,
        max_length=10,
    )


class Order(BaseModel):
    id: str
    customer_id: str
    items: list[OrderItemRequest]
    total_amount: Decimal
    status: str
    created_at: datetime


# --------------------------------------------------
# DOWNSTREAM: INVENTORY
# --------------------------------------------------

def reserve_inventory(
    item: OrderItemRequest,
) -> None:

    with httpx.Client(
        timeout=DOWNSTREAM_TIMEOUT_SECONDS
    ) as client:

        response = client.post(
            f"{INVENTORY_URL}/inventory/reserve",
            json={
                "product_id": item.product_id,
                "quantity": item.quantity,
            },
        )

        response.raise_for_status()


# --------------------------------------------------
# DOWNSTREAM: PAYMENT
# --------------------------------------------------

def authorize_payment(
    order_id: str,
    amount: Decimal,
) -> str:

    with httpx.Client(
        timeout=DOWNSTREAM_TIMEOUT_SECONDS
    ) as client:

        response = client.post(
            f"{PAYMENT_URL}/payments/authorize",
            json={
                "order_id": order_id,
                "amount": str(amount),
                "payment_method": "TEST",
            },
        )

        response.raise_for_status()

        return response.json()["status"]


# --------------------------------------------------
# HEALTH
# --------------------------------------------------

@app.get("/health")
def health() -> dict:

    return {
        "status": "healthy",
        "service": "order-service",
    }


# --------------------------------------------------
# READINESS
# --------------------------------------------------

@app.get("/ready")
def ready(
    db: Session = Depends(get_db),
) -> dict:

    try:
        db.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "service": "order-service",
            "database": "connected",
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )


# --------------------------------------------------
# CREATE ORDER
# --------------------------------------------------

@app.post(
    "/orders",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
) -> Order:

    total = sum(
        (
            item.quantity * item.unit_price
            for item in payload.items
        ),
        Decimal("0.00"),
    )

    order_id = str(uuid4())

    # ----------------------------------------------
    # STEP 1: RESERVE INVENTORY
    # ----------------------------------------------

    try:

        for item in payload.items:
            reserve_inventory(item)

        # ------------------------------------------
        # STEP 2: AUTHORIZE PAYMENT
        # ------------------------------------------

        payment_status = authorize_payment(
            order_id,
            total,
        )

    except httpx.HTTPStatusError as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Downstream service rejected request: "
                f"{exc.response.status_code}"
            ),
        ) from exc

    except httpx.RequestError as exc:

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Required downstream service unavailable"
            ),
        ) from exc


    # ----------------------------------------------
    # STEP 3: DETERMINE ORDER STATUS
    # ----------------------------------------------

    final_status = (
        "CONFIRMED"
        if payment_status == "APPROVED"
        else "PAYMENT_DECLINED"
    )

    created_at = datetime.now(timezone.utc)


    # ----------------------------------------------
    # STEP 4: CREATE ORDER DATABASE RECORD
    # ----------------------------------------------

    db_order = OrderModel(
        id=order_id,
        customer_id=payload.customer_id,
        total_amount=total,
        status=final_status,
        created_at=created_at,
    )

    db.add(db_order)


    # ----------------------------------------------
    # STEP 5: CREATE ORDER ITEM RECORDS
    # ----------------------------------------------

    db_items = []

    for item in payload.items:

        db_item = OrderItemModel(
            order_id=order_id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )

        db_items.append(db_item)

    db.add_all(db_items)


    # ----------------------------------------------
    # STEP 6: SAVE EVERYTHING
    # ----------------------------------------------

    try:

        db.commit()

    except SQLAlchemyError:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save order",
        )


    # ----------------------------------------------
    # STEP 7: RETURN API RESPONSE
    # ----------------------------------------------

    return Order(
        id=order_id,
        customer_id=payload.customer_id,
        items=payload.items,
        total_amount=total,
        status=final_status,
        created_at=created_at,
    )


# --------------------------------------------------
# GET ORDER
# --------------------------------------------------

@app.get(
    "/orders/{order_id}",
    response_model=Order,
)
def get_order(
    order_id: str,
    db: Session = Depends(get_db),
) -> Order:

    db_order = db.get(
        OrderModel,
        order_id,
    )

    if not db_order:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )


    # ----------------------------------------------
    # QUERY ORDER ITEMS
    # ----------------------------------------------

    statement = select(
        OrderItemModel
    ).where(
        OrderItemModel.order_id == order_id
    )

    db_items = db.scalars(
        statement
    ).all()


    # ----------------------------------------------
    # CONVERT ORM ITEMS TO API RESPONSE
    # ----------------------------------------------

    items = [
        OrderItemRequest(
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )
        for item in db_items
    ]


    return Order(
        id=db_order.id,
        customer_id=db_order.customer_id,
        items=items,
        total_amount=db_order.total_amount,
        status=db_order.status,
        created_at=db_order.created_at,
    )


# --------------------------------------------------
# SERVICE ERROR HANDLER
# --------------------------------------------------

@app.exception_handler(ServiceError)
async def service_error_handler(
    request: Request,
    exc: ServiceError,
) -> JSONResponse:

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "service": "order-service",
            "path": request.url.path,
        },
    )


# --------------------------------------------------
# REQUEST LOGGING MIDDLEWARE
# --------------------------------------------------

@app.middleware("http")
async def request_logging(
    request: Request,
    call_next,
):

    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid4()),
    )

    started = time.perf_counter()

    response = await call_next(request)

    duration_ms = (
        time.perf_counter() - started
    ) * 1000

    response.headers[
        "X-Request-ID"
    ] = request_id

    logger.info(
        (
            "request_id=%s "
            "method=%s "
            "path=%s "
            "status=%s "
            "duration_ms=%.2f"
        ),
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response