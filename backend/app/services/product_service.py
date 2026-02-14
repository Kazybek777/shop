from sqlalchemy.orm import Session

from ..repositories.product_repository import ProductRepository
from ..repositories.category_repository import CategoryRepository
from ..schemas.product import ProductResponse, ProductListResponse, ProductCreate
from .translation_service import TranslationService
from fastapi import HTTPException, status


class ProductService:
    def __init__(self, db: Session):
        self.product_repository = ProductRepository(db)
        self.category_repository = CategoryRepository(db)

    def get_all_products(self, query: str | None = None) -> ProductListResponse:
        products = self.product_repository.get_all(query=query)
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products_response, total=len(products_response))

    def get_product_by_id(self, product_id: int) -> ProductResponse:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found"
            )
        return ProductResponse.model_validate(product)

    def get_products_by_category(self, category_id: int) -> ProductListResponse:
        category = self.category_repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found"
            )

        products = self.product_repository.get_by_category(category_id)
        products_response = [ProductResponse.model_validate(prod) for prod in products]
        return ProductListResponse(products=products_response, total=len(products_response))

    def create_product(self, product_data: ProductCreate, image_urls: list[str] | None = None) -> ProductResponse:
        category = self.category_repository.get_by_id(product_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {product_data.category_id} does not exist"
            )

        name_ru, name_en = TranslationService.build_ru_en(product_data.name)
        description_ru, description_en = TranslationService.build_ru_en(product_data.description)
        product = self.product_repository.create(
            product_data,
            image_urls=image_urls,
            name_ru=name_ru,
            name_en=name_en,
            description_ru=description_ru,
            description_en=description_en,
        )
        return ProductResponse.model_validate(product)

    def update_product(
        self,
        product_id: int,
        product_data: ProductCreate,
        image_urls: list[str] | None = None,
        replace_images: bool = False,
    ) -> ProductResponse:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found",
            )

        category = self.category_repository.get_by_id(product_data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {product_data.category_id} does not exist",
            )

        name_ru, name_en = TranslationService.build_ru_en(product_data.name)
        description_ru, description_en = TranslationService.build_ru_en(product_data.description)

        updated = self.product_repository.update(
            product,
            image_urls=image_urls,
            replace_images=replace_images,
            name_ru=name_ru,
            name_en=name_en,
            description_ru=description_ru,
            description_en=description_en,
            **product_data.model_dump(),
        )
        return ProductResponse.model_validate(updated)

    def delete_product(self, product_id: int) -> None:
        product = self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with id {product_id} not found",
            )
        self.product_repository.delete(product)
