"""API package."""
from src.api.auth.routes import router as auth_router
from src.api.movies.routes import router as movies_router
from src.api.showtimes.routes import router as showtimes_router
from src.api.reservations.routes import router as reservations_router
from src.api.admin.routes import router as admin_router

__all__ = [
    "auth_router",
    "movies_router",
    "showtimes_router",
    "reservations_router",
    "admin_router",
]
