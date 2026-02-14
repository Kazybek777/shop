from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .category import CategoryResponse


class ProductBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., gt=0, description="Product price (must be greater than 0)")
    category_id: int = Field(..., description="Category id")
    image_url: Optional[str] = Field(None, description="Product image url")


class ProductCreate(ProductBase):
    pass


class ProductResponse(BaseModel):
    id: int = Field(..., description="Unique product id")
    name: str
    name_ru: Optional[str] = None
    name_en: Optional[str] = None
    description: Optional[str]
    description_ru: Optional[str] = None
    description_en: Optional[str] = None
    price: float
    category_id: int
    image_url: Optional[str]
    images: list[str] = Field(default_factory=list, description="All product image urls")
    created_at: datetime
    category: CategoryResponse = Field(..., description="Product category details")

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    products: list[ProductResponse]
    total: int = Field(..., description="Total number of products")
