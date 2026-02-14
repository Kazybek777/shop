from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..database import Base


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    name_ru = Column(String, nullable=True)
    name_en = Column(String, nullable=True)
    description = Column(Text)
    description_ru = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    product_images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.sort_order",
    )

    @property
    def images(self) -> list[str]:
        if self.product_images:
            return [image.image_url for image in self.product_images if image.image_url]
        if self.image_url:
            return [self.image_url]
        return []

    @property
    def primary_image_url(self) -> str | None:
        images = self.images
        return images[0] if images else None

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"
