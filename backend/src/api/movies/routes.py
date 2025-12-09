"""
Movie management API routes.
"""
from fastapi import APIRouter, Depends, Query, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import shutil
from pathlib import Path

from src.config.database import get_db
from src.config.settings import settings
from src.models.user import User
from src.schemas.movie import (
    MovieCreateRequest,
    MovieUpdateRequest,
    MovieResponse,
    MovieListResponse,
)
from src.schemas.showtime import ShowtimeResponse
from src.services.movie_service import movie_service
from src.middleware.auth import require_admin
from src.utils.exceptions import ValidationException

router = APIRouter(prefix="/movies", tags=["Movies"])


@router.post(
    "",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new movie (Admin only)",
    dependencies=[Depends(require_admin)]
)
def create_movie(
    movie_data: MovieCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new movie. Requires admin privileges."""
    movie = movie_service.create_movie(db, movie_data.model_dump())
    return MovieResponse.model_validate(movie)


@router.get(
    "",
    response_model=MovieListResponse,
    summary="List all movies",
    description="Get list of movies with optional filtering by genre"
)
def list_movies(
    genre: Optional[str] = Query(None, description="Filter by genre"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """Get list of movies with pagination."""
    skip = (page - 1) * page_size
    movies, total = movie_service.get_movies(db, genre=genre, skip=skip, limit=page_size)
    
    return MovieListResponse(
        movies=[MovieResponse.model_validate(m) for m in movies],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/{movie_id}",
    response_model=MovieResponse,
    summary="Get movie details"
)
def get_movie(
    movie_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific movie."""
    movie = movie_service.get_movie_by_id(db, movie_id)
    return MovieResponse.model_validate(movie)


@router.put(
    "/{movie_id}",
    response_model=MovieResponse,
    summary="Update a movie (Admin only)",
    dependencies=[Depends(require_admin)]
)
def update_movie(
    movie_id: uuid.UUID,
    update_data: MovieUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update movie information. Requires admin privileges."""
    movie = movie_service.update_movie(
        db,
        movie_id,
        update_data.model_dump(exclude_unset=True)
    )
    return MovieResponse.model_validate(movie)


@router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a movie (Admin only)",
    dependencies=[Depends(require_admin)]
)
def delete_movie(
    movie_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Delete a movie. Requires admin privileges."""
    movie_service.delete_movie(db, movie_id)


@router.get(
    "/{movie_id}/showtimes",
    response_model=list[ShowtimeResponse],
    summary="Get showtimes for a movie"
)
def get_movie_showtimes(
    movie_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get all showtimes for a specific movie."""
    showtimes = movie_service.get_showtimes_for_movie(db, movie_id)
    return [ShowtimeResponse.model_validate(st) for st in showtimes]


@router.post(
    "/{movie_id}/poster",
    summary="Upload movie poster (Admin only)",
    dependencies=[Depends(require_admin)]
)
async def upload_poster(
    movie_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a poster image for a movie. Requires admin privileges."""
    # Verify movie exists
    movie = movie_service.get_movie_by_id(db, movie_id)
    
    # Validate file extension
    ext = Path(file.filename).suffix.lower().lstrip(".")
    if ext not in settings.allowed_extensions_list:
        raise ValidationException(
            message="Invalid file type",
            details={"allowed": settings.allowed_extensions_list}
        )
    
    # Create upload directory if needed
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(exist_ok=True)
    
    # Save file
    filename = f"{movie_id}.{ext}"
    file_path = upload_dir / filename
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update movie poster URL
    poster_url = f"/{settings.UPLOAD_DIR}/{filename}"
    movie_service.update_movie(db, movie_id, {"poster_url": poster_url})
    
    return {"message": "Poster uploaded successfully", "poster_url": poster_url}
