from sqlalchemy.orm import Session
from typing import List
from ..repositories.category_repository import CategoryRepository
from ..repositories.product_repository import ProductRepository
from ..schemas.category import CategoryResponse, CategoryCreate
from .translation_service import TranslationService
from fastapi import HTTPException, status


class CategoryService:
    def __init__(self, db: Session):
        self.repository = CategoryRepository(db)
        self.product_repository = ProductRepository(db)

    def get_all_categories(self) -> List[CategoryResponse]:
        categories = self.repository.get_all()
        return [CategoryResponse.model_validate(cat) for cat in categories]

    def get_category_by_id(self, category_id: int) -> CategoryResponse:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Category with id {category_id} not found'
            )
        return CategoryResponse.model_validate(category)

    def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        if self.repository.get_by_slug(category_data.slug):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with slug '{category_data.slug}' already exists",
            )

        name_ru, name_en = TranslationService.build_ru_en(category_data.name)
        category = self.repository.create(category_data, name_ru=name_ru, name_en=name_en)
        return CategoryResponse.model_validate(category)

    def update_category(self, category_id: int, category_data: CategoryCreate) -> CategoryResponse:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )

        existing_slug = self.repository.get_by_slug(category_data.slug)
        if existing_slug and existing_slug.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with slug '{category_data.slug}' already exists",
            )

        name_ru, name_en = TranslationService.build_ru_en(category_data.name)

        updated = self.repository.update(
            category,
            name=category_data.name,
            slug=category_data.slug,
            name_ru=name_ru,
            name_en=name_en,
        )
        return CategoryResponse.model_validate(updated)

    def delete_category(self, category_id: int) -> None:
        category = self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {category_id} not found",
            )

        products = self.product_repository.get_by_category(category_id)
        if products:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with existing products",
            )

        self.repository.delete(category)
