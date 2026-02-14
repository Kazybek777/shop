from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import settings
from .database import init_db
from .routes import categories_router, products_router, cart_router, auth_router, admin_router

Path(settings.static_dir).mkdir(parents=True, exist_ok=True)
Path(settings.images_dir).mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

app.include_router(categories_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(auth_router)
app.include_router(admin_router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {
        "message": "Welcome to fastapi shop API",
        "docs": "api/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
