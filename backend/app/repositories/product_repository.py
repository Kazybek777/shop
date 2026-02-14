from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from ..models.product import Product
from ..models.product_image import ProductImage
from ..schemas.product import ProductCreate


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _normalize_image_urls(image_urls: list[str] | None) -> list[str]:
        normalized: list[str] = []
        for image_url in image_urls or []:
            value = (image_url or "").strip()
            if value:
                normalized.append(value)
        return normalized

    @staticmethod
    def _resolve_primary_image_url(image_urls: list[str], fallback: str | None = None) -> str | None:
        if image_urls:
            return image_urls[0]
        return fallback

    def get_all(self, query: str | None = None) -> List[Product]:
        q = self.db.query(Product).options(joinedload(Product.category), joinedload(Product.product_images))
        if query:
            like_pattern = f"%{query.strip()}%"
            q = q.filter(
                or_(
                    Product.name.ilike(like_pattern),
                    Product.name_ru.ilike(like_pattern),
                    Product.name_en.ilike(like_pattern),
                    Product.description.ilike(like_pattern),
                    Product.description_ru.ilike(like_pattern),
                    Product.description_en.ilike(like_pattern),
                )
            )
        return q.all()

    def get_by_id(self, product_id: int) -> Product:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category), joinedload(Product.product_images))
            .filter(Product.id == product_id)
            .first()
        )

    def get_by_category(self, category_id: int) -> List[Product]:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category), joinedload(Product.product_images))
            .filter(Product.category_id == category_id)
            .all()
        )

    def create(self, product_data: ProductCreate, image_urls: list[str] | None = None, **extra_fields) -> Product:
        normalized_images = self._normalize_image_urls(image_urls)
        payload = product_data.model_dump()
        payload.update(extra_fields)
        payload["image_url"] = self._resolve_primary_image_url(normalized_images, payload.get("image_url"))

        db_product = Product(**payload)
        db_product.product_images = [
            ProductImage(image_url=image_url, sort_order=index)
            for index, image_url in enumerate(normalized_images)
        ]
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def get_multiple_by_ids(self, product_ids: List[int]) -> List[Product]:
        return (
            self.db.query(Product)
            .options(joinedload(Product.category), joinedload(Product.product_images))
            .filter(Product.id.in_(product_ids))
            .all()
        )

    def update(self, product: Product, image_urls: list[str] | None = None, replace_images: bool = False, **kwargs) -> Product:
        for key, value in kwargs.items():
            setattr(product, key, value)

        normalized_images = self._normalize_image_urls(image_urls)
        if replace_images:
            product.product_images = [
                ProductImage(image_url=image_url, sort_order=index)
                for index, image_url in enumerate(normalized_images)
            ]
            product.image_url = self._resolve_primary_image_url(normalized_images, kwargs.get("image_url"))
        elif normalized_images:
            product.image_url = self._resolve_primary_image_url(normalized_images, product.image_url)

        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def delete(self, product: Product) -> None:
        self.db.delete(product)
        self.db.commit()
