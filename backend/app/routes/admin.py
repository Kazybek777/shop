from pathlib import Path
import json
import shutil
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..repositories.product_repository import ProductRepository
from ..repositories.user_repository import UserRepository
from ..routes.auth import require_admin
from ..schemas.admin import MessageResponse, UserRoleUpdateRequest
from ..schemas.auth import UserResponse
from ..schemas.category import CategoryCreate, CategoryResponse
from ..schemas.product import ProductCreate, ProductListResponse, ProductResponse
from ..services.category_service import CategoryService
from ..services.product_service import ProductService

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_admin)])

LOCAL_IMAGE_PREFIX = "/static/images/"
MAX_PRODUCT_IMAGES = 5
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _ensure_images_dir() -> None:
    Path(settings.images_dir).mkdir(parents=True, exist_ok=True)


def _save_uploaded_image(image_file: UploadFile) -> str:
    if not image_file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image filename is missing")

    extension = Path(image_file.filename).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .jpg, .jpeg, .png, .webp, .gif are supported",
        )

    if image_file.content_type and not image_file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file must be an image")

    _ensure_images_dir()
    filename = f"{uuid.uuid4().hex}{extension}"
    destination = Path(settings.images_dir) / filename
    with destination.open("wb") as buffer:
        shutil.copyfileobj(image_file.file, buffer)

    return f"{LOCAL_IMAGE_PREFIX}{filename}"


def _save_uploaded_images(image_files: list[UploadFile] | None) -> list[str]:
    files = [file for file in (image_files or []) if file and file.filename]
    if not files:
        return []

    if len(files) > MAX_PRODUCT_IMAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_PRODUCT_IMAGES} images are allowed for one product",
        )

    image_urls: list[str] = []
    try:
        for image_file in files:
            image_urls.append(_save_uploaded_image(image_file))
        return image_urls
    except Exception:
        _remove_local_images(image_urls)
        raise


def _parse_existing_image_urls(raw_value: str | None, existing_images: list[str]) -> list[str] | None:
    if raw_value in (None, ""):
        return None

    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="existing_image_urls must be valid JSON array") from exc

    if not isinstance(parsed, list):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="existing_image_urls must be a JSON array")

    existing_set = set(existing_images)
    normalized: list[str] = []
    for item in parsed:
        value = str(item or "").strip()
        if not value:
            continue
        if value not in existing_set:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="existing_image_urls contains unknown image")
        if value not in normalized:
            normalized.append(value)

    return normalized


def _is_local_image(image_url: str | None) -> bool:
    return bool(image_url and image_url.startswith(LOCAL_IMAGE_PREFIX))


def _remove_local_image(image_url: str | None) -> None:
    if not _is_local_image(image_url):
        return
    filename = image_url.replace(LOCAL_IMAGE_PREFIX, "", 1)
    path = Path(settings.images_dir) / filename
    if path.exists():
        path.unlink()


def _remove_local_images(image_urls: list[str] | None) -> None:
    for image_url in image_urls or []:
        _remove_local_image(image_url)


@router.get("/users", response_model=List[UserResponse], status_code=status.HTTP_200_OK)
def get_users(db: Session = Depends(get_db)):
    repository = UserRepository(db)
    users = repository.get_all()
    return [UserResponse.model_validate(user) for user in users]


@router.patch("/users/{user_id}/role", response_model=UserResponse, status_code=status.HTTP_200_OK)
def update_user_role(
    user_id: int,
    payload: UserRoleUpdateRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    repository = UserRepository(db)
    user = repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_admin.id and payload.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot remove admin role from your own account",
        )

    updated = repository.update(user, role=payload.role)
    return UserResponse.model_validate(updated)


@router.delete("/users/{user_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin=Depends(require_admin)):
    repository = UserRepository(db)
    user = repository.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own admin account",
        )

    repository.delete(user)
    return MessageResponse(message="User deleted")


@router.get("/categories", response_model=List[CategoryResponse], status_code=status.HTTP_200_OK)
def get_categories(db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.get_all_categories()


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.create_category(payload)


@router.put("/categories/{category_id}", response_model=CategoryResponse, status_code=status.HTTP_200_OK)
def update_category(category_id: int, payload: CategoryCreate, db: Session = Depends(get_db)):
    service = CategoryService(db)
    return service.update_category(category_id, payload)


@router.delete("/categories/{category_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    service = CategoryService(db)
    service.delete_category(category_id)
    return MessageResponse(message="Category deleted")


@router.get("/products", response_model=ProductListResponse, status_code=status.HTTP_200_OK)
def get_products(db: Session = Depends(get_db)):
    service = ProductService(db)
    return service.get_all_products()


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    name: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    description: str | None = Form(default=None),
    image_files: list[UploadFile] | None = File(default=None),
    db: Session = Depends(get_db),
):
    image_urls = _save_uploaded_images(image_files)
    if not image_urls:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please upload at least one product image")

    payload = ProductCreate(
        name=name.strip(),
        description=description.strip() if description else None,
        price=price,
        category_id=category_id,
        image_url=image_urls[0],
    )

    service = ProductService(db)
    try:
        return service.create_product(payload, image_urls=image_urls)
    except Exception:
        _remove_local_images(image_urls)
        raise


@router.put("/products/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(
    product_id: int,
    name: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    description: str | None = Form(default=None),
    image_files: list[UploadFile] | None = File(default=None),
    existing_image_urls: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    repository = ProductRepository(db)
    existing = repository.get_by_id(product_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    existing_images = list(existing.images)
    kept_existing_images = _parse_existing_image_urls(existing_image_urls, existing_images)
    new_image_urls = _save_uploaded_images(image_files)
    combined_images = list(kept_existing_images if kept_existing_images is not None else existing_images)
    replace_images = kept_existing_images is not None

    if new_image_urls:
        combined_images.extend(new_image_urls)
        if len(combined_images) > MAX_PRODUCT_IMAGES:
            _remove_local_images(new_image_urls)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {MAX_PRODUCT_IMAGES} images are allowed for one product",
            )
        replace_images = True
    if replace_images and not combined_images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please keep or upload at least one product image",
        )

    image_url = (combined_images[0] if combined_images else None) or existing.primary_image_url or existing.image_url

    payload = ProductCreate(
        name=name.strip(),
        description=description.strip() if description else None,
        price=price,
        category_id=category_id,
        image_url=image_url,
    )

    service = ProductService(db)
    try:
        updated_product = service.update_product(
            product_id,
            payload,
            image_urls=combined_images if replace_images else None,
            replace_images=replace_images,
        )
    except Exception:
        _remove_local_images(new_image_urls)
        raise

    if replace_images:
        new_images_set = set(combined_images)
        stale_images = [image_url for image_url in existing_images if image_url not in new_images_set]
        _remove_local_images(stale_images)

    return updated_product


@router.delete("/products/{product_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    repository = ProductRepository(db)
    existing = repository.get_by_id(product_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    existing_images = list(existing.images)
    service = ProductService(db)
    service.delete_product(product_id)
    _remove_local_images(existing_images)
    return MessageResponse(message="Product deleted")
