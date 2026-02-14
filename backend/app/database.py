from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Ensure all models are imported before metadata creation.
    from .models import Category, Product, ProductImage, User  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _run_sqlite_migrations()


def _run_sqlite_migrations():
    if not settings.database_url.startswith("sqlite"):
        return

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    with engine.begin() as connection:
        _migrate_users_table(connection, inspector, tables)
        _migrate_product_images_table(connection, tables)
        _migrate_translatable_columns(connection, tables)


def _migrate_users_table(connection, inspector, tables):
    if "users" not in tables:
        return

    columns = {column["name"] for column in inspector.get_columns("users")}
    if "role" not in columns:
        connection.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR NOT NULL DEFAULT 'user'"))


def _migrate_product_images_table(connection, tables):
    if "product" not in tables:
        return

    if "product_images" not in tables:
        connection.execute(
            text(
                """
                CREATE TABLE product_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER NOT NULL,
                    image_url VARCHAR NOT NULL,
                    sort_order INTEGER NOT NULL DEFAULT 0,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(product_id) REFERENCES product(id) ON DELETE CASCADE
                )
                """
            )
        )
        connection.execute(text("CREATE INDEX IF NOT EXISTS ix_product_images_product_id ON product_images (product_id)"))

    # Keep existing image_url data compatible by seeding the new table once.
    connection.execute(
        text(
            """
            INSERT INTO product_images (product_id, image_url, sort_order, created_at)
            SELECT p.id, p.image_url, 0, CURRENT_TIMESTAMP
            FROM product p
            LEFT JOIN product_images pi ON pi.product_id = p.id AND pi.sort_order = 0
            WHERE p.image_url IS NOT NULL AND TRIM(p.image_url) != '' AND pi.id IS NULL
            """
        )
    )

    # Keep legacy image_url column synchronized with the first image.
    connection.execute(
        text(
            """
            UPDATE product
            SET image_url = (
                SELECT pi.image_url
                FROM product_images pi
                WHERE pi.product_id = product.id
                ORDER BY pi.sort_order ASC, pi.id ASC
                LIMIT 1
            )
            WHERE image_url IS NULL OR TRIM(image_url) = ''
            """
        )
    )


def _column_exists(table_name: str, column_name: str) -> bool:
    inspector = inspect(engine)
    if table_name not in set(inspector.get_table_names()):
        return False
    columns = {column["name"] for column in inspector.get_columns(table_name)}
    return column_name in columns


def _add_column_if_missing(connection, table_name: str, column_name: str, sql_type: str):
    if _column_exists(table_name, column_name):
        return
    connection.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_type}"))


def _migrate_translatable_columns(connection, tables):
    if "categories" in tables:
        _add_column_if_missing(connection, "categories", "name_ru", "VARCHAR")
        _add_column_if_missing(connection, "categories", "name_en", "VARCHAR")
        connection.execute(text("UPDATE categories SET name_ru = name WHERE name_ru IS NULL OR TRIM(name_ru) = ''"))
        connection.execute(text("UPDATE categories SET name_en = name WHERE name_en IS NULL OR TRIM(name_en) = ''"))

    if "product" in tables:
        _add_column_if_missing(connection, "product", "name_ru", "VARCHAR")
        _add_column_if_missing(connection, "product", "name_en", "VARCHAR")
        _add_column_if_missing(connection, "product", "description_ru", "TEXT")
        _add_column_if_missing(connection, "product", "description_en", "TEXT")

        connection.execute(text("UPDATE product SET name_ru = name WHERE name_ru IS NULL OR TRIM(name_ru) = ''"))
        connection.execute(text("UPDATE product SET name_en = name WHERE name_en IS NULL OR TRIM(name_en) = ''"))
        connection.execute(text("UPDATE product SET description_ru = description WHERE description_ru IS NULL"))
        connection.execute(text("UPDATE product SET description_en = description WHERE description_en IS NULL"))

    _backfill_translations(connection, tables)


def _needs_translation(source_value: str | None, ru_value: str | None, en_value: str | None) -> bool:
    source = (source_value or "").strip()
    if not source:
        return False
    ru = (ru_value or "").strip()
    en = (en_value or "").strip()
    if not ru or not en:
        return True
    return ru == source and en == source


def _backfill_translations(connection, tables):
    from .services.translation_service import TranslationService

    if "categories" in tables:
        categories = connection.execute(text("SELECT id, name, name_ru, name_en FROM categories")).mappings().all()
        for category in categories:
            if not _needs_translation(category["name"], category["name_ru"], category["name_en"]):
                continue
            name_ru, name_en = TranslationService.build_ru_en(category["name"])
            connection.execute(
                text("UPDATE categories SET name_ru = :name_ru, name_en = :name_en WHERE id = :id"),
                {"id": category["id"], "name_ru": name_ru, "name_en": name_en},
            )

    if "product" in tables:
        products = connection.execute(
            text("SELECT id, name, name_ru, name_en, description, description_ru, description_en FROM product")
        ).mappings().all()
        for product in products:
            update_payload: dict[str, str | int | None] = {"id": product["id"]}
            should_update = False

            if _needs_translation(product["name"], product["name_ru"], product["name_en"]):
                name_ru, name_en = TranslationService.build_ru_en(product["name"])
                update_payload["name_ru"] = name_ru
                update_payload["name_en"] = name_en
                should_update = True

            if _needs_translation(product["description"], product["description_ru"], product["description_en"]):
                description_ru, description_en = TranslationService.build_ru_en(product["description"])
                update_payload["description_ru"] = description_ru
                update_payload["description_en"] = description_en
                should_update = True

            if should_update:
                connection.execute(
                    text(
                        """
                        UPDATE product
                        SET name_ru = COALESCE(:name_ru, name_ru),
                            name_en = COALESCE(:name_en, name_en),
                            description_ru = COALESCE(:description_ru, description_ru),
                            description_en = COALESCE(:description_en, description_en)
                        WHERE id = :id
                        """
                    ),
                    {
                        "id": update_payload["id"],
                        "name_ru": update_payload.get("name_ru"),
                        "name_en": update_payload.get("name_en"),
                        "description_ru": update_payload.get("description_ru"),
                        "description_en": update_payload.get("description_en"),
                    },
                )
