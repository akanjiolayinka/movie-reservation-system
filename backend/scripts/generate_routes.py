"""
Script to generate remaining API route files for the movie reservation system.
Run this script to create all missing route files.
"""
import os
from pathlib import Path

# Get backend directory
BACKEND_DIR = Path(__file__).parent.parent

# Movie routes content
MOVIES_ROUTES = '''"""
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
'''

# Showtimes routes
SHOWTIMES_ROUTES = '''"""
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
'''

# Reservations routes
RESERVATIONS_ROUTES = '''"""
Reservation API routes.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import uuid

from src.config.database import get_db
from src.models.user import User
from src.schemas.reservation import (
    SeatAvailabilityResponse,
    LockSeatsRequest,
    LockSeatsResponse,
    CreateReservationRequest,
    ReservationResponse,
    ReservationWithDetailsResponse,
    ReservationListResponse,
    ReservationSeatResponse,
)
from src.schemas.common import MessageResponse
from src.services.reservation_service import reservation_service
from src.middleware.auth import get_current_user

router = APIRouter(tags=["Reservations"])


@router.get(
    "/showtimes/{showtime_id}/seats",
    response_model=SeatAvailabilityResponse,
    summary="Get seat availability for a showtime"
)
def get_seat_availability(
    showtime_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get real-time seat availability for a specific showtime."""
    availability = reservation_service.get_seat_availability(db, showtime_id)
    return availability


@router.post(
    "/showtimes/{showtime_id}/lock-seats",
    response_model=LockSeatsResponse,
    summary="Temporarily lock seats",
    description="Lock seats for 10 minutes to reserve them during booking process"
)
def lock_seats(
    showtime_id: uuid.UUID,
    lock_request: LockSeatsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Temporarily lock seats before creating reservation."""
    lock_info = reservation_service.lock_seats(
        db,
        current_user,
        showtime_id,
        lock_request.seat_ids
    )
    return LockSeatsResponse(**lock_info)


@router.post(
    "/reservations",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a reservation"
)
def create_reservation(
    reservation_data: CreateReservationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new reservation. Seats must be locked first."""
    reservation = reservation_service.create_reservation(
        db,
        current_user,
        reservation_data.showtime_id,
        reservation_data.seat_ids
    )
    
    # Build response with seat details
    seats = []
    for res_seat in reservation.reservation_seats:
        seat = res_seat.seat
        seats.append(ReservationSeatResponse(
            seat_id=seat.id,
            row_label=seat.row_label,
            seat_number=seat.seat_number,
            seat_label=seat.seat_label,
            seat_type=seat.seat_type
        ))
    
    return ReservationResponse(
        id=reservation.id,
        user_id=reservation.user_id,
        showtime_id=reservation.showtime_id,
        status=reservation.status,
        total_price=reservation.total_price,
        seats=seats,
        created_at=reservation.created_at,
        updated_at=reservation.updated_at
    )


@router.get(
    "/reservations",
    response_model=ReservationListResponse,
    summary="Get user's reservations"
)
def get_user_reservations(
    include_past: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reservations for the authenticated user."""
    reservations = reservation_service.get_user_reservations(
        db,
        current_user,
        include_past=include_past
    )
    
    # Build detailed response
    detailed_reservations = []
    for res in reservations:
        seats = [
            ReservationSeatResponse(
                seat_id=rs.seat.id,
                row_label=rs.seat.row_label,
                seat_number=rs.seat.seat_number,
                seat_label=rs.seat.seat_label,
                seat_type=rs.seat.seat_type
            )
            for rs in res.reservation_seats
        ]
        
        detailed_reservations.append(ReservationWithDetailsResponse(
            id=res.id,
            status=res.status,
            total_price=res.total_price,
            seats=seats,
            showtime={"id": res.showtime.id, "start_time": res.showtime.start_time},
            movie={"id": res.showtime.movie.id, "title": res.showtime.movie.title},
            theater={"id": res.showtime.theater.id, "name": res.showtime.theater.name},
            created_at=res.created_at,
            is_cancellable=res.is_cancellable
        ))
    
    return ReservationListResponse(
        reservations=detailed_reservations,
        total=len(reservations)
    )


@router.delete(
    "/reservations/{reservation_id}",
    response_model=MessageResponse,
    summary="Cancel a reservation"
)
def cancel_reservation(
    reservation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a reservation. Only upcoming reservations can be cancelled."""
    reservation_service.cancel_reservation(db, current_user, reservation_id)
    return MessageResponse(message="Reservation cancelled successfully")
'''

# Admin routes
ADMIN_ROUTES = '''"""
Admin API routes for analytics and reporting.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
import uuid

from src.config.database import get_db
from src.schemas.admin import (
    CapacityReportResponse,
    RevenueReportRequest,
    RevenueReportResponse,
    PopularMoviesResponse,
    PromoteUserRequest,
)
from src.schemas.auth import UserResponse
from src.schemas.common import MessageResponse
from src.services.admin_service import admin_service
from src.middleware.auth import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])


@router.get(
    "/reports/capacity",
    response_model=CapacityReportResponse,
    summary="Get capacity utilization report"
)
def get_capacity_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    movie_id: Optional[uuid.UUID] = Query(None),
    theater_id: Optional[uuid.UUID] = Query(None),
    db: Session = Depends(get_db)
):
    """Generate capacity utilization report for showtimes."""
    report = admin_service.get_capacity_report(
        db,
        start_date=start_date,
        end_date=end_date,
        movie_id=movie_id,
        theater_id=theater_id
    )
    return report


@router.get(
    "/reports/revenue",
    response_model=RevenueReportResponse,
    summary="Get revenue report"
)
def get_revenue_report(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    movie_id: Optional[uuid.UUID] = Query(None),
    theater_id: Optional[uuid.UUID] = Query(None),
    group_by: str = Query("day", regex="^(day|week|month|movie|theater)$"),
    db: Session = Depends(get_db)
):
    """Generate revenue report with various grouping options."""
    report = admin_service.get_revenue_report(
        db,
        start_date=start_date,
        end_date=end_date,
        movie_id=movie_id,
        theater_id=theater_id,
        group_by=group_by
    )
    return report


@router.get(
    "/reports/popular-movies",
    response_model=PopularMoviesResponse,
    summary="Get popular movies report"
)
def get_popular_movies(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get most popular movies by reservations and revenue."""
    report = admin_service.get_popular_movies(
        db,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    return report


@router.post(
    "/users/{user_id}/promote",
    response_model=UserResponse,
    summary="Promote or demote user"
)
def promote_user(
    user_id: uuid.UUID,
    promotion_data: PromoteUserRequest,
    db: Session = Depends(get_db)
):
    """Promote user to admin or demote admin to regular user."""
    user = admin_service.promote_user(
        db,
        user_id,
        promotion_data.promote_to_admin
    )
    return UserResponse.model_validate(user)
'''

# API __init__ files
API_INIT = '''"""API package."""
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
'''

# Create files
files_to_create = {
    "src/api/movies/routes.py": MOVIES_ROUTES,
    "src/api/movies/__init__.py": '''"""Movies API package."""\nfrom src.api.movies.routes import router\n__all__ = ["router"]''',
    "src/api/showtimes/routes.py": SHOWTIMES_ROUTES,
    "src/api/showtimes/__init__.py": '''"""Showtimes API package."""\nfrom src.api.showtimes.routes import router\n__all__ = ["router"]''',
    "src/api/reservations/routes.py": RESERVATIONS_ROUTES,
    "src/api/reservations/__init__.py": '''"""Reservations API package."""\nfrom src.api.reservations.routes import router\n__all__ = ["router"]''',
    "src/api/admin/routes.py": ADMIN_ROUTES,
    "src/api/admin/__init__.py": '''"""Admin API package."""\nfrom src.api.admin.routes import router\n__all__ = ["router"]''',
    "src/api/__init__.py": API_INIT,
}

def create_files():
    """Create all route files."""
    for file_path, content in files_to_create.items():
        full_path = BACKEND_DIR / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Created: {file_path}")

if __name__ == "__main__":
    print("Generating API route files...")
    create_files()
    print("\\nAll API route files created successfully!")
