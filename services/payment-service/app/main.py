from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Payment as PaymentModel


app = FastAPI(
    title="FailSafe Payment Service",
    version="0.1.0",
)


# --------------------------------------------------
# PYDANTIC SCHEMAS
# --------------------------------------------------

class PaymentRequest(BaseModel):
    order_id: str = Field(
        min_length=10,
        max_length=64,
    )

    amount: Decimal = Field(
        gt=0,
        decimal_places=2,
    )

    payment_method: str = Field(
        default="TEST",
        pattern=r"^TEST$",
    )


class PaymentResult(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    payment_id: str
    order_id: str
    status: str
    amount: Decimal


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health() -> dict:
    return {
        "status": "healthy",
        "service": "payment-service",
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
            "service": "payment-service",
            "database": "connected",
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )


# --------------------------------------------------
# AUTHORIZE PAYMENT
# --------------------------------------------------

@app.post(
    "/payments/authorize",
    response_model=PaymentResult,
)
def authorize_payment(
    payload: PaymentRequest,
    db: Session = Depends(get_db),
) -> PaymentResult:

    payment_status = (
        "APPROVED"
        if payload.amount <= Decimal("50000.00")
        else "DECLINED"
    )

    payment_id = str(uuid4())

    payment = PaymentModel(
        payment_id=payment_id,
        order_id=payload.order_id,
        amount=payload.amount,
        payment_method=payload.payment_method,
        status=payment_status,
        created_at=datetime.now(timezone.utc),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return PaymentResult(
        payment_id=payment.payment_id,
        order_id=payment.order_id,
        status=payment.status,
        amount=payment.amount,
    )