from pydantic import BaseModel, Field
from typing import Optional


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Category name")
    slug: str = Field(..., min_length=3, max_length=50, description="URL-friendly category name")


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int = Field(..., description="Unique category identifier")
    name_ru: Optional[str] = None
    name_en: Optional[str] = None

    class Config:
        from_attributes = True
