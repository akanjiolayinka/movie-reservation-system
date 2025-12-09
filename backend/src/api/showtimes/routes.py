"""
Showtime management API routes.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import uuid

from src.config.database import get_db
from src.schemas.showtime import (
    ShowtimeCreateRequest,
    ShowtimeUpdateRequest,
    ShowtimeResponse,
)
from src.services.movie_service import movie_service
from src.middleware.auth import require_admin

router = APIRouter(prefix="/showtimes", tags=["Showtimes"])


@router.post(
    "",
    response_model=ShowtimeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new showtime (Admin only)",
    dependencies=[Depends(require_admin)]
)
def create_showtime(
    showtime_data: ShowtimeCreateRequest,
    db: Session = Depends(get_db)
):
    """Create a new showtime. Requires admin privileges."""
    showtime = movie_service.create_showtime(db, showtime_data.model_dump())
    return ShowtimeResponse.model_validate(showtime)


@router.get(
    "/{showtime_id}",
    response_model=ShowtimeResponse,
    summary="Get showtime details"
)
def get_showtime(
    showtime_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific showtime."""
    showtime = movie_service.get_showtime_by_id(db, showtime_id)
    return ShowtimeResponse.model_validate(showtime)


@router.put(
    "/{showtime_id}",
    response_model=ShowtimeResponse,
    summary="Update a showtime (Admin only)",
    dependencies=[Depends(require_admin)]
)
def update_showtime(
    showtime_id: uuid.UUID,
    update_data: ShowtimeUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update showtime information. Requires admin privileges."""
    showtime = movie_service.update_showtime(
        db,
        showtime_id,
        update_data.model_dump(exclude_unset=True)
    )
    return ShowtimeResponse.model_validate(showtime)


@router.delete(
    "/{showtime_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a showtime (Admin only)",
    dependencies=[Depends(require_admin)]
)
def delete_showtime(
    showtime_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Delete a showtime. Requires admin privileges."""
    movie_service.delete_showtime(db, showtime_id)
