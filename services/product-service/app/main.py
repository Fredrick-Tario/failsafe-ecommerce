from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product as ProductModel

app = FastAPI(
    title="FailSafe Product Service",
    version="0.1.0",
)


# --------------------------------------------------
# PYDANTIC SCHEMAS
# --------------------------------------------------


class ProductCreate(BaseModel):
    sku: str = Field(
        min_length=3,
        max_length=40,
    )

    name: str = Field(
        min_length=2,
        max_length=120,
    )

    price: Decimal = Field(
        gt=0,
        decimal_places=2,
    )


class Product(ProductCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool = True


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------


@app.get("/health")
def health() -> dict:
    return {
        "status": "healthy",
        "service": "product-service",
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
            "service": "product-service",
            "database": "connected",
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )


# --------------------------------------------------
# LIST PRODUCTS
# --------------------------------------------------


@app.get(
    "/products",
    response_model=list[Product],
)
def list_products(
    db: Session = Depends(get_db),
) -> list[ProductModel]:

    statement = select(ProductModel).order_by(ProductModel.id)

    products = db.scalars(statement).all()

    return list(products)


# --------------------------------------------------
# GET PRODUCT
# --------------------------------------------------


@app.get(
    "/products/{product_id}",
    response_model=Product,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductModel:

    product = db.get(
        ProductModel,
        product_id,
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return product


# --------------------------------------------------
# CREATE PRODUCT
# --------------------------------------------------


@app.post(
    "/products",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
) -> ProductModel:

    existing_product = db.scalar(select(ProductModel).where(ProductModel.sku == payload.sku))

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists.",
        )

    product = ProductModel(
        sku=payload.sku,
        name=payload.name,
        price=payload.price,
        active=True,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product
