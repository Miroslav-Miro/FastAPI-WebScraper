from ..services.auth_service import router as auth_router
from .book_scraper import router as api_router

__all__ = ["auth_router", "api_router"]
