from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.product_service import ProductService
from ..schemas.product import ProductResponse, ProductListResponse

router = APIRouter(
    prefix="/api/products",
    tags=["products"]
)

@router.get("", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
def get_products(
    q: str | None = Query(default=None, min_length=1, max_length=100),
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return service.get_all_products(query=q)

@router.get("/category/{category_id}", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
def get_products_by_category(category_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_products_by_category(category_id)

@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_product_by_id(product_id)
