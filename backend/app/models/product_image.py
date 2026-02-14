from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String, nullable=False)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    product = relationship("Product", back_populates="product_images")

    def __repr__(self):
        return f"<ProductImage(id={self.id}, product_id={self.product_id}, sort_order={self.sort_order})>"
