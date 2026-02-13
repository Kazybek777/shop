from pydantic import BaseModel, Field
from typing import Optional

class CartItemBase(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., gt= 0, description="Quantity (must be greater than 0)")


class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(CartItemBase):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0,
                          description="Quantity (must be greater than 0)")

class CartItem(BaseModel):
    product_id: int
    name: str = Field(..., description="Product name")
    price: float = Field(..., description="Product price")
    quantity: int = Field(..., description="Quantity in Cart")
    subtotal: float = Field(...,
                            description="Total price for this item (price + quantity)")
    image_url: Optional[str] = Field(None, description="Product image url")


class CartResponse(BaseModel):
    items: list[CartItemBase] = Field(..., description="List of items in Cart")
    total: float = Field(..., description="Total number of items in Cart")
    items_count: int = Field(..., description="Number of items in Cart")